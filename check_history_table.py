import pymysql

conn = pymysql.connect(host='localhost', user='root', password='123456', database='guangzhou_house')
cursor = conn.cursor()

print("history表结构:")
cursor.execute('DESCRIBE history')
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]}')

print("\nhistory表数据样本:")
cursor.execute('SELECT * FROM history LIMIT 3')
for row in cursor.fetchall():
    print(f'  {row}')

cursor.close()
conn.close()
