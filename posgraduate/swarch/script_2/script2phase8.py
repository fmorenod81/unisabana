import sys
import boto3
from botocore.exceptions import ClientError

def check_codedeploy_application(session):
    """Verifies that the CodeDeploy application exists and is configured correctly."""
    print("[*] Reviewing CodeDeploy Application...")
    codedeploy = session.client('codedeploy')

    application_name = 'microservices'
    all_ok = True

    try:
        resp = codedeploy.get_application(applicationName=application_name)
        app = resp.get('application', {})

        print(f"[+] Found CodeDeploy Application: {application_name}")
        print(f"  [+] Application Name: {app.get('applicationName')}")
        print(f"  [+] Compute Platform: {app.get('computePlatform')}")

        if app.get('computePlatform') != 'Server':
            print(f"  [-] WARNING: Expected Compute Platform 'Server', found '{app.get('computePlatform')}'")

    except ClientError as e:
        print(f"[-] ERROR: CodeDeploy application '{application_name}' not found: {e}")
        all_ok = False

    return all_ok

def check_codedeploy_deployment_groups(session):
    """Verifies that CodeDeploy deployment groups for both microservices exist."""
    print("[*] Reviewing CodeDeploy Deployment Groups...")
    codedeploy = session.client('codedeploy')
    ecs = session.client('ecs')

    application_name = 'microservices'
    deployment_groups_to_check = [
        {'name': 'microservices-customer', 'service': 'customer-microservice'},
        {'name': 'microservices-employee', 'service': 'employee-microservice'}
    ]
    cluster_name = 'microservices-serverlesscluster'
    all_ok = True

    try:
        resp = codedeploy.list_deployment_groups(applicationName=application_name)
        deployment_group_names = resp.get('deploymentGroups', [])
    except ClientError as e:
        print(f"[-] ERROR: Failed to list deployment groups: {e}")
        return False

    for dg_info in deployment_groups_to_check:
        dg_name = dg_info['name']
        service_name = dg_info['service']

        if dg_name not in deployment_group_names:
            print(f"[-] ERROR: Deployment group '{dg_name}' not found.")
            all_ok = False
            continue

        try:
            dg_resp = codedeploy.get_deployment_group(
                applicationName=application_name,
                deploymentGroupName=dg_name
            )
            dg = dg_resp.get('deploymentGroupInfo', {})

            print(f"[+] Found Deployment Group: {dg_name}")
            print(f"  [+] Service Role ARN: {dg.get('serviceRoleArn', 'N/A')}")

            # Check deployment config
            dep_config = dg.get('deploymentConfigName')
            print(f"  [+] Deployment Config: {dep_config}")
            if dep_config != 'CodeDeployDefault.ECSAllAtOnce':
                print(f"  [-] WARNING: Expected 'CodeDeployDefault.ECSAllAtOnce', found '{dep_config}'")

            # Check auto rollback configuration
            auto_rollback = dg.get('autoRollbackConfiguration', {})
            print(f"  [+] Auto Rollback Enabled: {auto_rollback.get('enabled', False)}")

            # Check ECS services
            ecs_target = dg.get('ecsServices', [])
            if ecs_target:
                service_info = ecs_target[0]
                cluster = service_info.get('clusterName')
                service = service_info.get('serviceName')
                print(f"  [+] ECS Cluster: {cluster}")
                print(f"  [+] ECS Service: {service}")

                if cluster != cluster_name:
                    print(f"  [-] ERROR: Expected cluster '{cluster_name}', found '{cluster}'")
                    all_ok = False
                if service != service_name:
                    print(f"  [-] ERROR: Expected service '{service_name}', found '{service}'")
                    all_ok = False
            else:
                print("  [-] ERROR: No ECS services configured for this deployment group.")
                all_ok = False

            # Check load balancer info
            lb_info = dg.get('loadBalancerInfo', {})
            tg_group_pair_info = lb_info.get('targetGroupPairInfoList', [])

            if tg_group_pair_info:
                for tg_pair in tg_group_pair_info:
                    prod_tg = tg_pair.get('targetGroups', [{}])[0].get('name', 'N/A')
                    test_tg = tg_pair.get('targetGroups', [{}, {}])[1].get('name', 'N/A') if len(tg_pair.get('targetGroups', [])) > 1 else 'N/A'
                    print(f"  [+] Production Target Group: {prod_tg}")
                    print(f"  [+] Test Target Group: {test_tg}")
            else:
                print("  [-] WARNING: No load balancer configuration found.")

            # Check traffic rerouting
            traffic_reroute = dg.get('deploymentStyle', {}).get('deploymentType')
            print(f"  [+] Deployment Type: {traffic_reroute}")

        except ClientError as e:
            print(f"[-] ERROR describing deployment group '{dg_name}': {e}")
            all_ok = False

    return all_ok

