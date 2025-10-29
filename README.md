# DetectAnomalyEquipmentAI

Directory Information:

demo: contains demo jupyter notebook to run locally

lambda_api_gw: contains lambda function for API gateway integration

lambda_process_report: contains lambda function to proccess sagemaker output with recommendation from Bedrock

lambda_trigger_transform: contains lambda function to trigger sagemaker to transform the input for anomaly detection.

presentation: contains powerpoint file.

sagemaker: training and inference script

samples: sample input and output


API Documentation
GET /reports

Description: Retrieve recent or device-specific anomaly reports from DynamoDB.
Lambda: lambda_get_reports/lambda_function.py

Query Parameters
Name	Type	Required	Description
device_id	string	No	If provided, filters reports by device ID. Otherwise returns latest 100.
Example Request
GET https://api.example.com/reports?device_id=M2

Response (200 OK)
[
  {
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "device_id": "M2",
    "event_timestamp": "2025-10-20T10:15:00Z",
    "predicted_abnormal": 1,
    "abnormal_probability": "0.91",
    "report_summary": "Anomaly detected with 91% probability",
    "root_cause": "Bearing wear due to mechanical friction",
    "recommendation": "Lubricate and inspect bearing"
  }
]
