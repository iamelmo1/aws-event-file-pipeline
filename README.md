AWS Event Driven Pipeline

Uploads = "angel-pipeline-ingest" (S3)  
S3 event = "angel-pipeline-queue" (SQS)
SQS trigger = "lambdas3sqs" (Lambda)  
Lambda copies:
- allowed extensions: `angel-pipeline-processed`
- everything else: `angel-pipeline-quara`

#Services that are being used

- S3: 3 buckets (ingest, processed, quarantine)
- SQS: main queue + DLQ
- Lambda: Python 3.14 function reading from SQS
- IAM: custom policy "3buckets4life" for S3 access

#Lambda actions 

See "lambda_function.py":
- Parses SQS messages
- Reads S3 event records
- Filters "incoming/" prefix
- Routes files by extension
- Returns partial batch response with "batchItemFailures"

#Useful CLI commands 

```bash
aws s3api get-bucket-notification-configuration \
  --bucket angel-pipeline-ingest

aws s3api put-bucket-notification-configuration \
  --bucket angel-pipeline-ingest \
  --notification-configuration file://infra/notif.json
