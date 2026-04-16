import json
import os
import boto3
from datetime import datetime

s3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    method = event["httpMethod"]
    params = event.get("queryStringParameters") or {}

    if method == "PUT":
        body = json.loads(event.get("body") or "{}")
        key = body.get("key", "default.txt")
        content = body.get("content", "")
        s3.put_object(Bucket=BUCKET, Key=key, Body=content)
        return response(200, {"message": f"File '{key}' created", "timestamp": now()})

    if method == "GET":
        key = params.get("key", "default.txt")
        try:
            obj = s3.get_object(Bucket=BUCKET, Key=key)
            return response(200, {"key": key, "content": obj["Body"].read().decode()})
        except s3.exceptions.NoSuchKey:
            return response(404, {"message": f"File '{key}' not found"})

    if method == "DELETE":
        key = params.get("key", "default.txt")
        s3.delete_object(Bucket=BUCKET, Key=key)
        return response(200, {"message": f"File '{key}' deleted", "timestamp": now()})

    return response(405, {"message": "Method not allowed"})


def now():
    return datetime.utcnow().isoformat()


def response(status, body):
    return {"statusCode": status, "body": json.dumps(body)}
