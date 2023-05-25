import mysql.connector
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsRegressor

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


def predict_gross(mycursor,mydb,genre, budget, rating, runtime, k=5):
 
    query = "SELECT Budget, Rating, Runtime, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Fetch the data and convert it to a NumPy array
    data = mycursor.fetchall()
    data = np.array(data)

    x = data[:, :-1] # :-1 is select all row except the last one (Budget, Rating, Runtime,)
    y = data[:, -1]  # select all data of the last collumn (Gross)

    knn = KNeighborsRegressor(n_neighbors=10) #select amount of neighbor to compare
    knn.fit(x, y) # Train the regressor on the selected features and gross

    # Make a prediction using the input features
    input_features = [[budget, rating, runtime]]
    predicted_gross = knn.predict(input_features).item()

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

#genre = ("Action")
#budget = 100000
#rating = 7.5
#runtime = 120

genre = input("Genre: ") 
budget = int(input("Budget: "))
rating = float(input("Rating: "))
runtime = int(input("runtime: "))
predicted_gross = predict_gross(mycursor,mydb, genre, budget, rating, runtime)
print(f"The predicted gross for a movie with genre={genre}, budget={budget}, rating={rating}, and runtime={runtime} days, is around ${predicted_gross:.2f}")

# Close the cursor and connection
mycursor.close()
mydb.close()