def check_codepipelines(session):
    """Verifies that CodePipelines for both microservices exist and are configured correctly."""
    print("[*] Reviewing CodePipelines...")
    codepipeline = session.client('codepipeline')

    pipelines_to_check = ['update-customer-microservice', 'update-employee-microservice']
    all_ok = True

    for pipeline_name in pipelines_to_check:
        try:
            resp = codepipeline.get_pipeline(name=pipeline_name)
            pipeline = resp.get('pipeline', {})

            print(f"[+] Found Pipeline: {pipeline_name}")
            print(f"  [+] Role ARN: {pipeline.get('roleArn', 'N/A')}")
            print(f"  [+] Artifact Store: {pipeline.get('artifactStore', {}).get('location', 'N/A')}")

            # Check stages
            stages = pipeline.get('stages', [])
            stage_names = [stage.get('name') for stage in stages]
            print(f"  [+] Stages: {', '.join(stage_names)}")

            expected_stages = ['Source', 'Deploy']
            for expected_stage in expected_stages:
                if expected_stage not in stage_names:
                    print(f"  [-] ERROR: Expected stage '{expected_stage}' not found.")
                    all_ok = False

            # Check source stage
            source_stage = next((s for s in stages if s.get('name') == 'Source'), None)
            if source_stage:
                source_action = source_stage.get('actions', [{}])[0]
                provider = source_action.get('actionTypeId', {}).get('provider')
                repo = source_action.get('configuration', {}).get('RepositoryName')
                branch = source_action.get('configuration', {}).get('BranchName')
                print(f"  [+] Source Provider: {provider}")
                print(f"  [+] Source Repository: {repo}")
                print(f"  [+] Source Branch: {branch}")

                if provider != 'CodeCommit':
                    print(f"  [-] ERROR: Expected source provider 'CodeCommit', found '{provider}'")
                    all_ok = False
                if branch != 'dev':
                    print(f"  [-] ERROR: Expected branch 'dev', found '{branch}'")
                    all_ok = False

            # Check deploy stage
            deploy_stage = next((s for s in stages if s.get('name') == 'Deploy'), None)
            if deploy_stage:
                deploy_action = deploy_stage.get('actions', [{}])[0]
                deploy_provider = deploy_action.get('actionTypeId', {}).get('provider')
                print(f"  [+] Deploy Provider: {deploy_provider}")

                if deploy_provider != 'CodeDeployToECS':
                    print(f"  [-] ERROR: Expected deploy provider 'CodeDeployToECS', found '{deploy_provider}'")
                    all_ok = False

        except ClientError as e:
            print(f"[-] ERROR: Pipeline '{pipeline_name}' not found or error retrieving it: {e}")
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
    codedeploy_app_ok = check_codedeploy_application(session)
    print()
    deployment_groups_ok = check_codedeploy_deployment_groups(session)
    print()
    pipelines_ok = check_codepipelines(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 8 Review Summary:")
    print(f"==================================================")

    if codedeploy_app_ok:
        print("[+] CodeDeploy application is properly configured.")
    else:
        print("[-] CodeDeploy application checks failed.")

    if deployment_groups_ok:
        print("[+] CodeDeploy deployment groups are properly configured.")
    else:
        print("[-] CodeDeploy deployment groups checks failed.")

    if pipelines_ok:
        print("[+] CodePipelines are properly configured.")
    else:
        print("[-] CodePipelines checks failed.")

    if codedeploy_app_ok and deployment_groups_ok and pipelines_ok:
        print(f"\n[+] PHASE 8 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 8 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
