import boto3
import io
import logging
from PIL import Image, ImageDraw

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Specify S3 bucket names
Original_bucket = 'invoice-kxseafood-591543'
Json_output_bucket = 'extract-response-output-v1-us-east-1'
Modified_image_bucket = 'invoice-boxes' # create and name bucket (unless this is handled elsewhere)

def draw_bounding_box(key, val, width, height, draw):
    # Code for drawing bounding boxes
    if "Geometry" in key:
        box = val["BoundingBox"]
        left = width * box['Left']
        top = height * box['Top']
        draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])], outline='black')

def print_labels_and_values(field):
    #  Code for printing labels and values
    if "LabelDetection" in field:
        logger.info("Summary Label Detection - Confidence: {}, Summary Values: {}".format(
            str(field.get("LabelDetection")["Confidence"]),
            str(field.get("LabelDetection")["Text"])
        ))
        logger.info(field.get("LabelDetection")["Geometry"])
    else:
        logger.info("Label Detection - No labels returned.")
    if "ValueDetection" in field:
        logger.info("Summary Value Detection - Confidence: {}, Summary Values: {}".format(
            str(field.get("ValueDetection")["Confidence"]),
            str(field.get("ValueDetection")["Text"])
        ))
        logger.info(field.get("ValueDetection")["Geometry"])
    else:
        logger.info("Value Detection - No values returned")

def process_invoice(event, context):
    # Initialize AWS clients
    s3_client = boto3.client('s3')
    textract_client = boto3.client('textract')

    # Retrieve S3 bucket and object key from Lambda event
    bucket = event['Records'][0]['s3']['bucket']['name']
    document = event['Records'][0]['s3']['object']['key']

    # Step 1: Analyze the original invoice
    response = textract_client.analyze_expense(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}}
    )

    # Log info about the analysis
    logger.info("Analyzed invoice: {}".format(document))

    # Step 2: Store the JSON output in the "textract-invoice-data" bucket
    json_output = response  # Replace with the actual JSON data
    s3_client.put_object(
        Bucket='textract-invoice-data',
        Key=f'{document}.json',
        Body=json_output
    )

    # Log info about storing JSON data
    logger.info("Stored JSON data in 'textract-invoice-data' bucket")

    # Step 3: Create a new version of the invoice with bounding boxes
    s3_object = s3_client.Object(bucket, document)
    s3_response = s3_object.get()
    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)
    width, height = image.size
    draw = ImageDraw.Draw(image)

    # Iterate through the response and draw bounding boxes
    for expense_doc in response["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    for key, val in expense_fields["ValueDetection"].items():
                        if "Geometry" in key:
                            draw_bounding_box(key, val, width, height, draw)

        for label in expense_doc["SummaryFields"]:
            if "LabelDetection" in label:
                for key, val in label["LabelDetection"].items():
                    draw_bounding_box(key, val, width, height, draw)

    # Save the modified image with bounding boxes
    modified_image_path = f'/tmp/{document}'
    image.save(modified_image_path)
    s3_client.upload_file(modified_image_path, 'invoice-boxes', document)

    # Log info about creating the modified invoice
    logger.info("Created modified invoice with bounding boxes")

def lambda_handler(event, context):
    process_invoice(event, context)
