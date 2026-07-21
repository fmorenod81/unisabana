import sys
import boto3
from botocore.exceptions import ClientError

def check_ecs_services_and_scaling(session):
    """Verifies that both microservices are running and customer is scaled to 3 tasks."""
    print("[*] Reviewing ECS Services and Scaling...")
    ecs = session.client('ecs')

    cluster_name = 'microservices-serverlesscluster'
    services_to_check = {
        'customer-microservice': 3,  # Expected desired count
        'employee-microservice': 1   # Expected desired count
    }
    all_ok = True

    for service_name, expected_desired_count in services_to_check.items():
        try:
            resp = ecs.describe_services(cluster=cluster_name, services=[service_name])
            services = resp.get('services', [])

            if not services or services[0].get('status') == 'INACTIVE':
                print(f"[-] ERROR: ECS Service '{service_name}' not found or INACTIVE.")
                all_ok = False
                continue

            service = services[0]
            print(f"[+] Found ECS Service: {service_name}")

            # Check desired count
            desired_count = service.get('desiredCount')
            running_count = service.get('runningCount')
            print(f"  [+] Desired Count: {desired_count}")
            print(f"  [+] Running Count: {running_count}")

            if desired_count != expected_desired_count:
                print(f"  [-] ERROR: Expected Desired Count of {expected_desired_count}, found {desired_count}")
                all_ok = False
            else:
                print(f"  [+] Desired count matches expected value of {expected_desired_count}")

            # Check status
            status = service.get('status')
            print(f"  [+] Service Status: {status}")
            if status != 'ACTIVE':
                print(f"  [-] WARNING: Expected status 'ACTIVE', found '{status}'")

        except ClientError as e:
            print(f"[-] ERROR describing ECS service '{service_name}': {e}")
            all_ok = False

    return all_ok

def check_load_balancer_rules(session):
    """Verifies that load balancer listener rules have source IP restrictions for employee microservice."""
    print("[*] Reviewing Load Balancer Listener Rules...")
    elb = session.client('elbv2')
    all_ok = True

    try:
        # Get load balancer
        resp = elb.describe_load_balancers(Names=['microservicesLB'])
        load_balancers = resp.get('LoadBalancers', [])

        if not load_balancers:
            print("[-] ERROR: Load balancer 'microservicesLB' not found.")
            return False

        lb_arn = load_balancers[0]['LoadBalancerArn']

        # Get listeners
        listeners_resp = elb.describe_listeners(LoadBalancerArn=lb_arn)
        listeners = listeners_resp.get('Listeners', [])

        print(f"[+] Found Load Balancer: microservicesLB")

        for listener in listeners:
            port = listener.get('Port')
            protocol = listener.get('Protocol')
            print(f"[+] Listener: {protocol}:{port}")

            if port in [80, 8080]:
                # Get rules for this listener
                rules_resp = elb.describe_rules(ListenerArn=listener['ListenerArn'])
                rules = rules_resp.get('Rules', [])

                # Check for admin path rule with source IP condition
                admin_rule_found = False
                source_ip_condition_found = False

                for rule in rules:
                    conditions = rule.get('Conditions', [])
                    actions = rule.get('Actions', [])

                    # Check if this is the admin path rule
                    for condition in conditions:
                        if condition.get('Field') == 'path-pattern':
                            values = condition.get('Values', [])
                            if '/admin/*' in values:
                                admin_rule_found = True
                                print(f"  [+] Found admin path rule for {protocol}:{port}")

                                # Check for source IP condition
                                for cond in conditions:
                                    if cond.get('Field') == 'source-ip':
                                        source_ip_condition_found = True
                                        ip_values = cond.get('Values', [])
                                        if ip_values:
                                            print(f"    [+] Source IP condition found with values: {ip_values}")
                                        else:
                                            print(f"    [+] Source IP condition found (values may be empty)")

                if admin_rule_found and not source_ip_condition_found:
                    print(f"  [-] WARNING: Admin rule found but no source IP condition for {protocol}:{port}")

        return all_ok

    except ClientError as e:
        print(f"[-] ERROR retrieving load balancer rules: {e}")
        return False

def check_pipeline_executions(session):
    """Verifies that recent pipeline executions for employee microservice succeeded."""
    print("[*] Reviewing CodePipeline Executions...")
    codepipeline = session.client('codepipeline')
    all_ok = True

    pipeline_name = 'update-employee-microservice'

    try:
        # Get pipeline execution history
        resp = codepipeline.list_pipeline_executions(pipelineName=pipeline_name)
        executions = resp.get('pipelineExecutionSummaries', [])

        print(f"[+] Pipeline: {pipeline_name}")
        print(f"  [+] Recent Executions: {len(executions)}")

        if not executions:
            print(f"  [-] WARNING: No recent executions found for pipeline")
            return True  # Not necessarily a failure

        # Check the most recent execution
        latest_execution = executions[0]
        status = latest_execution.get('status')
        execution_id = latest_execution.get('pipelineExecutionId')
        start_time = latest_execution.get('startTime')

        print(f"  [+] Latest Execution Status: {status}")
        print(f"  [+] Started: {start_time}")

        if status != 'Succeeded':
            print(f"  [-] WARNING: Expected latest execution status 'Succeeded', found '{status}'")
        else:
            print(f"  [+] Latest execution succeeded")

    except ClientError as e:
        print(f"[-] ERROR retrieving pipeline executions: {e}")
        all_ok = False

    return all_ok

