import mysql.connector

mydb = mysql.connector.connect(
    host='std-mysql',
    user='std_1455_map_way',
    passwd='12345678',
    database='std_1455_map_way'
)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM Place;")
myresult = mycursor.fetchall()
print(myresult[0])
