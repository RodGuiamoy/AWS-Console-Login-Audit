import boto3

# Create an IAM client
iam = boto3.client('iam')

# Specify the IAM user
user_name = 'rguiamoy'

# List MFA devices for the specified user
response = iam.list_mfa_devices(UserName=user_name)

# Extract and print the list of MFA devices
mfa_devices = response.get('MFADevices', [])

# Extract serial numbers and join them with a separator (e.g., ', ')
serial_numbers = [device['SerialNumber'] for device in mfa_devices]
serial_numbers_string = ', '.join(serial_numbers)

# Print the serial numbers in one line
print(serial_numbers_string)