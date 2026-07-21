import sys
import boto3
from botocore.exceptions import ClientError

def check_target_groups(session):
    """Verifies that the 4 target groups exist and have correct configuration."""
    print("[*] Reviewing Target Groups...")
    elbv2 = session.client('elbv2')
    
    tgs_to_check = {
        'customer-tg-one': {'port': 8080, 'path': '/'},
        'customer-tg-two': {'port': 8080, 'path': '/'},
        'employee-tg-one': {'port': 8080, 'path': '/admin/suppliers'},
        'employee-tg-two': {'port': 8080, 'path': '/admin/suppliers'}
    }
    
    all_ok = True
    try:
        # Get all target groups
        paginator = elbv2.get_paginator('describe_target_groups')
        existing_tgs = {}
        for page in paginator.paginate():
            for tg in page.get('TargetGroups', []):
                existing_tgs[tg['TargetGroupName']] = tg
                
        for name, expected in tgs_to_check.items():
            if name not in existing_tgs:
                print(f"[-] ERROR: Target Group '{name}' was not found.")
                all_ok = False
                continue
                
            tg = existing_tgs[name]
            port = tg.get('Port')
            protocol = tg.get('Protocol')
            health_path = tg.get('HealthCheckPath')
            
            print(f"[+] Found Target Group: {name}")
            
            # Verify port, protocol and health check path
            if port == expected['port'] and protocol == 'HTTP':
                print(f"  [+] Port & Protocol: HTTP {port}")
            else:
                print(f"  [-] ERROR: Expected HTTP {expected['port']}, found {protocol} {port}")
                all_ok = False
                
            if health_path == expected['path']:
                print(f"  [+] Health Check Path: {health_path}")
            else:
                print(f"  [-] ERROR: Expected Health Check Path '{expected['path']}', found '{health_path}'")
                all_ok = False
                
    except ClientError as e:
        print(f"[-] ERROR describing target groups: {e}")
        all_ok = False
        
    return all_ok

def check_security_group(session):
    """Checks the 'microservices-sg' security group and its rules."""
    print("[*] Reviewing Security Group: microservices-sg...")
    ec2 = session.client('ec2')
    
    try:
        resp = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['microservices-sg']}]
        )
        sgs = resp.get('SecurityGroups', [])
        if not sgs:
            print("[-] ERROR: Security group 'microservices-sg' was not found.")
            return False
            
        sg = sgs[0]
        sg_id = sg['GroupId']
        print(f"[+] Found Security Group '{sg['GroupName']}' (ID: {sg_id})")
        
        # Verify ports 80 and 8080 are open
        port_80_open = False
        port_8080_open = False
        
        for permission in sg.get('IpPermissions', []):
            protocol = permission.get('IpProtocol')
            from_port = permission.get('FromPort')
            to_port = permission.get('ToPort')
            
            if protocol == 'tcp' or protocol == '-1':
                if protocol == '-1':
                    port_80_open = True
                    port_8080_open = True
                else:
                    if from_port <= 80 <= to_port:
                        port_80_open = True
                    if from_port <= 8080 <= to_port:
                        port_8080_open = True
                        
        if port_80_open:
            print("[+] Verified: Inbound rule for HTTP port 80 exists.")
        else:
            print("[-] ERROR: Inbound rule for port 80 is missing.")
            
        if port_8080_open:
            print("[+] Verified: Inbound rule for port 8080 exists.")
        else:
            print("[-] ERROR: Inbound rule for port 8080 is missing.")
            
        return port_80_open and port_8080_open
    except ClientError as e:
        print(f"[-] ERROR describing security groups: {e}")
        return False

