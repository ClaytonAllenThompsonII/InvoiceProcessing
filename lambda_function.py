"""
Purpose
An AWS Lambda function that analyzes invoices with Amazon Textract
"""
import base64
import logging
import json
import boto3

from botocore.exceptions import ClientError

#Set up logging
logger = logging.getLogger(__name__)
#Initialize the Textract client.
textract_client = boto3.client('textract')


def lambda_handler(event, context):
   

    # Get s3 Bucket and object information from the trigger event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']

    # Specify the S3 bucket where you want to store Textract output
    output_bucket = 'your-output-bucket'

    # Call Textract to process the PDF
    response = textract_client.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
    )

    # Get the Job ID from the Textract response
    job_id = response['JobId']


    # Wait for Textract job to complete
    textract_client.get_waiter('document_text_detection_completed').wait(JobId=job_id)

    # Retrieve the Textract results
    result = textract_client.get_document_text_detection(JobId=job_id)

    # Extract structured data from Textract response (modify as needed)
    extracted_data = extract_data(result)

    # Store the extracted data in another S3 bucket
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=output_bucket,
        Key=s3_key.replace('pdf', 'json'),  # Change file extension if needed
        Body=json.dumps(extracted_data, indent=4)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('PDF processing complete!')
    }

def extract_data(textract_result):
    # Modify this function to extract the structured data you need from Textract response
    # Textract response structure can be complex; you may need to parse it accordingly
    extracted_data = {}  # Extracted data should be in a structured format
    # Extract data here...

    




    return extracted_data




