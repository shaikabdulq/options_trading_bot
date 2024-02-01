import boto3
import time
import paramiko
import json

key_filename = input('Enter Key Pair Name(including .pem): ')
email_id = input('Enter IQ Options Id: ')
password = input('Enter IQ Option Password: ')
key_name = (key_filename.split('.'))[0]

#SSH
hostname = input("Public DNS of EC2")
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
