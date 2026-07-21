import sys
import boto3
from botocore.exceptions import ClientError

def check_ecr(session):
    """Checks if ECR repositories exist and have the latest images."""
    print("[*] Reviewing ECR Repositories...")
    ecr = session.client('ecr')
    repos = ['customer', 'employee']
    all_ok = True
    
    for repo in repos:
        try:
            desc_resp = ecr.describe_repositories(repositoryNames=[repo])
            print(f"[+] Found ECR Repository: {repo}")
            
            # Check if there is an image tagged 'latest'
            try:
                images_resp = ecr.describe_images(
                    repositoryName=repo,
                    imageIds=[{'imageTag': 'latest'}]
                )
                if images_resp.get('imageDetails'):
                    print(f"[+] Verified: Image tagged 'latest' exists in repository '{repo}'.")
                else:
                    print(f"[-] ERROR: Repository '{repo}' exists but has no image tagged 'latest'.")
                    all_ok = False
            except ClientError as e:
                print(f"[-] ERROR checking images in repository '{repo}': {e}")
                all_ok = False
                
        except ecr.exceptions.RepositoryNotFoundException:
            print(f"[-] ERROR: ECR repository '{repo}' was not found.")
            all_ok = False
        except ClientError as e:
            print(f"[-] ERROR checking repository '{repo}': {e}")
            all_ok = False
    return all_ok

def check_ecs_cluster(session):
    """Checks if the ECS cluster exists and is active."""
    print("[*] Reviewing ECS Cluster...")
    ecs = session.client('ecs')
    cluster_name = 'microservices-serverlesscluster'
    
    try:
        resp = ecs.describe_clusters(clusters=[cluster_name])
        clusters = resp.get('clusters', [])
        if not clusters:
            print(f"[-] ERROR: ECS Cluster '{cluster_name}' was not found.")
            return False
            
        cluster = clusters[0]
        status = cluster.get('status')
        print(f"[+] Found ECS Cluster: {cluster_name}")
        print(f"[+] Cluster Status: {status}")
        
        if status == 'ACTIVE':
            return True
        else:
            print(f"[-] ERROR: ECS Cluster is in status '{status}' (should be ACTIVE).")
            return False
    except ClientError as e:
        print(f"[-] ERROR checking ECS cluster: {e}")
        return False

def check_task_definitions(session):
    """Verifies that the task definitions are registered in ECS."""
    print("[*] Reviewing Registered ECS Task Definitions...")
    ecs = session.client('ecs')
    task_defs = ['customer-microservice', 'employee-microservice']
    all_ok = True
    
    for td in task_defs:
        try:
            resp = ecs.describe_task_definition(taskDefinition=td)
            td_details = resp.get('taskDefinition', {})
            family = td_details.get('family')
            revision = td_details.get('revision')
            print(f"[+] Found registered Task Definition family '{family}' (Revision: {revision})")
        except ClientError as e:
            print(f"[-] ERROR: Task definition '{td}' is not registered or cannot be described: {e}")
            all_ok = False
    return all_ok

def check_deployment_assets(session):
    """Checks CodeCommit 'deployment' repository and files."""
    print("[*] Reviewing CodeCommit deployment repository and assets...")
    cc = session.client('codecommit')
    repo_name = 'deployment'
    branch_name = 'dev'
    all_ok = True
    
    try:
        # Verify repository metadata
        cc.get_repository(repositoryName=repo_name)
        print(f"[+] Found CodeCommit Repository: {repo_name}")
        
        # Verify dev branch exists
        try:
            cc.get_branch(repositoryName=repo_name, branchName=branch_name)
            print(f"[+] Found branch '{branch_name}' in repository '{repo_name}'.")
        except ClientError as e:
            print(f"[-] ERROR: Branch '{branch_name}' not found in repository '{repo_name}': {e}")
            return False
            
        # Check files in deployment repo
        required_files = [
            'taskdef-customer.json',
            'taskdef-employee.json',
            'appspec-customer.yaml',
            'appspec-employee.yaml'
        ]
        
        for file in required_files:
            try:
                file_resp = cc.get_file(
                    repositoryName=repo_name,
                    commitSpecifier=branch_name,
                    filePath=file
                )
                print(f"[+] Verified: File '{file}' exists in CodeCommit (dev branch).")
                
                # Check for Task 5.6 placeholder updates in JSON files
                if file.endswith('.json'):
                    content = file_resp.get('fileContent', b'').decode('utf-8')
                    if '"image": "<IMAGE1_NAME>"' in content:
                        print(f"[+] Verified: '{file}' contains the expected '<IMAGE1_NAME>' placeholder.")
                    else:
                        print(f"[-] ERROR: '{file}' does not contain the '<IMAGE1_NAME>' placeholder. Check Task 5.6.")
                        all_ok = False
                        
            except ClientError as e:
                print(f"[-] ERROR: File '{file}' was not found in CodeCommit: {e}")
                all_ok = False
                
    except ClientError as e:
        print(f"[-] ERROR accessing CodeCommit repository '{repo_name}': {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 5")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    ecr_ok = check_ecr(session)
    print()
    cluster_ok = check_ecs_cluster(session)
    print()
    td_ok = check_task_definitions(session)
    print()
    cc_ok = check_deployment_assets(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 5 Review Summary:")
    print(f"==================================================")
    
    if ecr_ok:
        print("[PASS] ECR repositories exist and contain 'latest' images.")
    else:
        print("[FAIL] ECR repositories check failed.")
        
    if cluster_ok:
        print("[PASS] ECS Cluster 'microservices-serverlesscluster' is ACTIVE.")
    else:
        print("[FAIL] ECS Cluster check failed.")
        
    if td_ok:
        print("[PASS] Task definitions are registered with ECS.")
    else:
        print("[FAIL] Task definitions check failed.")
        
    if cc_ok:
        print("[PASS] CodeCommit 'deployment' repository contains the required deployment assets.")
    else:
        print("[FAIL] CodeCommit deployment assets check failed.")

    if ecr_ok and cluster_ok and td_ok and cc_ok:
        print(f"\n[+] PHASE 5 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 5 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
