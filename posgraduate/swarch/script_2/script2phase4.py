import sys
import boto3
from botocore.exceptions import ClientError

def check_security_group_rules(session, instance_id):
    """Checks if ports 8080 and 8081 are open in the Cloud9 instance's security groups."""
    print("[*] Reviewing Cloud9 Security Group rules...")
    ec2 = session.client('ec2')
    
    try:
        # Get instance details to find security groups
        instances_resp = ec2.describe_instances(InstanceIds=[instance_id])
        instance = instances_resp['Reservations'][0]['Instances'][0]
        security_groups = instance.get('SecurityGroups', [])
        
        if not security_groups:
            print("[-] ERROR: No security groups associated with the Cloud9 instance.")
            return False
            
        sg_ids = [sg['GroupId'] for sg in security_groups]
        print(f"[+] Found associated Security Group(s): {', '.join(sg_ids)}")
        
        # Describe security group rules
        rules_resp = ec2.describe_security_groups(GroupIds=sg_ids)
        
        port_8080_open = False
        port_8081_open = False
        
        for sg in rules_resp.get('SecurityGroups', []):
            for permission in sg.get('IpPermissions', []):
                from_port = permission.get('FromPort')
                to_port = permission.get('ToPort')
                protocol = permission.get('IpProtocol')
                
                # Check TCP protocol rules
                if protocol == 'tcp' or protocol == '-1':
                    # Check if port ranges cover 8080 and 8081
                    # Note: protocol == '-1' means all protocols/ports
                    if protocol == '-1':
                        port_8080_open = True
                        port_8081_open = True
                    else:
                        if from_port <= 8080 <= to_port:
                            port_8080_open = True
                        if from_port <= 8081 <= to_port:
                            port_8081_open = True
                            
        if port_8080_open:
            print("[+] Verified: Port 8080 is open/allowed.")
        else:
            print("[-] ERROR: Port 8080 is NOT allowed in the security groups.")
            
        if port_8081_open:
            print("[+] Verified: Port 8081 is open/allowed.")
        else:
            print("[-] ERROR: Port 8081 is NOT allowed in the security groups.")
            
        return port_8080_open and port_8081_open
        
    except ClientError as e:
        print(f"[-] ERROR checking security group rules: {e}")
        return False

def check_cloud9_instance(session):
    """Retrieves the Cloud9 instance ID."""
    c9 = session.client('cloud9')
    ec2 = session.client('ec2')
    
    try:
        env_ids = c9.list_environments().get('environmentIds', [])
        if not env_ids:
            return None
            
        response = c9.describe_environments(environmentIds=env_ids)
        env_id = None
        for env in response.get('environments', []):
            if env.get('name') == 'MicroservicesIDE':
                env_id = env['id']
                break
                
        if not env_id:
            return None
            
        instances_response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:aws:cloud9:environment', 'Values': [env_id]},
                {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
            ]
        )
        
        reservations = instances_response.get('Reservations', [])
        if not reservations:
            # Name-based fallback
            instances_response = ec2.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [f'*aws-cloud9-MicroservicesIDE*']},
                    {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
                ]
            )
            reservations = instances_response.get('Reservations', [])
            
        if reservations:
            return reservations[0]['Instances'][0]['InstanceId']
            
    except ClientError:
        pass
    return None

def check_codecommit_assets(session):
    """Checks CodeCommit to verify Dockerfiles exist and employee microservice port is adjusted to 8080."""
    print("[*] Reviewing CodeCommit repository structure for Phase 4...")
    cc = session.client('codecommit')
    repo_name = 'microservices'
    branch_name = 'dev'
    
    try:
        # Check customer/Dockerfile existence
        try:
            cc.get_file(
                repositoryName=repo_name,
                commitSpecifier=branch_name,
                filePath='customer/Dockerfile'
            )
            print("[+] Verified: 'customer/Dockerfile' exists in CodeCommit (dev branch).")
            customer_ok = True
        except ClientError as e:
            print(f"[-] ERROR: 'customer/Dockerfile' not found in CodeCommit: {e}")
            customer_ok = False
            
        # Check employee/Dockerfile and port settings
        employee_ok = False
        try:
            file_resp = cc.get_file(
                repositoryName=repo_name,
                commitSpecifier=branch_name,
                filePath='employee/Dockerfile'
            )
            print("[+] Verified: 'employee/Dockerfile' exists in CodeCommit (dev branch).")
            
            # Read file content to check for EXPOSE 8080
            file_content = file_resp.get('fileContent', b'').decode('utf-8')
            if 'EXPOSE 8080' in file_content:
                print("[+] Verified: 'employee/Dockerfile' exposes port 8080 (Task 4.6 adjustment).")
                employee_ok = True
            else:
                print("[-] ERROR: 'employee/Dockerfile' does not expose port 8080. Check Task 4.6.")
                
        except ClientError as e:
            print(f"[-] ERROR: 'employee/Dockerfile' not found in CodeCommit: {e}")
            
        return customer_ok and employee_ok
        
    except ClientError as e:
        print(f"[-] ERROR accessing CodeCommit: {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 4")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # 1. Check Security Group Rules
    sg_ok = False
    instance_id = check_cloud9_instance(session)
    if instance_id:
        sg_ok = check_security_group_rules(session, instance_id)
    else:
        print("[-] ERROR: Could not locate EC2 instance associated with 'MicroservicesIDE'.")
        
    print()
    
    # 2. Check CodeCommit Assets (Dockerfiles and Ports)
    cc_ok = check_codecommit_assets(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 4 Review Summary:")
    print(f"==================================================")
    
    if sg_ok:
        print("[PASS] Cloud9 Security Group allows inbound ports 8080 and 8081.")
    else:
        print("[FAIL] Cloud9 Security Group configuration incorrect.")
        
    if cc_ok:
        print("[PASS] Microservices structure and Dockerfiles pushed to CodeCommit with correct ports.")
    else:
        print("[FAIL] CodeCommit repository checks failed.")

    if sg_ok and cc_ok:
        print(f"\n[+] PHASE 4 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 4 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
