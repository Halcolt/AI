import mysql.connector
import numpy as np


def connect_to_database(): #connect to Mysql
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
        print(f"Error connecting to MySQL: {e}") #print error message 
        exit()

def euclid(x1, x2): 
    # Calculate the Euclidean distance between two points
    distance = 0.0
    for i in range(len(x1)): # both x1, x2: budget, rating, runtime
        distance += (x1[i] - x2[i]) ** 2 # i dont' use sqrt here because there is no need to check for the distance, we only need to compare distance
    return distance

def predict_gross(mydb,mycursor,genre, budget, rating, runtime, k=5): 
    # Execute SELECT query to get movies data filtered by genre
    query = "SELECT Budget, Rating, Runtime, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Fetch the data
    data = mycursor.fetchall()
    data = list(data)

    # Calculate the Euclidean distance between the input features and each data point
    distances = []
    for item in data: # run through all row
        x = item[:-1]  # Features (budget, rating, runtime) || ": -1" all collumn except the last one
        y = item[-1]   # Target variable (gross) || last column
        distance = euclid([budget, rating, runtime], x)
        distances.append((x, y, distance))

    # Sort the distances in ascending order
    distances.sort(key=lambda z: z[2])

    # Select the k nearest neighbors
    neighbors = distances[:k] # take the first 5 shortest distance 

    # Calculate the average gross of the k nearest neighbors
    total_gross = sum(neighbor[1] for neighbor in neighbors)
    predicted_gross = total_gross / k   # we set the predict one to be the average of the 5 closest
    return predicted_gross

# Connect to the database
mydb = connect_to_database()
mycursor = mydb.cursor()

# Turn off safe mode
mycursor.execute("SET SQL_SAFE_UPDATES = 0")
mydb.commit()

# Set Profit 
mycursor.execute("Update movies SET Profit = Gross-Budget")
mydb.commit()

#test data
genre = ("Action")
budget = 100000
rating = 7.5
runtime = 120

'''
genre = input("Genre: ") 
budget = int(input("Budget: "))
rating = float(input("Rating: "))
runtime = int(input("runtime: "))
'''
predicted_gross = predict_gross(mydb,mycursor,genre, budget, rating, runtime) # run predict function
print(f"The predicted gross for a movie with genre={genre}, budget={budget}, rating={rating}, and runtime={runtime} days, is around ${predicted_gross:.2f}")

# Close the cursor and connection
mycursor.close()
mydb.close()