def check_alb(session):
    """Checks ALB existence and its listeners/routing rules."""
    print("[*] Reviewing Application Load Balancer: microservicesLB...")
    elbv2 = session.client('elbv2')
    alb_arn = None
    
    try:
        # Check ALB
        resp = elbv2.describe_load_balancers(Names=['microservicesLB'])
        lbs = resp.get('LoadBalancers', [])
        if not lbs:
            print("[-] ERROR: ALB 'microservicesLB' was not found.")
            return False
            
        alb = lbs[0]
        alb_arn = alb['LoadBalancerArn']
        print(f"[+] Found ALB: {alb['LoadBalancerName']}")
        print(f"[+] Scheme: {alb['Scheme']} (should be internet-facing)")
        print(f"[+] DNS Name: {alb['DNSName']}")
        
        # Check listeners
        listeners_resp = elbv2.describe_listeners(LoadBalancerArn=alb_arn)
        listeners = listeners_resp.get('Listeners', [])
        
        port_80_listener = None
        port_8080_listener = None
        
        for l in listeners:
            port = l.get('Port')
            if port == 80:
                port_80_listener = l
            elif port == 8080:
                port_8080_listener = l
                
        listeners_ok = True
        
        # Check Port 80
        if port_80_listener:
            print("[+] Found Listener on port 80.")
            l_arn = port_80_listener['ListenerArn']
            rules_resp = elbv2.describe_rules(ListenerArn=l_arn)
            rules = rules_resp.get('Rules', [])
            
            # Look for path-pattern rule '/admin/*'
            has_admin_rule = False
            for rule in rules:
                for cond in rule.get('Conditions', []):
                    if cond.get('Field') == 'path-pattern' and '/admin/*' in cond.get('Values', []):
                        has_admin_rule = True
                        # Verify it forwards to employee target group (contains employee-tg)
                        actions = rule.get('Actions', [])
                        if actions and 'employee-tg' in actions[0].get('TargetGroupArn', ''):
                            print("  [+] Rule '/admin/*' correctly forwards to an employee target group.")
                        else:
                            print("  [-] ERROR: Rule '/admin/*' does not forward to employee target group.")
                            listeners_ok = False
            if not has_admin_rule:
                print("  [-] ERROR: Path-based rule for '/admin/*' is missing on port 80.")
                listeners_ok = False
        else:
            print("[-] ERROR: Listener on port 80 was not found.")
            listeners_ok = False
            
        # Check Port 8080
        if port_8080_listener:
            print("[+] Found Listener on port 8080.")
            l_arn = port_8080_listener['ListenerArn']
            rules_resp = elbv2.describe_rules(ListenerArn=l_arn)
            rules = rules_resp.get('Rules', [])
            
            # Look for path-pattern rule '/admin/*'
            has_admin_rule = False
            for rule in rules:
                for cond in rule.get('Conditions', []):
                    if cond.get('Field') == 'path-pattern' and '/admin/*' in cond.get('Values', []):
                        has_admin_rule = True
                        # Verify it forwards to employee target group (contains employee-tg)
                        actions = rule.get('Actions', [])
                        if actions and 'employee-tg' in actions[0].get('TargetGroupArn', ''):
                            print("  [+] Rule '/admin/*' correctly forwards to an employee target group.")
                        else:
                            print("  [-] ERROR: Rule '/admin/*' does not forward to employee target group.")
                            listeners_ok = False
            if not has_admin_rule:
                print("  [-] ERROR: Path-based rule for '/admin/*' is missing on port 8080.")
                listeners_ok = False
        else:
            print("[-] ERROR: Listener on port 8080 was not found.")
            listeners_ok = False
            
        return listeners_ok
        
    except ClientError as e:
        print(f"[-] ERROR checking Load Balancer: {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 6")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    tgs_ok = check_target_groups(session)
    print()
    sg_ok = check_security_group(session)
    print()
    alb_ok = check_alb(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 6 Review Summary:")
    print(f"==================================================")
    
    if tgs_ok:
        print("[PASS] Target Groups configured correctly.")
    else:
        print("[FAIL] Target Groups check failed.")
        
    if sg_ok:
        print("[PASS] Security Group 'microservices-sg' permits ports 80 and 8080.")
    else:
        print("[FAIL] Security Group check failed.")
        
    if alb_ok:
        print("[PASS] Load Balancer 'microservicesLB' listeners and routing rules configured correctly.")
    else:
        print("[FAIL] Load Balancer check failed.")

    if tgs_ok and sg_ok and alb_ok:
        print(f"\n[+] PHASE 6 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 6 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
