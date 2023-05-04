import mysql.connector
from sklearn.cluster import KMeans
import numpy as np
def connect_to_database():
    # Read MySQL config from config.txt file
    with open("config.txt") as f:
        host = f.readline().strip()
        user = f.readline().strip()
        password = f.readline().strip()
        database = f.readline().strip()

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            print('Connection Successful')
            return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}") 
        exit()

# Connect to the database
mydb = connect_to_database()
# Create a cursor object
mycursor = mydb.cursor()

#turn off safe mode
mycursor.execute("SET SQL_SAFE_UPDATES = 0")
mydb.commit()

#Set Profit inmovies table
mycursor.execute("Update movies SET Profit = Gross-Budget")
mydb.commit()

mycursor.close()
mydb.close()