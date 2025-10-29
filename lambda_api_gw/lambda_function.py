# lambda_get_reports/lambda_function.py
import os
import boto3
import json
from boto3.dynamodb.conditions import Key

AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
DDB_TABLE = os.environ["DDB_TABLE"]

ddb = boto3.resource("dynamodb", region_name=AWS_REGION).Table(DDB_TABLE)

def lambda_handler(event, context):
    """
    Example API Gateway event:
      GET /reports?device_id=M2
      or GET /reports (fetch all recent)
    """
    print("Event:", json.dumps(event))
    params = event.get("queryStringParameters") or {}
    device_id = params.get("device_id")

    if device_id:
        resp = ddb.query(
            IndexName="device_id-index",  # optional if you define GSI
            KeyConditionExpression=Key("device_id").eq(device_id)
        )
        items = resp.get("Items", [])
    else:
        # fallback: scan all (for demo)
        resp = ddb.scan(Limit=100)
        items = resp.get("Items", [])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(items, indent=2)
    }
