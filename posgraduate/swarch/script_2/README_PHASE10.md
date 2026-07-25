# AWS Microservices Screenshot Tool - Phase 10

This Python script captures screenshots of your AWS microservices deployment, including both the Cloud9 development environment and the Application Load Balancer (ALB) endpoints. It's designed to run on Windows and requires specific prerequisites.

## Purpose

The script takes snapshots from:
- **Cloud9 Instance**: Public endpoints on ports 8080 and 8081
- **ALB (Application Load Balancer)**: Multiple endpoints across different ports and paths:
  - Port 8080: `/admin/suppliers`, `/suppliers`, `/` (root)
  - Port 80: `/admin/suppliers`, `/suppliers`, `/` (root)

Screenshots are organized in a folder named after your AWS profile for easy reference.

## Prerequisites

### System Requirements
- **OS**: Windows 10 or later
- **Python**: Python 3.7 or higher
- **Google Chrome**: Latest version installed on your machine

### Python Libraries
The script requires the following packages (install via pip):
```bash
boto3                    # AWS SDK for Python
selenium                 # Web automation framework
```

### AWS Configuration
- Valid AWS credentials configured for the specified profile
- IAM permissions to:
  - Describe EC2 instances (for Cloud9)
  - Describe load balancers (for ALB)

### ChromeDriver
Selenium requires ChromeDriver to automate Chrome:

1. **Download ChromeDriver**:
   - Go to https://chromedriver.chromium.org/
   - Download the version matching your Chrome version
   - Or use `webdriver-manager` for automatic management

2. **Installation Options**:
   
   **Option A**: Add to System PATH
   - Extract `chromedriver.exe` to a folder
   - Add that folder to your Windows PATH environment variable
   - Verify: Open Command Prompt and type `chromedriver --version`

   **Option B**: Use webdriver-manager (Recommended)
   ```bash
   pip install webdriver-manager
   ```
   - Modify line 46 in the script to:
   ```python
   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
   ```

## Installation

### Step 1: Install Python Dependencies
```bash
pip install boto3 selenium
```

### Step 2: Optional - Install webdriver-manager
```bash
pip install webdriver-manager
```

### Step 3: Configure AWS Credentials
If you haven't already configured AWS CLI:
```bash
aws configure --profile LabMicroservices
```

Or manually edit `~/.aws/credentials`:
```
[LabMicroservices]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_default_region = us-east-1
```

## Usage

### Basic Usage
Run the script with your AWS profile name:

```bash
python script2phase10.py LabMicroservices
```

### Interactive Mode
Run without arguments and enter the profile name when prompted:

```bash
python script2phase10.py
```

Then enter your profile name (e.g., `LabMicroservices`).

## Output

The script creates a folder with the same name as your AWS profile containing:

```
LabMicroservices/
├── 01_cloud9_port8080.png           # Cloud9 on port 8080
├── 02_cloud9_port8081.png           # Cloud9 on port 8081
├── 03_alb_8080_admin_suppliers.png  # ALB port 8080 /admin/suppliers
├── 04_alb_8080_suppliers.png        # ALB port 8080 /suppliers
├── 05_alb_8080_root.png             # ALB port 8080 /
├── 06_alb_80_admin_suppliers.png    # ALB port 80 /admin/suppliers
├── 07_alb_80_suppliers.png          # ALB port 80 /suppliers
└── 08_alb_80_root.png               # ALB port 80 /
```

All filenames are prefixed with numbers for easy sorting and identification.

## What the Script Does

1. **Validates AWS Profile**: Ensures the specified AWS profile is configured
2. **Retrieves Cloud9 IP**: Queries EC2 to find the running Cloud9 instance's public IP
3. **Retrieves ALB DNS**: Queries ELBv2 to find the Application Load Balancer's DNS name
4. **Sets Up WebDriver**: Initializes Chrome WebDriver for screenshot automation
5. **Captures Screenshots**: Takes screenshots of all specified endpoints
6. **Saves to Profile Folder**: Stores all images in a folder named after the profile

## Troubleshooting

### Error: "ChromeDriver not found"
**Solution**: 
- Install webdriver-manager: `pip install webdriver-manager`
- Or add ChromeDriver to your system PATH

### Error: "Failed to initialize AWS session"
**Solution**:
- Verify AWS credentials: `aws configure list --profile LabMicroservices`
- Ensure the profile name is correct
- Check that credentials have proper IAM permissions

### Error: "No running Cloud9 instance found"
**Solution**:
- Verify the Cloud9 instance is running in your AWS account
- Ensure it has a public IP address
- Check IAM permissions to describe EC2 instances

### Error: "Load balancer 'microservicesLB' not found"
**Solution**:
- Verify the ALB is created and running
- Confirm the ALB name is exactly `microservicesLB`
- Check IAM permissions to describe load balancers

### Screenshots are blank or incomplete
**Solution**:
- Increase the `wait_time` parameter in the `take_snapshot()` function (default is 5 seconds)
- Check network connectivity to the endpoints
- Verify the endpoints are accessible and returning content

### Chrome window opens but nothing happens
**Solution**:
- Close all Chrome instances and try again
- Check Chrome is fully installed and updated
- Try restarting your computer

## Advanced Usage

### Modifying Wait Time
To increase the wait time for page loads (useful for slow connections):

Edit line in the script:
```python
if take_screenshot(driver, url, filename, output_folder, wait_time=10):
```

Change `wait_time=5` to a higher value (in seconds).

### Customizing Endpoints
To add or modify endpoints, edit the `urls` list in the `take_snapshots()` function:

```python
urls = [
    (f"http://{cloud9_ip}:8080", "01_cloud9_port8080.png"),
    # Add more endpoints as needed
]
```

## Performance Notes

- The script captures 8 screenshots sequentially
- Each screenshot takes approximately 5-10 seconds
- Total execution time: typically 2-3 minutes
- Network speed and page load times affect performance

## Security Considerations

- Store AWS credentials securely
- Don't commit credentials to version control
- Use IAM roles with minimal required permissions
- Screenshots may contain sensitive data - protect the output folder

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Review AWS CloudWatch logs for service health
4. Ensure network connectivity to AWS resources

## Related Scripts

This script is part of a series of AWS microservices automation tools:
- `script2phase8.py`: CodeDeploy configuration review
- `script2phase9.py`: ECS services and deployment review
- `script2phase10.py`: Microservices screenshot tool (this script)
