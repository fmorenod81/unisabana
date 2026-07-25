import sys
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_cloud9_instance_info(session):
    """Retrieves the public IP of the Cloud9 instance."""
    print("[*] Retrieving Cloud9 Instance Public IP...")
    ec2 = session.client('ec2')

    try:
        instances = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:aws:cloud9:environment', 'Values': ['*']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )

        for reservation in instances.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                public_ip = instance.get('PublicIpAddress')
                instance_id = instance.get('InstanceId')

                if public_ip:
                    print(f"[+] Cloud9 Instance Found:")
                    print(f"  [+] Instance ID: {instance_id}")
                    print(f"  [+] Public IP: {public_ip}")
                    return public_ip

        print("[-] ERROR: No running Cloud9 instance found with public IP.")
        return None

    except ClientError as e:
        print(f"[-] ERROR retrieving Cloud9 instance: {e}")
        return None

def get_alb_dns(session):
    """Retrieves the public DNS name of the Application Load Balancer."""
    print("[*] Retrieving ALB DNS Name...")
    elb = session.client('elbv2')

    try:
        response = elb.describe_load_balancers(Names=['microservicesLB'])
        load_balancers = response.get('LoadBalancers', [])

        if load_balancers:
            alb_dns = load_balancers[0].get('DNSName')
            alb_arn = load_balancers[0].get('LoadBalancerArn')

            print(f"[+] ALB Found:")
            print(f"  [+] ARN: {alb_arn}")
            print(f"  [+] DNS Name: {alb_dns}")
            return alb_dns

        print("[-] ERROR: Load balancer 'microservicesLB' not found.")
        return None

    except ClientError as e:
        print(f"[-] ERROR retrieving ALB DNS: {e}")
        return None

def setup_webdriver():
    """Sets up the Selenium WebDriver for Chrome."""
    print("[*] Setting up WebDriver...")

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=options)
        print("[+] WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"[-] ERROR initializing WebDriver: {e}")
        print("    Make sure ChromeDriver is installed and in your PATH.")
        return None

def take_screenshot(driver, url, filename, output_folder, wait_time=5):
    """Takes a screenshot of the given URL and saves it."""
    try:
        print(f"[*] Accessing: {url}")
        driver.get(url)

        # Wait for page to load
        time.sleep(wait_time)

        filepath = os.path.join(output_folder, filename)
        driver.save_screenshot(filepath)
        print(f"  [+] Screenshot saved: {filename}")
        return True

    except Exception as e:
        print(f"  [-] ERROR capturing screenshot for {url}: {e}")
        return False

def create_output_folder(profile_name):
    """Creates the output folder for screenshots."""
    output_folder = os.path.abspath(profile_name)

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"[+] Output folder created: {output_folder}")
        except Exception as e:
            print(f"[-] ERROR creating output folder: {e}")
            return None
    else:
        print(f"[+] Using existing output folder: {output_folder}")

    return output_folder

def take_snapshots(cloud9_ip, alb_dns, output_folder):
    """Takes snapshots from Cloud9 and ALB."""
    print(f"\n[*] Starting snapshot collection...")

    driver = setup_webdriver()
    if not driver:
        return False

    try:
        # URLs to capture
        urls = [
            # Cloud9 Instance
            (f"http://{cloud9_ip}:8080", "01_cloud9_port8080.png"),
            (f"http://{cloud9_ip}:8081", "02_cloud9_port8081.png"),

            # ALB - Port 8080
            (f"http://{alb_dns}:8080/admin/suppliers", "03_alb_8080_admin_suppliers.png"),
            (f"http://{alb_dns}:8080/suppliers", "04_alb_8080_suppliers.png"),
            (f"http://{alb_dns}:8080/", "05_alb_8080_root.png"),

            # ALB - Port 80
            (f"http://{alb_dns}/admin/suppliers", "06_alb_80_admin_suppliers.png"),
            (f"http://{alb_dns}/suppliers", "07_alb_80_suppliers.png"),
            (f"http://{alb_dns}/", "08_alb_80_root.png"),
        ]

        successful_captures = 0

        for url, filename in urls:
            if take_screenshot(driver, url, filename, output_folder):
                successful_captures += 1

        print(f"\n[+] Snapshot collection completed: {successful_captures}/{len(urls)} successful")
        return True

    except Exception as e:
        print(f"[-] ERROR during snapshot collection: {e}")
        return False

    finally:
        driver.quit()
        print("[+] WebDriver closed.")

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
    print(f" AWS Microservices Screenshot Tool - Phase 10")
    print(f" AWS Profile: {profile_name}")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================\n")

    try:
        # Initialize boto3 session
        session = boto3.Session(profile_name=profile_name)
    except Exception as e:
        print(f"[-] ERROR: Failed to initialize AWS session with profile '{profile_name}': {e}")
        sys.exit(1)

    # Get Cloud9 IP and ALB DNS
    cloud9_ip = get_cloud9_instance_info(session)
    print()
    alb_dns = get_alb_dns(session)

    if not cloud9_ip or not alb_dns:
        print("\n[-] ERROR: Could not retrieve required AWS resources.")
        sys.exit(1)

    # Create output folder
    print()
    output_folder = create_output_folder(profile_name)
    if not output_folder:
        sys.exit(1)

    # Take snapshots
    print()
    if take_snapshots(cloud9_ip, alb_dns, output_folder):
        print(f"\n==================================================")
        print(f" Screenshots saved to: {output_folder}")
        print(f" Total files: 8")
        print(f"==================================================\n")
    else:
        print("\n[-] Failed to capture all snapshots.")
        sys.exit(1)

if __name__ == "__main__":
    main()
