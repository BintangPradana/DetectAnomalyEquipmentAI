import os, json, csv, tempfile, uuid, boto3
from urllib.parse import unquote_plus

AWS_REGION = os.environ.get("AWS_REGION","ap-southeast-1")
DDB_TABLE = os.environ["DDB_TABLE"]
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID","")
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD","0.5"))

s3 = boto3.client("s3", region_name=AWS_REGION)
ddb = boto3.resource("dynamodb", region_name=AWS_REGION).Table(DDB_TABLE)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION) if BEDROCK_MODEL_ID else None

def bedrock_report(device_id, timestamp, row):
    if not bedrock or not BEDROCK_MODEL_ID:
        return {
            "summary": f"Anomaly detected for {device_id} at {timestamp} with p={row.get('abnormal_probability','')}",
            "root_cause": "Likely bearing wear due to high vibration/temperature",
            "recommendation": "Lubricate bearing; schedule inspection"
        }
    prompt = (
        f"A machine (ID: {device_id}) shows anomaly.\n"
        f"Timestamp: {timestamp}\n"
        f"Row: {json.dumps(row)}\n"
        "Produce concise JSON with keys: summary, root_cause, recommendation."
    )
    body = {"input": prompt}
    resp = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID, contentType="application/json", accept="application/json",
        body=json.dumps(body)
    )
    raw = resp["body"].read().decode("utf-8")
    try:
        return json.loads(raw)
    except Exception:
        return {"summary": raw, "root_cause": "", "recommendation": ""}

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    for rec in event.get("Records", []):
        bucket = rec["s3"]["bucket"]["name"]
        key = unquote_plus(rec["s3"]["object"]["key"])
        with tempfile.NamedTemporaryFile() as tmp:
            s3.download_file(bucket, key, tmp.name)
            tmp.seek(0)
            reader = csv.DictReader(tmp)
            with ddb.batch_writer() as batch:
                for row in reader:
                    prob = float(row.get("abnormal_probability","0") or 0)
                    predicted = int(float(row.get("predicted_abnormal","0") or 0))
                    device_id = row.get("device_id","unknown")
                    ts = row.get("timestamp","")
                    if predicted == 1 or prob >= ANOMALY_THRESHOLD:
                        report = bedrock_report(device_id, ts, row)
                        item = {
                            "report_id": str(uuid.uuid4()),
                            "device_id": device_id,
                            "event_timestamp": ts,
                            "predicted_abnormal": predicted,
                            "abnormal_probability": str(prob),
                            "report_summary": report.get("summary",""),
                            "root_cause": report.get("root_cause",""),
                            "recommendation": report.get("recommendation","")
                        }
                        batch.put_item(Item=item)
    return {"status":"ok"}
