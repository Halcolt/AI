import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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

def predict_gross(mycursor,genre, budget, rating, runtime):

    # Execute SELECT query to get movies data filtered by genre
    query = "SELECT Budget, Rating, Runtime, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Load the data read drom database to data in array
    data = list(mycursor.fetchall())

    # Calculate the Euclidean distance between the input features and each data point
    distances = []
    for val in data: # run through all row
        x = val[:-1]  # Features (budget, rating, runtime) || ": -1" all collumn except the last one (gross)
        y = val[-1]   # Target variable (gross) || last column
        distance = euclid([budget, rating, runtime], x) # first is the data from the movie need to compare, x is data from database
        distances.append((x, y, distance))

    # sort the [2] element (distance) in ascending order
    distances.sort(key=lambda z: z[2]) 

    k=5 # set k for the below calculation

    # Select the k nearest neighbors
    neighbors = distances[:k] # take the first 5 shortest distance 

    # Calculate the average gross of the k nearest neighbors
    total_gross = sum(neighbor[1] for neighbor in neighbors)
    predicted_gross = total_gross / k   # we set the predict one to be the average of the 5 closest
    return predicted_gross

def calculate_average_values(mycursor, genre):
    query = "SELECT AVG(Gross), AVG(Budget) FROM movies WHERE Genre = %s"
    mycursor.execute(query, (genre,))
    result = mycursor.fetchone()
    average_gross = result[0]
    average_budget = result[1]
    return average_gross, average_budget

def list_genres(mycursor):
    # Execute SELECT query to get unique genres from the database
    query = "SELECT DISTINCT Genre FROM movies"
    mycursor.execute(query)
    genres = mycursor.fetchall()

    print("Average rate of Value(Gross / Budget):")
    for genre in genres:
        genre_name = genre[0]
        average_gross, average_budget = calculate_average_values(mycursor, genre_name)
        average_ratio = average_gross / average_budget
        print(f"{genre_name}: {average_ratio:.2f}")


def Statistic(mycursor):
    # Execute SELECT query to get movies data filtered by genre
    list_genres(mycursor)
    genre = input("Enter genre: ")
    query = "SELECT Budget, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Load the data read drom database to data
    data = mycursor.fetchall()

    # Separate budget and gross into separate lists
    budget = [val[0] for val in data]
    gross = [val[1] for val in data]

    # Convert budget and gross lists to numpy arrays
    budget = np.array(budget).reshape(-1, 1)
    gross = np.array(gross)

    # Fit a linear regression model, aka: redline 
    regression_model = LinearRegression()
    regression_model.fit(budget, gross)

    # Generate predicted values for the regression line
    predicted_gross = regression_model.predict(budget)

    # Plot budget vs gross
    plt.scatter(budget, gross)
    plt.xlabel("Budget")
    plt.ylabel("Gross")
    plt.title(f"Budget vs Gross for Genre: {genre}")

    # label axis
    budget_units = [unit / 10000000 for unit in plt.xunits()[0]]
    gross_units = [unit / 10000000 for unit in plt.yunits()[0]]
    plt.xunits(plt.xunits()[0], ['${:.1f}M'.format(unit) for unit in budget_units])
    plt.yunits(plt.yunits()[0], ['${:.2f}M'.format(unit) for unit in gross_units])

    # Plot the regression line
    plt.plot(budget, predicted_gross, 'r-', label='Regression Line')
    plt.show()

def menu():
    # Connect to the database
    mydb = connect_to_database()
    mycursor = mydb.cursor()

    # Turn off safe mode ** Always need when start init the database
    mycursor.execute("SET SQL_SAFE_UPDATES = 0")
    mydb.commit()

    while True:
        print("Menu:")
        print("1. Statistical Analysis")
        print("2. Gross Prediction")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            
            Statistic(mycursor)
            break
        elif choice == "2":
            list_genres(mycursor)
            genre = input("Enter genre: ")
            budget = int(input("Enter budget: "))
            rating = float(input("Enter rating: "))
            if (rating > 10 or rating < 0):
                print("Rating is between 0.0 and 10.0, please try again")
                exit()
            runtime = int(input("Enter runtime: "))
            predicted_gross = predict_gross(mycursor, genre, budget, rating, runtime)
            print(f"The predicted gross for a movie with genre={genre}, budget={budget}, rating={rating}, and runtime={runtime} days, is around ${predicted_gross:.2f}")
            break
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

    # Close the cursor and connection
    mycursor.close()
    mydb.close()

# Main program
menu()


'''
#test data
genre = ("Action")
budget = 100000
rating = 7.5
runtime = 120

'''


