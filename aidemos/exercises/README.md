Please download the images with sample deployments.

I use Amazon Q Developer (Kiro), GitHub Copilot and Gemini to produce the solutions.
app-nlb-35339c7611196c76.elb.us-east-1.amazonaws.com
**Gemini**

@AWS_SAA_C02_Labs-Labs6c2.jpg With this picture create a terraform project on a folder called TF_labs6c2. Input parameters are: instance type, CIDR for VPCs: vpcn, vpcp. Notice the port and the docker image; for each layer: 80 and 8080; docker image: fmorenod81/mtwa:web and fmorenod81/mtwa:app.


**GitHub Copilot**

Create the infrastructure on AWS using terraform given on the attached image. Use keypair, CIDR, as a input parameter. Omit the spot instance, instead using ondeman instance. Create the code on a folder called TF_ex5.
I attached AWS_SAA_C02_Labs-Labs5c1.jpg

**Gemini**

@AWS_SAA_C02_Labs-Labs6c2.jpg Create a terraform code for that image, create folder calle TF_Exercise_6c2 for it. You have to allow SSH for any IP address, and receive the keypair as parameter. DOcker image are fmorenod81/mtwa:web and fmorenod81/mtwa:app. The APPSERVER is a environmental variable for Docker on Public Subnets on vpcn. Review the rigth launch on docker images on vpcp to have connecvity. All subnets can see each others, so review the routing table using vpc peering.


**Troubleshooting**

* You can't create policies, roles, keypair, or spot instances. So you have to modify the prompt to override the information on the picture.
* Keyfile on Windows usually bother when your use SSH. Google it.
* Review the dependencies in some case: EIP and ENI. Do it on console, to review the feasibility and then, do it on Terraform.
* Code Assistant don't create the Security Groups for your machine, in order to have SSH, so review it; in addition to other records, for instance on Routing Tables.
* Wrong code to install Docker. It's based on Operating System, Linux Distribution, etc. The Code Assistant will try to generalize and it can be wrong, so you have to review it.
* Review its prefix for resource naming using terraform plan, for instance starting with i- or aws-


** Tested on AWS Academy Architectin on AWS - Sandbox Account **


TF_exercise0: S3 bucket with 4 digits random as prefix

TF_exercise1: EC2 with a specific keypair. Why don't work my SSH ?

TF_exercise2: VPC, Subnet, and EC2 with specific keypair, cidr for VPC, EBS size and instance type with a validation. Why don't work my SSH ?

TF_exercise4c1: Solution from Image AWS_SAA_C02_Labs-Labs4c1.jpg

TF_exercise4c2: Solution from Image AWS_SAA_C02_Labs-Labs4c2.jpg

