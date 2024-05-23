import boto3

# Initialize a session using Amazon IAM
session = boto3.Session()
iam = session.client('iam')

# Function to list access keys for a specific user
# def list_user_access_keys(user_name):
#     access_keys = iam.list_access_keys(UserName=user_name)
#     return access_keys['AccessKeyMetadata']

# Accept username as input
username = 'rguiamoy'

# try:
#     # Get the access keys for the specified user
#     access_keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
#     if not access_keys:
#         result = "No access keys found for this user."
#     else:
#         result_lines = []
#         for key in access_keys:
#             result_lines.append(f"Access Key ID: {key['AccessKeyId']}, Status: {key['Status']}")
#         result = "\n".join(result_lines)
# except Exception as e:
#     result = f"An error occurred: {e}"

# print(result)
try:
    # Get the access keys for the specified user
    access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetaData']
    if not access_keys:
        result = "No access keys found for this user."
    else:
        result_lines = []
        for key in access_keys:
            result_lines.append(f"Access Key ID: {key['AccessKeyId']}, Status: {key['Status']}")
        result = "\n".join(result_lines)
except Exception as e:
    result = f"An error occurred: {e}"

print(result)
