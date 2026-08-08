## Demo for showing ABAC Attribute-Based Access Control on S3 buckets

After deploy the terraform code, you have to review the output and create profiles on your credentials: alpha and beta.

Then, you can check using:

aws sts get-caller-identity --profile=alpha

aws sts get-caller-identity --profile=beta

On Windows for example,

set "ALPHA_BUCKET=abac-alpha-70ae1bcf"

set "BETA_BUCKET=abac-beta-70ae1bcf"

aws s3 ls s3://%ALPHA_BUCKET% --profile alpha

aws s3 ls s3://%BETA_BUCKET% --profile alpha

aws s3 ls s3://%BETA_BUCKET% --profile beta

aws s3 ls s3://%BETA_BUCKET% --profile alpha

And check the error message on the case.

For instance,

>> aws s3 ls s3://abac-alpha-aef1354c --profile beta

An error occurred (AccessDenied) when calling the ListObjectsV2 operation: User: arn:aws:iam::768312754627:user/abac-beta-aef1354c is not authorized to perform: s3:ListBucket on resource: "arn:aws:s3:::abac-alpha-aef1354c" with an explicit deny in a resource-based policy