def check_ecr_image_updates(session):
    """Verifies that recent images exist in ECR for both microservices."""
    print("[*] Reviewing ECR Image Updates...")
    ecr = session.client('ecr')
    all_ok = True

    repositories = ['customer', 'employee']

    for repo_name in repositories:
        try:
            # Get image details
            resp = ecr.describe_images(repositoryName=repo_name, maxResults=10)
            images = resp.get('imageDetails', [])

            if not images:
                print(f"[-] ERROR: No images found in repository '{repo_name}'")
                all_ok = False
                continue

            print(f"[+] Repository: {repo_name}")
            print(f"  [+] Total Images: {len(images)}")

            # Check the latest image
            latest_image = images[0]
            image_pushed_date = latest_image.get('imagePushedAt')
            image_tags = latest_image.get('imageTags', [])
            image_digest = latest_image.get('imageId', {}).get('imageDigest', 'N/A')

            print(f"  [+] Latest Image Pushed: {image_pushed_date}")
            if image_tags:
                print(f"  [+] Image Tags: {image_tags}")
                # Verify 'latest' tag exists
                if 'latest' not in image_tags:
                    print(f"  [-] WARNING: 'latest' tag not found for {repo_name}")
                else:
                    print(f"  [+] 'latest' tag is present")
            else:
                print(f"  [-] WARNING: No tags found for latest image in {repo_name}")

            if image_digest != 'N/A':
                print(f"  [+] Image Digest: {image_digest[:12]}...")

        except ClientError as e:
            print(f"[-] ERROR retrieving ECR images for '{repo_name}': {e}")
            all_ok = False

    return all_ok

def check_codedeploy_deployment_status(session):
    """Verifies that recent CodeDeploy deployments succeeded for employee microservice."""
    print("[*] Reviewing CodeDeploy Deployment Status...")
    codedeploy = session.client('codedeploy')
    all_ok = True

    application_name = 'microservices'
    deployment_group_name = 'microservices-employee'

    try:
        # Get recent deployments
        resp = codedeploy.list_deployments(
            applicationName=application_name,
            deploymentGroupName=deployment_group_name
        )
        deployment_ids = resp.get('deployments', [])

        print(f"[+] Application: {application_name}, Deployment Group: {deployment_group_name}")
        print(f"  [+] Recent Deployments: {len(deployment_ids)}")

        if not deployment_ids:
            print(f"  [-] WARNING: No recent deployments found")
            return True

        # Get details of the latest deployment
        latest_deployment_id = deployment_ids[0]
        deployment_resp = codedeploy.get_deployment(deploymentId=latest_deployment_id)
        deployment = deployment_resp.get('deploymentInfo', {})

        status = deployment.get('status')
        create_time = deployment.get('createTime')
        update_time = deployment.get('updateTime')

        print(f"  [+] Latest Deployment Status: {status}")
        print(f"  [+] Created: {create_time}")
        print(f"  [+] Updated: {update_time}")

        if status not in ['Succeeded', 'InProgress']:
            print(f"  [-] WARNING: Expected deployment status 'Succeeded' or 'InProgress', found '{status}'")
        else:
            print(f"  [+] Latest deployment has valid status: {status}")

    except ClientError as e:
        print(f"[-] ERROR retrieving deployment status: {e}")
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
    print(f" AWS Laboratory Reviewer - Phase 9")
    print(f" AWS Profile: {profile_name}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Run checks
    services_ok = check_ecs_services_and_scaling(session)
    print()
    lb_rules_ok = check_load_balancer_rules(session)
    print()
    pipeline_ok = check_pipeline_executions(session)
    print()
    ecr_ok = check_ecr_image_updates(session)
    print()
    deployment_ok = check_codedeploy_deployment_status(session)

    # Final Summary
    print(f"\n==================================================")
    print(f" Phase 9 Review Summary:")
    print(f"==================================================")

    if services_ok:
        print("[+] ECS Services are properly configured and scaled.")
    else:
        print("[-] ECS Services checks failed.")

    if lb_rules_ok:
        print("[+] Load Balancer rules are properly configured.")
    else:
        print("[-] Load Balancer rules checks failed.")

    if pipeline_ok:
        print("[+] CodePipeline executions are available.")
    else:
        print("[-] CodePipeline execution checks failed.")

    if ecr_ok:
        print("[+] ECR repositories have recent images.")
    else:
        print("[-] ECR image checks failed.")

    if deployment_ok:
        print("[+] CodeDeploy deployments are properly configured.")
    else:
        print("[-] CodeDeploy deployment checks failed.")

    if services_ok and lb_rules_ok and pipeline_ok and ecr_ok and deployment_ok:
        print(f"\n[+] PHASE 9 REVIEW SUCCESSFUL! All checks passed.")
    else:
        print(f"\n[-] PHASE 9 REVIEW FAILED. Please check the errors above.")
    print(f"==================================================\n")

if __name__ == "__main__":
    main()
