import os, json, time, boto3
from urllib.parse import unquote_plus

AWS_REGION = os.environ.get("AWS_REGION","ap-southeast-1")
MODEL_NAME = os.environ["MODEL_NAME"]
TRANSFORM_INSTANCE_TYPE = os.environ.get("TRANSFORM_INSTANCE_TYPE","ml.m5.large")
TRANSFORM_INSTANCE_COUNT = int(os.environ.get("TRANSFORM_INSTANCE_COUNT","1"))
INFERENCE_OUTPUT_S3 = os.environ["INFERENCE_OUTPUT_S3"]

sm = boto3.client("sagemaker", region_name=AWS_REGION)

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    for rec in event.get("Records", []):
        bucket = rec["s3"]["bucket"]["name"]
        key = unquote_plus(rec["s3"]["object"]["key"])
        input_s3 = f"s3://{bucket}/{key}"
        job_name = f"bt-{int(time.time())}"
        sm.create_transform_job(
            TransformJobName=job_name,
            ModelName=MODEL_NAME,
            TransformInput={
                "DataSource": {"S3DataSource": {"S3DataType": "S3Prefix", "S3Uri": input_s3}},
                "ContentType": "text/csv",
                "SplitType": "Line"
            },
            TransformOutput={
                "S3OutputPath": INFERENCE_OUTPUT_S3,
                "Accept": "text/csv",
                "AssembleWith": "Line"
            },
            TransformResources={
                "InstanceType": TRANSFORM_INSTANCE_TYPE,
                "InstanceCount": TRANSFORM_INSTANCE_COUNT
            }
        )
    return {"status":"ok"}
