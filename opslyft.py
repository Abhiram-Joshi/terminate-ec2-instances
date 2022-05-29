import boto3
from botocore.exceptions import ClientError
import pickle

# Error in sending email

def send_email(email_address: str, instance_id: list, tags_missing: list, termination: bool) -> None:

    ses_resource = boto3.client("ses", region_name="ap-south-1")

    sender_email = "abhiramjoshi02@gmail.com"
    recipient_email = email_address
    subject = "Warning: Termination of EC2 instance"

    instance_id_string = ", ".join(instance_id)

    if not termination:
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
    
    else:
        body_text = f"Your EC2 instance(Instance ID = {instance_id}) is being terminated. Reason: Missing tags."
                    
        body_html = f"""
        <html>
        <head></head>
        <body>
        <h1>Termination of EC2 instance</h1>
        <p>
            Your EC2 instance(Instance ID = {instance_id}) is being terminated.
            <br><br>
            Reaso: Missing tags.
            <br><br>
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
    s3_resource = boto3.resource("s3")
    
    ec2_instance_reminded = []
    
    try:
        ec2_instance_reminded_serialised_object = s3_resource.Object("ec2-terminate", "ec2_instance_reminded_serialised.ser")
        ec2_instance_reminded_serialised = ec2_instance_reminded_serialised_object.get()["Body"].read()

        ec2_instance_reminded = pickle.loads(ec2_instance_reminded_serialised)

    
    except Exception as e:
        print(e)

    ec2_instances_terminate = []
    ec2_instances_terminate_dicts = []
    
    # Increasing the number of hours since sending the reminder
    for i in ec2_instance_reminded:
        i["hours_passed"]+=1
        if i.get("hours_passed") >= 6 and ec2_resource.Instance(i.get("instance_id")).state["Name"] == "running":
            ec2_instances_terminate.append(i.get("instance_id"))
            ec2_instances_terminate_dicts.append(i)
    
    for i in ec2_instances_terminate_dicts:
        ec2_instance_reminded.remove(i)
    
    if ec2_instances_terminate:
        print(f"Sending termination email for {ec2_instances_terminate}")
        send_email("abhiramjoshivit@gmail.com", ec2_instances_terminate, None, True)
        ec2_resource.instances.filter(InstanceIds = ec2_instances_terminate).terminate()
    
    print(ec2_instance_reminded)
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
        
        if tags_present < 2 and ec2_instance.id not in list(map(lambda x: x.get("instance_id", None), ec2_instance_reminded)) and ec2_instance.state["Name"] == "running":
            print(f"Sending email for {ec2_instance.id}")
            send_email(email_address, [ec2_instance.id], " ".join(tags_missing), False)
            ec2_instance_reminded.append(
                {
                    "instance_id": ec2_instance.id,
                    "hours_passed": 0,
                }
            )

    ec2_instance_reminded_serialised = pickle.dumps(ec2_instance_reminded)
    
    ec2_instance_reminded_serialised_object = s3_resource.Object("ec2-terminate", "ec2_instance_reminded_serialised.ser")
    ec2_instance_reminded_serialised_object.put(Body=ec2_instance_reminded_serialised)

    return {
        'statusCode': 200,
        'body': "Lambda function executed successfully",
    }