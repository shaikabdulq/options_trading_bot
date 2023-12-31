from iqoptionapi.stable_api import IQ_Option
import time
import math


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

email = 'yourmail@example.com'
password = 'password'
ACTIVES = 'EURUSD'
duration = 1
loss_count = 0
action = 'call'
total_win_count = 0
polling_time=5

Iq = IQ_Option(email, password)
Iq.connect()
# print(Iq.reset_practice_balance())
# print(Iq.get_balance())

while True:
    start_at_specific_time(10)
    if Iq.check_connect() == False: 
        print("Reconnecting...")
        Iq = IQ_Option(email, password)
        check, reason = Iq.connect()
    amount = decide_amount(loss_count)
    start_at_specific_time(26)
    _, id = (Iq.buy_digital_spot(ACTIVES, amount, action, duration))
    print(f"\nCall Option for ${round(amount,3)} made!")
    if loss_count != 12:
        while True:
            check, win = Iq.check_win_digital_v2(id)
            if check == True:
                break
        if win < 0:
            loss_count=loss_count+1
            print(f"You lose ${round(win,3)}! Loss Count: {loss_count}")
        else:
            loss_count=0
            total_win_count = total_win_count+1
            print(f"You win ${round(win,3)}! Total Win Count: {total_win_count}")
    elif id == "error":
        print("Error! Program stopped")
        quit()
    else:
        print(f"Alas! Initial capital lost! ")
        quit()
