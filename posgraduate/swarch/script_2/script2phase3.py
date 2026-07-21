import sys
import boto3
from botocore.exceptions import ClientError

def check_cloud9(session):
    """Checks if the Cloud9 IDE 'MicroservicesIDE' exists and its instance configuration."""
    print("[*] Reviewing Cloud9 Environment: MicroservicesIDE...")
    c9 = session.client('cloud9')
    ec2 = session.client('ec2')
    
    try:
        # Get list of environment IDs
        env_ids = c9.list_environments().get('environmentIds', [])
        if not env_ids:
            print("[-] ERROR: No Cloud9 environments found.")
            return False

        # Describe environments to find the one named 'MicroservicesIDE'
        response = c9.describe_environments(environmentIds=env_ids)
        target_env = None
        for env in response.get('environments', []):
            if env.get('name') == 'MicroservicesIDE':
                target_env = env
                break
        
        if not target_env:
            print("[-] ERROR: Cloud9 environment named 'MicroservicesIDE' was not found.")
            return False

        env_id = target_env['id']
        print(f"[+] Found Cloud9 Environment 'MicroservicesIDE' (ID: {env_id})")
        print(f"[+] Description: {target_env.get('description', 'No description')}")
        print(f"[+] Type: {target_env.get('type')}")

        # Find the EC2 instance associated with this Cloud9 environment
        instances_response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:aws:cloud9:environment', 'Values': [env_id]},
                {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
            ]
        )
        
        reservations = instances_response.get('Reservations', [])
        if not reservations:
            # Fallback filter by name prefix
            instances_response = ec2.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [f'*aws-cloud9-MicroservicesIDE*']},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
                ]
            )
            reservations = instances_response.get('Reservations', [])

        if not reservations:
            print("[-] ERROR: No EC2 instance associated with the Cloud9 environment was found.")
            return False
            
        instance = reservations[0]['Instances'][0]
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        state = instance['State']['Name']
        print(f"[+] Associated EC2 Instance: {instance_id}")
        print(f"[+] Instance State: {state}")
        print(f"[+] Instance Type: {instance_type}")
        
        # Verify instance type is t3.small
        if instance_type == 't3.small':
            print("[+] Instance type is correct (t3.small).")
            return True
        else:
            print(f"[-] ERROR: Expected instance type 't3.small', but found '{instance_type}'.")
            return False

    except ClientError as e:
        print(f"[-] ERROR checking Cloud9/EC2: {e}")
        return False

def check_codecommit(session):
    """Checks if the CodeCommit repository 'microservices' exists and has dev branch."""
    print("[*] Reviewing CodeCommit Repository: microservices...")
    cc = session.client('codecommit')
    
    try:
        # Get repository details
        repo_response = cc.get_repository(repositoryName='microservices')
        repo_metadata = repo_response.get('repositoryMetadata', {})
        print(f"[+] Found CodeCommit Repository: {repo_metadata.get('repositoryName')}")
        print(f"[+] Clone URL (HTTP): {repo_metadata.get('cloneUrlHttp')}")
        
        # Check for 'dev' branch
        try:
            branch_response = cc.get_branch(
                repositoryName='microservices',
                branchName='dev'
            )
            branch_info = branch_response.get('branchInfo', {})
            commit_id = branch_info.get('commitId')
            print(f"[+] Found branch 'dev' pointing to commit: {commit_id}")
            return True
        except cc.exceptions.BranchDoesNotExistException:
            print("[-] ERROR: Branch 'dev' does not exist in the 'microservices' repository.")
            return False
            
    except cc.exceptions.RepositoryDoesNotExistException:
        print("[-] ERROR: CodeCommit repository named 'microservices' does not exist.")
        return False
    except ClientError as e:
        print(f"[-] ERROR checking CodeCommit: {e}")
        return False

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
    print(f" AWS Laboratory Reviewer - Phase 3")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    c9_ok = check_cloud9(session)
    print()
    cc_ok = check_codecommit(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 3 Review Summary:")
    print(f"==================================================")
    
    if c9_ok:
        print("[PASS] Cloud9 environment 'MicroservicesIDE' exists on t3.small instance.")
    else:
        print("[FAIL] Cloud9 environment check failed.")
        
    if cc_ok:
        print("[PASS] CodeCommit repository 'microservices' has been created and has a 'dev' branch.")
    else:
        print("[FAIL] CodeCommit repository check failed.")

    if c9_ok and cc_ok:
        print(f"\n[+] PHASE 3 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 3 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
