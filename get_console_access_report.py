import boto3
from datetime import datetime
import csv
import sys

# Create an IAM client
iam = boto3.client('iam')

def main(aws_environment):
    
    # Get the current date
    current_date = datetime.now()

    # Format the date to MMddyyyy
    formatted_date = current_date.strftime('%m%d%Y')
    
    # Using str.replace() to remove spaces
    aws_environment = aws_environment.replace(" ", "")
    
    # Define the CSV file name
    csv_file_name = f"AWS{aws_environment}_{formatted_date}.csv"
    
    # Define the header names based on the data we are collecting
    headers = ['UserName', 'ConsoleAccess', 'LastLogin']
    
    # Open a new CSV file
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write the header
        writer.writeheader()
    
        # List all IAM users
        paginator = iam.get_paginator('list_users')
        for response in paginator.paginate():
            for user in response['Users']:
                
                username = user['UserName']
                
                # Get login profile to check console access
                try:
                    iam.get_login_profile(UserName=user['UserName'])
                    console_access = True
                except iam.exceptions.NoSuchEntityException:
                    console_access = False
                    pass

                # Get the last login date
                user_detail = iam.get_user(UserName=user['UserName'])
                if 'PasswordLastUsed' in user_detail['User']:
                    last_login = user_detail['User']['PasswordLastUsed'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_login = None             
                # Write the user's details to the CSV
                writer.writerow({
                    'UserName': username,
                    'ConsoleAccess': console_access,
                    'LastLogin': last_login
                })
                
                print (f"{username},{console_access},{last_login}")

if __name__ == "__main__":
    aws_environment = sys.argv[1]
    main(aws_environment)