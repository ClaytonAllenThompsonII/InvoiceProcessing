"""
Purpose
An AWS Lambda function that analyzes invoices with Amazon Textract
"""
import base64
import logging
import json
import boto3

from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)                #Set up logging
textract_client = boto3.client('textract')          #Initialize the Textract client.



def lambda_handler(event, context):
    # Get s3 Bucket and object information from the trigger event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']

    # Specify the S3 bucket where you want to store Textract output
    output_bucket = 'extract-response-output-v1-us-east-1' # Add outout bucket to S3 called ""

    # Call Textract to process the invoice PDF
    response = textract_client.analyze_expense(
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
    s3_client = boto3.client('s3')          # A low-level client representing Amazon Simple Storage Service (S3)
    s3_client.put_object(                   # Adds an object to a bucket. You must have WRITE permissions on a bucket to add an object to it.
        Bucket=output_bucket,
        Key=s3_key.replace('pdf', 'json'),  # Change file extension if needed
        Body=json.dumps(extracted_data, indent=4)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('PDF processing complete!')
    }

def extract_data(textract_result): #textract_response is the parameter passed to the function, which represents the Textract response. Contains the info extracted from the PDF invoice. 
    # Modify this function to extract the structured data you need from Textract response
    # Textract response structure can be complex; you may need to parse it accordingly
    extracted_data = {}  # Extracted data should be in a structured format. Populate this dictionary with extracted data. 
    # Extract data here...

    invoice_number = textract_result['Blocks'][0]['text']
    




    return extracted_data




