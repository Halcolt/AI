import mysql.connector
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


def euclidean_distance(x1, x2):
    # Calculate the Euclidean distance between two points
    distance = 0.0
    for i in range(len(x1)):
        distance += (x1[i] - x2[i]) ** 2
    return distance

def predict_gross(genre, budget, rating, runtime, k=5):
    # Connect to MySQL database
    mydb = connect_to_database()

    # Create a cursor object to execute SQL queries
    mycursor = mydb.cursor()

    # Execute SELECT query to get movies data filtered by genre
    query = "SELECT Budget, Rating, Runtime, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Fetch the data
    data = mycursor.fetchall()

    # Close the cursor and connection
    mycursor.close()
    mydb.close()

    # Convert the data to a list
    data = list(data)

    # Calculate the Euclidean distance between the input features and each data point
    distances = []
    for item in data:
        x = item[:-1]  # Features (budget, rating, runtime)
        y = item[-1]   # Target variable (gross)
        distance = euclidean_distance([budget, rating, runtime], x)
        distances.append((x, y, distance))

    # Sort the distances in ascending order
    distances.sort(key=lambda x: x[2])

    # Select the k nearest neighbors
    neighbors = distances[:k]

    # Calculate the average gross of the k nearest neighbors
    total_gross = sum(neighbor[1] for neighbor in neighbors)
    predicted_gross = total_gross / k

    return predicted_gross

# Connect to the database
mydb = connect_to_database()

# Turn off safe mode
mycursor = mydb.cursor()
mycursor.execute("SET SQL_SAFE_UPDATES = 0")
mydb.commit()

# Set Profit 
mycursor.execute("Update movies SET Profit = Gross-Budget")
mydb.commit()

genre = input("Genre: ") 
budget = int(input("Budget: "))
rating = float(input("Rating: "))
runtime = int(input("runtime: "))
predicted_gross = predict_gross(genre, budget, rating, runtime)
print(f"The predicted gross for a movie with genre={genre}, budget={budget}, rating={rating}, and runtime={runtime} days, is around ${predicted_gross:.2f}")

# Close the cursor and connection
mycursor.close()
mydb.close()
