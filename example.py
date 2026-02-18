import boto3
import json

# The full ARN of the DynamoDB table in Account A
# The region must match the table's region
TABLE_ARN = "arn:aws:dynamodb:us-east-1:982352146950:table/tablaprueba"
REGION = "us-east-1" # e.g., 'us-east-1'

# Initialize the DynamoDB client using credentials from Account B
# Boto3 automatically uses configured credentials (e.g., from environment variables,
# a configured AWS CLI profile, or EC2/Lambda execution role)
dynamodb_client = boto3.client('dynamodb', region_name=REGION)

def query_cross_account_dynamodb(partition_key_value, sort_key_value):
    try:
        response = dynamodb_client.query(
            TableName=TABLE_ARN,
            KeyConditionExpression='PK = :pk_val AND SK = :sk_val',
            ExpressionAttributeValues={
                ':pk_val': {'S': partition_key_value},
                ':sk_val': {'S': sort_key_value}
            }
        )
        print("Query successful. Items:")
        for item in response.get('Items', []):
            print(json.dumps(item, indent=2))
        return response

    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return None

# Example usage (replace with your actual keys and values)
# The KeyConditionExpression needs to match your table's schema (PK/SK names)
query_cross_account_dynamodb('cualquiercosa', '12')
