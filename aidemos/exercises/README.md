Please download the images with sample deployment

**GEMINI**
@AWS_SAA_C02_Labs-Labs6c2.jpg With this picture create a terraform project on a folder called TF_labs6c2. Input parameters are: instance type, CIDR for VPCs: vpcn, vpcp. Notice the port and the docker image; for each layer: 80 and 8080; docker image: fmorenod81/mtwa:web and fmorenod81/mtwa:app.

**GITHUB COPILOT**
Create the infrastructure on AWS using terraform given on the attached image. Use keypair, CIDR, as a input parameter. Omit the spot instance, instead using ondeman instance. Create the code on a folder called TF_ex5.
I attached AWS_SAA_C02_Labs-Labs5c1.jpg


**Troubleshooting**

* You can't create policies or roles.
* Keyfile on Windows usually bother when your use SSH. Google it.
* Review the dependencies in some case: EIP and ENI. Do it on console, to review the feasibility and then, do it on Terraform.
* Wrong code to install Docker. It's based on Operating System, Linux Distribution, etc.
* Review its prefix for resource naming using terraform plan
