import boto3
import time
import paramiko
import json

user_data = '''#!/bin/bash
yum update -y
yum install -y pip
pip install websocket-client==0.56
pip install -U https://github.com/iqoptionapi/iqoptionapi/archive/refs/heads/master.zip
yum install -y git
git clone https://github.com/shaikabdulq/options_trading_bot.git /home/ec2-user/options_trading_bot
yum install -y tmux
pip install boto3'''
key_filename = input('Enter Key Filename (including .pem): ')
email_id = input('Enter IQ Options Id: ')
password = input('Enter IQ Option Password: ')
key_name = (key_filename.split('.'))[0]
iam_role_name = ''
iam_role_arn = ''
security_group_id = ''

# Create IAM Role
try:
    client = boto3.client('iam')
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    trust_policy_json = json.dumps(trust_policy)
    response = client.create_role(RoleName='trading_bot_role',AssumeRolePolicyDocument=trust_policy_json)
    client.attach_role_policy(RoleName='trading_bot_role',PolicyArn='arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess')
    print('IAM Role Created: trading_bot_role')
except:
    iam_role_name = 'trading_bot_role'

# Create Security Group
try:
    ec2 = boto3.client('ec2')
    response = ec2.create_security_group(GroupName='Allow_only_SSH_for_trading_bot',Description='Allow SSH inbound and all outbound')
    security_group_id = response['GroupId']
    ec2.authorize_security_group_ingress(GroupId=security_group_id,IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ])
    print(f'Security group ({security_group_id}) created, allowing only SSH for inbound.')
except:
    response = ec2.describe_security_groups(GroupNames=['Allow_only_SSH_for_trading_bot'])
    for i in response['SecurityGroups']:
        security_group_id = i['GroupId']

# Create Dynamodb table
try:
    import boto3
    dynamodb = boto3.resource('dynamodb')
    table_name = 'trading_data'
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'serial_no',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'serial_no',
                'AttributeType': 'N'  # Assuming serial_no is a number. Change if it's a different type.
            }
        ],
        BillingMode='PAY_PER_REQUEST')
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f'DynamoDB Table "{table_name}" created')
except:
    pass

# Create EC2 Instance
client = boto3.client('ec2',region_name='ap-south-1')
print("\nCreating EC2 Instance...")
print(iam_role_name)
response = client.run_instances(
    ImageId='ami-02a2af70a66af6dfb',
    InstanceType='t2.micro',
    MaxCount=1,
    MinCount=1,
    KeyName=key_name,
    SecurityGroupIds=[security_group_id],
    UserData=user_data,
    IamInstanceProfile={
        'Name': iam_role_name
    }
)
instance_id = response["Instances"][0]['InstanceId']
time.sleep(10)
response = client.describe_instances(InstanceIds=[instance_id])
public_dns = response['Reservations'][0]['Instances'][0]['PublicDnsName']
print("EC2 Instance Created!")
print('\nRunning bootstrap script...')
time.sleep(60)
print('Instance Ready!')

#SSH
hostname = public_dns
port = 22
username = "ec2-user"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


print('\nInitiating SSH...')
client.connect(hostname, port=port, username=username, key_filename=key_filename)
print('Running commands...')

command = f"echo {email_id},{password} > /home/ec2-user/secret.txt"
client.exec_command(command)
time.sleep(1)

command = "tmux"
stdin, stdout, stderr = client.exec_command(command)
print(stdout.read().decode("utf-8"))
time.sleep(5)

command = "python3 /home/ec2-user/options_trading_bot/main.py"
client.exec_command(command)
client.close()
print('Trading Bot Initiated!')
