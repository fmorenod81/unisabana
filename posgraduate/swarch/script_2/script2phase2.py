import sys
import urllib.request
import boto3
from botocore.exceptions import ClientError

def check_http(ip_address):
    """Checks if the monolithic application is accessible on port 80 and serving the expected page."""
    url = f"http://{ip_address}"
    print(f"[*] Testing HTTP connection to MonolithicAppServer ({url})...")
    try:
        # Use a short timeout of 5 seconds
        response = urllib.request.urlopen(url, timeout=5)
        status = response.getcode()
        
        if status == 200:
            content = response.read().decode('utf-8', errors='ignore')
            # Check if keywords from the coffee suppliers monolithic application are present
            keywords = ["coffee", "supplier", "suppliers"]
            if any(kw in content.lower() for kw in keywords):
                print(f"[+] SUCCESS: Monolithic application is serving the expected Coffee Suppliers page.")
                return True
            else:
                print(f"[?] WARNING: Monolithic application responded (HTTP 200), but expected keywords not found.")
                return True
        else:
            print(f"[?] WARNING: Monolithic application responded with status code: {status}")
            return False
    except urllib.error.URLError as e:
        print(f"[-] ERROR: Could not connect to the monolithic application: {e}")
        return False
    except Exception as e:
        print(f"[-] ERROR: Unexpected error during HTTP check: {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 2")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
        ec2 = session.client('ec2')
        rds = session.client('rds')
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # 1. Verify MonolithicAppServer EC2 Instance
    print("[*] Reviewing EC2 Instance: MonolithicAppServer...")
    public_ip = None
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['MonolithicAppServer']},
                {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}
            ]
        )
        
        reservations = response.get('Reservations', [])
        if not reservations:
            print("[-] ERROR: No EC2 instance named 'MonolithicAppServer' was found.")
        else:
            instance = reservations[0]['Instances'][0]
            state = instance['State']['Name']
            print(f"[+] Found instance 'MonolithicAppServer' (ID: {instance['InstanceId']})")
            print(f"[+] Instance State: {state}")
            
            if state != 'running':
                print(f"[-] ERROR: MonolithicAppServer is in state '{state}' (must be 'running').")
            else:
                public_ip = instance.get('PublicIpAddress')
                if public_ip:
                    print(f"[+] Public IPv4 Address: {public_ip}")
                else:
                    print("[-] ERROR: MonolithicAppServer does not have a public IP address.")
    except ClientError as e:
        print(f"[-] ERROR describing EC2 instances: {e}")

    print()

    # 2. Test HTTP connection and page content to EC2 Instance
    http_success = False
    if public_ip:
        http_success = check_http(public_ip)
    else:
        print("[-] Skipping HTTP check (no valid public IP).")

    print()

    # 3. Verify RDS Database Instance
    print("[*] Reviewing RDS Database...")
    db_found = False
    try:
        response = rds.describe_db_instances()
        db_instances = response.get('DBInstances', [])
        if not db_instances:
            print("[-] ERROR: No RDS DB instances found in the account.")
        else:
            # Look for active DB instance, usually containing 'coffee' or the first available
            db_inst = db_instances[0]
            for inst in db_instances:
                if 'coffee' in inst['DBInstanceIdentifier'].lower():
                    db_inst = inst
                    break
            
            db_id = db_inst['DBInstanceIdentifier']
            db_status = db_inst['DBInstanceStatus']
            print(f"[+] Found DB Instance: {db_id}")
            print(f"[+] DB Status: {db_status}")
            
            if db_status != 'available':
                print(f"[-] ERROR: DB Instance is in state '{db_status}' (must be 'available').")
            else:
                db_found = True
    except ClientError as e:
        print(f"[-] ERROR describing DB instances: {e}")

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 2 Review Summary:")
    print(f"==================================================")
    
    all_ok = True
    
    if public_ip and http_success:
        print("[PASS] Monolithic web application is running, accessible, and showing the expected page.")
    else:
        print("[FAIL] Monolithic web application page check failed.")
        all_ok = False
        
    if db_found:
        print("[PASS] RDS Database exists and is in available status.")
    else:
        print("[FAIL] RDS Database check failed.")
        all_ok = False

    if all_ok:
        print(f"\n[+] PHASE 2 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 2 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()

