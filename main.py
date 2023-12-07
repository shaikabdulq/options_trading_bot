from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
import boto3

def start_at_specific_time(target_second):
    while True:
        current_time = time.localtime()
        if (current_time.tm_sec) == (target_second): # replace with your desired second
            break
        time.sleep(1)

def decide_amount(loss_count):
    progression = [
        1,
        2.123595506,
        4.509657871,
        9.576689188,
        20.33701412,
        43.18759178,
        91.71297579,
        194.7612632,
        413.5941432,
        878.3066636,
        1865.168083,
        3960.862559,
        8411.269929,
        17862.13502,
        37931.94964,
        80552.11778,
        171060.1153,
        363262.492,
        771422.5954
    ]
    return progression[loss_count]


fhand = open('/home/ec2-user/secret.txt')
data = fhand.read()
email = ((data.split(','))[0]).strip()
password = ((data.split(','))[1]).strip()
table_name = 'trading_data'

ACTIVES = "EURUSD"
region_name = 'ap-south-1'
duration = 1
loss_count = 0
action = "call"
total_win_count = 0
earnings = 0
list_of_transactions=[]
transaction = {
    'serial_no':0,
    'timestamp':'YYYY-MM-DD HH:MM:SS.000000',
    'actives':'EURUSD',
    'action':'call/put',
    'amount':0,
    'result':'loss/win',
    'win':0,
    'balance':10000,
    'earnings':0
}
serial_no = 0

Iq = IQ_Option(email, password)
Iq.connect()
balance = Iq.get_balance()
ALL_Asset=Iq.get_all_open_time()
if ALL_Asset["digital"]["EURUSD-OTC"]["open"]:
    ACTIVES = 'EURUSD-OTC'
else:
    ACTIVES = 'EURUSD'

print(f"\n\n\nTrading Bot ready ... \nBalance: {round(balance,2)} \nActive: {ACTIVES} \nEarnings: {round(earnings,2)}")
# print(Iq.reset_practice_balance())

while True:
    serial_no = serial_no + 1
    if serial_no == 121:
        print('120 Transactions completed')
        quit()
    if loss_count == 12:
        print('Oh no! All Capital Lost')
        quit()
    print(f'\nInitiating transaction {serial_no} ...')
    amount = decide_amount(loss_count)
    start_at_specific_time(26)
    if Iq.check_connect() == False:  # detect the websocket is close
        print("Reconnecting...")
        Iq = IQ_Option(email, password)
        check, reason = Iq.connect()
    _, id = (Iq.buy_digital_spot(ACTIVES, amount, action, duration))
    print(f"Call Option for ${round(amount,2)} made ...")
    while True:
        wait_count = 0
        check, win = Iq.check_win_digital_v2(id)
        time.sleep(1)
        if check == True:
            break
    balance = balance + win
    earnings = earnings + win
    if win < 0:
        loss_count=loss_count+1
        result = 'loss'
        print(f"You lose ${round(win,2)}! \nLoss Count: {loss_count}")
        print(f'Earnings: {round(earnings,2)}')
    else:
        loss_count=0
        result = 'win'
        print(f"You win ${round(win,2)}! \nBalance: {round(balance,2)}")
        print(f'Earnings: {round(earnings,2)}')
    timestamp = str(datetime.now())
    transaction = {
        'serial_no': serial_no,
        'timestamp': timestamp,
        'actives': ACTIVES,
        'action': action,
        'amount': str(amount),
        'result': result,
        'win': str(win),
        'balance': str(balance),
        'earnings': str(earnings)
    }
    list_of_transactions.append(transaction)
    if serial_no % 5 == 0:
        print("\nWriting to Database...")
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        table = dynamodb.Table(table_name)
        with table.batch_writer() as batch:
            for item in list_of_transactions:
                batch.put_item(Item=item)
        #print(list_of_transactions)
        list_of_transactions = []
