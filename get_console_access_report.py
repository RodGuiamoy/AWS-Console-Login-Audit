import boto3
from datetime import datetime, timezone
import csv
import sys

# Create an IAM client
iam = boto3.client('iam')

def get_user_tags(username):
    response = iam.list_user_tags(UserName=username)
    return {tag['Key']: tag['Value'] for tag in response['Tags']}

# # Function to check if the email tag is in the whitelist
# def is_user_in_whitelist(user_tags):
    
#     whitelist = ["joshuagrabinger@deltek.com", 
#                  "amirjoven@deltek.com", 
#                  "markanthonysampayan@deltek.com",
#                  "michaelmarsek@deltek.com",
#                  "febinrajan@deltek.com",
#                  "claudestevenbayla@deltek.com",
#                  "tristansantiago@deltek.com",
#                  "angeloallas@deltek.com"]

#     # # response = iam.list_user_tags(UserName=user_name)
#     # tags = get_user_tags(user_name)
    
#     email_tag_value = None
#     for tag in user_tags:
#         if tag['Key'] == 'email':
#             email_tag_value = tag['Value']
#             break
    
#     if email_tag_value is not None:
#         if email_tag_value.lower() in [item.lower() for item in whitelist]:
#             return True
#         else:
#             return False
        
#     return False

def get_email_address(user_tags):        
    email = user_tags.get('email', None)
        
    return email

def is_service_account(user_tags):
    employee_ID = user_tags.get('employeeID', None) # Default to None if 'employeeID' tag doesn't exist
            
    if employee_ID == 'service-account':
        return True
    
    return False

def get_mfa(username):
    # List MFA devices for the specified user
    response = iam.list_mfa_devices(UserName=username)

    # Extract and print the list of MFA devices
    mfa_devices = response.get('MFADevices', [])

    # Extract serial numbers and join them with a separator (e.g., ', ')
    serial_numbers = [device['SerialNumber'] for device in mfa_devices]
    serial_numbers_string = ', '.join(serial_numbers)

    # Print the serial numbers in one line
    return serial_numbers_string
    

def get_access_keys(username):
    try:
        # Get the access keys for the specified user
        access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
        if not access_keys:
            result = None
        else:
            result_lines = []
            for key in access_keys:
                result_lines.append(f"Access Key ID: {key['AccessKeyId']}, Status: {key['Status']}")
            result = "\n".join(result_lines)
    except Exception as e:
        result = f"An error occurred: {e}"

    # print(result)
    return result

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
    headers = ['UserName', 'Email', 'ConsoleAccess', 'LastLogin', 'LoggedInAfterDisablementDate', 'IsServiceAccount', 'MFA', 'AccessKeys']
    
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
                user_tags = get_user_tags(username)
                
                email = get_email_address(user_tags)
                service_account = is_service_account(user_tags)
                mfa = get_mfa(username)
                access_keys = get_access_keys(username)
                                
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
                    'Email': email,
                    'ConsoleAccess': console_access,
                    'LastLogin': last_login,
                    'LoggedInAfterDisablementDate': logged_in_after_disablement_date,
                    'IsServiceAccount': service_account,
                    'MFA': mfa,
                    'AccessKeys': access_keys
                })
                
                print (f"{username}")

if __name__ == "__main__":
    aws_environment = sys.argv[1]
    main(aws_environment)