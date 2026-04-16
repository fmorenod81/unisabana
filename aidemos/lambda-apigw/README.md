# Lambda + API Gateway Microservice Demo

Single Lambda function behind API Gateway that manages files on S3.  
Supports **GET**, **PUT**, and **DELETE** HTTP methods.

## Architecture

```
Client → API Gateway (/files) → Lambda (file-manager) → S3 Bucket
```

The S3 bucket name is passed to Lambda via the `S3_BUCKET` environment variable.

## Deploy

```bash
terraform init
terraform apply -var="s3_bucket_name=my-unique-bucket-name" --auto-approve
```

## Usage

The API endpoint is printed as `api_endpoint` after deploy.

**Create a file (PUT):**
```bash
curl -X PUT <api_endpoint> -d '{"key": "hello.txt", "content": "Hello World!"}'

```

If there are any error, please using escape quotes for instance for Windows CMD:

```
curl -X PUT <api_endpoint> -d "{\"key\": \"hello.txt\", \"content\": \"Hello World!\"}"

```

**Read a file (GET):**
```bash
curl -X GET "<api_endpoint>?key=hello.txt"
```

**Delete a file (DELETE):**
```bash
curl -X DELETE "<api_endpoint>?key=hello.txt"
```

## Destroy

```bash
terraform destroy -var="s3_bucket_name=my-unique-bucket-name"
```



BANK TEST


curl -X PUT https://t40l3jhyi0.execute-api.us-east-1.amazonaws.com/dev/files -d "{'key': 'hello.txt', 'content': 'Hello World'}"

curl -X PUT https://t40l3jhyi0.execute-api.us-east-1.amazonaws.com/dev/files -d "{\"key\": \"hello.txt\", \"content\": \"Hello World!\"}"

curl -X GET https://t40l3jhyi0.execute-api.us-east-1.amazonaws.com/dev/files -d "{\"key\": \"hello.txt\"}"

curl -X GET "https://t40l3jhyi0.execute-api.us-east-1.amazonaws.com/dev/files?key=hello.txt"