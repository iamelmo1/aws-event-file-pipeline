import json
import os
import urllib.parse
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]
QUARANTINE_BUCKET = os.environ["QUARANTINE_BUCKET"]

ALLOWED_SUFFIXES = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}

def _ext(key: str) -> str:
    return "." + key.rsplit(".", 1)[-1].lower() if "." in key else ""

def handler(event, context):
    batch_item_failures = []

    for record in event.get("Records", []):
        msg_id = record.get("messageId")
        try:
            body = json.loads(record["body"])

            if "Records" not in body:
                logger.info("Skipping non-S3 message body: %s", body)
                continue

            for s3_event in body["Records"]:
                bucket = s3_event["s3"]["bucket"]["name"]
                key = urllib.parse.unquote_plus(s3_event["s3"]["object"]["key"])

                logger.info("Received S3 event: bucket=%s key=%s", bucket, key)

                if not key.startswith("incoming/"):
                    logger.info("Skipping key (not in incoming/): %s", key)
                    continue

                dest_bucket = PROCESSED_BUCKET if _ext(key) in ALLOWED_SUFFIXES else QUARANTINE_BUCKET
                dest_key = key[len("incoming/"):]

                logger.info("Copying to: dest_bucket=%s dest_key=%s", dest_bucket, dest_key)

                s3.copy_object(
                    Bucket=dest_bucket,
                    Key=dest_key,
                    CopySource={"Bucket": bucket, "Key": key},
                )

        except Exception as e:
            logger.exception("Failed processing messageId=%s", msg_id)
            if msg_id:
                batch_item_failures.append({"itemIdentifier": msg_id})

    return {"batchItemFailures": batch_item_failures}

# This is the name Lambda is looking for: lambda_function.lambda_handler
def lambda_handler(event, context):
    return handler(event, context)
