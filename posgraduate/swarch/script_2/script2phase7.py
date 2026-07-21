import sys
import boto3
from botocore.exceptions import ClientError

def check_ecs_services(session):
    """Verifies that the customer and employee ECS services exist and are configured correctly."""
    print("[*] Reviewing ECS Services in cluster 'microservices-serverlesscluster'...")
    ecs = session.client('ecs')
    ec2 = session.client('ec2')
    
    cluster_name = 'microservices-serverlesscluster'
    services_to_check = ['customer-microservice', 'employee-microservice']
    all_ok = True
    
    # Get security group ID for microservices-sg
    sg_id = None
    try:
        sg_resp = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['microservices-sg']}]
        )
        if sg_resp.get('SecurityGroups'):
            sg_id = sg_resp['SecurityGroups'][0]['GroupId']
    except ClientError:
        pass

    for service_name in services_to_check:
        try:
            resp = ecs.describe_services(cluster=cluster_name, services=[service_name])
            services = resp.get('services', [])
            
            if not services or services[0].get('status') == 'INACTIVE':
                print(f"[-] ERROR: ECS Service '{service_name}' was not found or is INACTIVE.")
                all_ok = False
                continue
                
            service = services[0]
            print(f"[+] Found ECS Service: {service_name}")
            
            # Check desired count
            desired_count = service.get('desiredCount')
            print(f"  [+] Desired Count: {desired_count}")
            if desired_count != 1:
                print(f"  [-] WARNING: Expected Desired Count of 1, found {desired_count}")
                
            # Check launch type
            launch_type = service.get('launchType')
            print(f"  [+] Launch Type: {launch_type}")
            if launch_type != 'FARGATE':
                print(f"  [-] ERROR: Expected Launch Type 'FARGATE', found '{launch_type}'")
                all_ok = False
                
            # Check deployment controller
            dep_controller = service.get('deploymentController', {}).get('type')
            print(f"  [+] Deployment Controller Type: {dep_controller}")
            if dep_controller != 'CODE_DEPLOY':
                print(f"  [-] ERROR: Expected Deployment Controller 'CODE_DEPLOY', found '{dep_controller}'")
                all_ok = False
                
            # Check load balancer association
            lb_mappings = service.get('loadBalancers', [])
            if lb_mappings:
                tg_arn = lb_mappings[0].get('targetGroupArn', '')
                container_name = lb_mappings[0].get('containerName')
                container_port = lb_mappings[0].get('containerPort')
                
                print(f"  [+] LB Target Group ARN: {tg_arn.split('/')[-1]}")
                print(f"  [+] Container: {container_name} on port {container_port}")
                
                # Check target group matches service
                expected_tg = 'customer-tg-two' if 'customer' in service_name else 'employee-tg-two'
                if expected_tg not in tg_arn:
                    print(f"  [?] Note: Currently attached to target group '{tg_arn.split('/')[-1]}' (expected initial: {expected_tg}). This could be modified by deployment updates.")
            else:
                print("  [-] ERROR: No Load Balancer mapping found for this service.")
                all_ok = False
                
            # Check security groups in network configuration
            net_cfg = service.get('networkConfiguration', {}).get('awsvpcConfiguration', {})
            sgs = net_cfg.get('securityGroups', [])
            if sg_id and sg_id in sgs:
                print("  [+] Network: Service is associated with 'microservices-sg'.")
            else:
                print(f"  [-] ERROR: Service is NOT associated with 'microservices-sg' (SGs: {sgs}).")
                all_ok = False
                
        except ClientError as e:
            print(f"[-] ERROR describing ECS service '{service_name}': {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 7")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    services_ok = check_ecs_services(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 7 Review Summary:")
    print(f"==================================================")
    
    if services_ok:
        print("[PASS] ECS Services are active and correctly configured on Fargate with CodeDeploy controller.")
    else:
        print("[FAIL] ECS Services checks failed.")

    if services_ok:
        print(f"\n[+] PHASE 7 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 7 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
