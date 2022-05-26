import boto3
from botocore.exceptions import ClientError

# Error in sending email

def send_email(email_address: str, instance_id: str, tags_missing: list) -> None:

    ses_resource = boto3.client("ses", region_name="ap-south-1")

    sender_email = "abhiramjoshi02@gmail.com"
    recipient_email = email_address
    subject = "Warning: Termination of EC2 instance"

    body_text = f"Your EC2 instance(Instance ID = {instance_id}) will be terminated soon. Tags missing = {tags_missing}. Add these tags as soon as possible to stop termination."
                
    body_html = f"""
    <html>
    <head></head>
    <body>
    <h1>Termination of EC2 instance</h1>
    <p>
        Your EC2 instance(Instance ID = {instance_id}) will be terminated soon.
        <br><br>
        Tags missing: {tags_missing}
        <br><br>
        Add these tags as soon as possible to stop termination.
    </p>
    </body>
    </html>
    """            

    try:
        response = ses_resource.send_email(
            Destination={
                'ToAddresses': [
                    recipient_email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source = sender_email,
        )
    
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent!")


def lambda_handler(event, context):
    # TODO implement

    ec2_resource = boto3.resource("ec2")

    for ec2_instance in ec2_resource.instances.all():
        tags_present = 0
        tags_missing = ["Name", "Environment"]
        email_address = ""

        for tag in ec2_instance.tags:
            if tag.get("Key", False) == "Name":
                tags_present += 1
                tags_missing.remove("Name")
            
            if tag.get("Key", False) == "Environment":
                tags_present += 1
                tags_missing.remove("Environment")

            if tag.get("Key", False) == "created by":
                email_address = tag.get("Value", None)


        if tags_present < 2:
            print(f"Sending email to {email_address}")
            send_email(email_address, ec2_instance.id, " ".join(tags_missing))

    return {
        'statusCode': 200,
        'body': "Lambda function executed successfully",
    }

lambda_handler(None, None)