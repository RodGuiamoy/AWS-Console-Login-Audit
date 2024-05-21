import boto3
from datetime import datetime, timezone
import csv
import sys

# Create an IAM client
iam = boto3.client('iam')

# Function to check if the email tag is in the whitelist
def is_user_in_whitelist(user_name):
    
    whitelist = ["joshuagrabinger@deltek.com", 
                 "amirjoven@deltek.com", 
                 "markanthonysampayan@deltek.com",
                 "michaelmarsek@deltek.com",
                 "febinrajan@deltek.com",
                 "claudestevenbayla@deltek.com",
                 "tristansantiago@deltek.com",
                 "angeloallas@deltek.com"]

    response = iam.list_user_tags(UserName=user_name)
    tags = response['Tags']
    
    email_tag_value = None
    for tag in tags:
        if tag['Key'] == 'email':
            email_tag_value = tag['Value']
            break
    
    if email_tag_value.lower() in [item.lower() for item in whitelist]:
        return True
    else:
        return False

def main(aws_environment):
    
    # Get the current date
    current_date = datetime.now()

    # Format the date to MMddyyyy
    formatted_date = current_date.strftime('%m%d%Y')
    
    # Using str.replace() to remove spaces
    aws_environment = aws_environment.replace(" ", "")
    
    # Define the CSV file name
    csv_file_name = f"{aws_environment}_{formatted_date}.csv"
    
    # Define the header names based on the data we are collecting
    headers = ['UserName', 'Whitelisted', 'ConsoleAccess', 'LastLogin', 'LoggedInAfterDisablementDate']
    
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
                
                whitelisted = is_user_in_whitelist(username)

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
                    last_login = user_detail['User']['PasswordLastUsed']# .strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Define the reference date and time
                    disablement_date = datetime(2024, 3, 26, 0, 0, tzinfo=timezone.utc)

                    # Check if last_login was after the reference date
                    if last_login > disablement_date:
                        logged_in_after_disablement_date = True
                    else:
                        logged_in_after_disablement_date = False
                        
                    last_login = last_login.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    last_login = None
                    logged_in_after_disablement_date = None
                    
                # Write the user's details to the CSV
                writer.writerow({
                    'UserName': username,
                    'Whitelisted': whitelisted,
                    'ConsoleAccess': console_access,
                    'LastLogin': last_login,
                    'LoggedInAfterDisablementDate': logged_in_after_disablement_date
                })
                
                print (f"{username},{console_access},{last_login},{logged_in_after_disablement_date}")

if __name__ == "__main__":
    aws_environment = sys.argv[1]
    main(aws_environment)