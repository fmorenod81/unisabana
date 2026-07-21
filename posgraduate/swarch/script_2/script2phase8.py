import sys
import boto3
from botocore.exceptions import ClientError

def check_codedeploy(session):
    """Verifies CodeDeploy application and deployment groups."""
    print("[*] Reviewing CodeDeploy Configuration...")
    cd = session.client('codedeploy')
    app_name = 'microservices'
    deployment_groups = ['microservices-customer', 'microservices-employee']
    all_ok = True
    
    try:
        # Check Application
        app_resp = cd.get_application(applicationName=app_name)
        print(f"[+] Found CodeDeploy Application: {app_resp['applicationInfo']['applicationName']}")
        
        # Check Deployment Groups
        for dg_name in deployment_groups:
            try:
                dg_resp = cd.get_deployment_group(
                    applicationName=app_name,
                    deploymentGroupName=dg_name
                )
                dg_info = dg_resp['deploymentGroupInfo']
                print(f"[+] Found Deployment Group: {dg_name}")
                
                # Check target ECS service & cluster
                ecs_services = dg_info.get('ecsServices', [])
                if ecs_services:
                    service = ecs_services[0]
                    print(f"  [+] ECS Cluster: {service.get('clusterName')}")
                    print(f"  [+] ECS Service: {service.get('serviceName')}")
                else:
                    print("  [-] ERROR: No associated ECS services found.")
                    all_ok = False
                    
                # Check load balancer info
                lb_info = dg_info.get('loadBalancerInfo', {}).get('elbInfoList', [])
                target_groups = dg_info.get('loadBalancerInfo', {}).get('targetGroupInfoList', [])
                print(f"  [+] Target Groups attached: {', '.join([tg['name'] for tg in target_groups])}")
                
                # Check deployment config
                dep_config = dg_info.get('deploymentConfigName')
                print(f"  [+] Deployment Config: {dep_config}")
                if dep_config != 'CodeDeployDefault.ECSAllAtOnce':
                    print(f"  [-] WARNING: Deployment config is '{dep_config}' (expected CodeDeployDefault.ECSAllAtOnce)")
                    
            except ClientError as e:
                print(f"[-] ERROR: Deployment Group '{dg_name}' not found or error occurred: {e}")
                all_ok = False
                
    except ClientError as e:
        print(f"[-] ERROR: CodeDeploy application '{app_name}' not found: {e}")
        all_ok = False
        
    return all_ok

def check_codepipelines(session):
    """Verifies update-customer-microservice and update-employee-microservice pipelines."""
    print("[*] Reviewing CodePipeline Configurations...")
    cp = session.client('codepipeline')
    pipelines = {
        'update-customer-microservice': {
            'ecr_repo': 'customer',
            'dg': 'microservices-customer'
        },
        'update-employee-microservice': {
            'ecr_repo': 'employee',
            'dg': 'microservices-employee'
        }
    }
    
    all_ok = True
    
    for pipe_name, expected in pipelines.items():
        try:
            resp = cp.get_pipeline(name=pipe_name)
            pipeline = resp.get('pipeline', {})
            print(f"[+] Found CodePipeline: {pipe_name}")
            
            # Check Stages
            stages = pipeline.get('stages', [])
            
            # 1. Check Source Stage (should have 2 actions: CodeCommit and ECR)
            source_stage = stages[0] if stages else {}
            actions = source_stage.get('actions', [])
            has_codecommit = False
            has_ecr = False
            
            for action in actions:
                provider = action.get('actionTypeId', {}).get('provider')
                if provider == 'CodeCommit':
                    has_codecommit = True
                    repo = action.get('configuration', {}).get('RepositoryName')
                    branch = action.get('configuration', {}).get('BranchName')
                    print(f"  [+] Source: CodeCommit repository '{repo}' (branch '{branch}')")
                elif provider == 'ECR':
                    has_ecr = True
                    repo = action.get('configuration', {}).get('RepositoryName')
                    tag = action.get('configuration', {}).get('ImageTag')
                    print(f"  [+] Source: ECR repository '{repo}' (tag '{tag}')")
                    if repo != expected['ecr_repo']:
                        print(f"  [-] ERROR: Expected ECR Repository '{expected['ecr_repo']}', found '{repo}'")
                        all_ok = False
            
            if not has_codecommit or not has_ecr:
                print("  [-] ERROR: Source stage must contain both CodeCommit and ECR sources.")
                all_ok = False
                
            # 2. Check Deploy Stage (CodeDeployToECS action)
            deploy_stage = stages[-1] if len(stages) > 1 else {}
            deploy_actions = deploy_stage.get('actions', [])
            deploy_ok = False
            
            for action in deploy_actions:
                provider = action.get('actionTypeId', {}).get('provider')
                if provider == 'CodeDeployToECS':
                    deploy_ok = True
                    app = action.get('configuration', {}).get('ApplicationName')
                    dg = action.get('configuration', {}).get('DeploymentGroupName')
                    print(f"  [+] Deploy Action: CodeDeployToECS (App: '{app}', Deployment Group: '{dg}')")
                    if dg != expected['dg']:
                        print(f"  [-] ERROR: Expected Deploy to DG '{expected['dg']}', found '{dg}'")
                        all_ok = False
                        
            if not deploy_ok:
                print("  [-] ERROR: Deploy stage must have a CodeDeployToECS action.")
                all_ok = False
                
        except ClientError as e:
            print(f"[-] ERROR: Pipeline '{pipe_name}' not found: {e}")
            all_ok = False
            
    return all_ok

def main():
    # Get profile name from arguments or input
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("Enter AWS Profile Name (e.g., LabMicroservices): ").strip()
    
    if not profile_name:
        print("[-] ERROR: Profile name cannot be empty.")
        sys.exit(1)

    print(f"\n==================================================")
    print(f" AWS Laboratory Reviewer - Phase 8")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    cd_ok = check_codedeploy(session)
    print()
    cp_ok = check_codepipelines(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 8 Review Summary:")
    print(f"==================================================")
    
    if cd_ok:
        print("[PASS] CodeDeploy application and deployment groups are correctly configured.")
    else:
        print("[FAIL] CodeDeploy checks failed.")
        
    if cp_ok:
        print("[PASS] CodePipelines for customer and employee microservices are correctly configured.")
    else:
        print("[FAIL] CodePipeline checks failed.")

    if cd_ok and cp_ok:
        print(f"\n[+] PHASE 8 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 8 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
