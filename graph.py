import boto3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

no_of_trans = 100 #Update as needed.
#No of transactions should be same as number of items in database
table_name = 'trading_data'


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
response = table.scan(Limit=120)
# print(response)
dict={}
for item in response['Items']:
    serial_no = int(item['serial_no'])
    earnings = round(float(item['earnings']),2)
    dict[serial_no] = earnings

# print(dict)
serial_no_list=[]
earnings_list=[]

for i in range(no_of_trans):
    serial_no_list.append(i+1)
    earnings_list.append(dict[i+1])
# print(dict)
# print(serial_no_list)
# print(earnings_list)

df = pd.DataFrame({"Serial No": serial_no_list, "Earnings": earnings_list})
df.sort_values(by="Serial No", inplace=True)  # Sort by serial no

sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(x="Serial No", y="Earnings", data=df, marker='o', color='b')
plt.title("Earnings Over Transactions")
plt.xlabel("Serial Number of Transaction")
plt.ylabel("Earned Amount")
plt.xticks((df['Serial No'][df["Serial No"] % 8 ==0]))
plt.show()
