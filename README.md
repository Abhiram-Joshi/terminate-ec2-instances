# Terminate EC2 instances

## Deployment steps of the lambda function:-
1. Start with creation of the lsmbda function by selecting the "Author from scratch" option
2. Write the function name
3. Choose the runtime as `Python 3.9`
4. For permissions, choose the `use an existing role` option and choose the role you have created. Create the role by following the steps mentioned.
5. Create function
6. Add a EventBridge (CloudWatch Events) trigger by making a rule to run the lambda function every hour.
7. Write the code into the editor.
8. Save the file(Test if needed) and deploy the code.

## Creating a role for the lambda function
1. Go to IAM user management and then the roles section underneath it.
2. Create a role for AWS lambda service
3. For this particular project, I attached `AmazonEC2FullAccess`, `AmazonS3FullAccess` and `AmazonSESFullAccess` policies to the role.