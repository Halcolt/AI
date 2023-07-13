import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression


def connect_database(): #connect to Mysql
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
    for i in range(len(x1)):
        distance += (x1[i] - x2[i]) ** 2
    return distance

def cluster_data(field_values, num_clusters):
    # Convert data to a NumPy array
    field_values = np.array(field_values).reshape(-1, 1)
    field_values = np.sort(field_values, axis=0, kind='quicksort')

    # Cluster data using KMeans
    kmeans = KMeans(n_clusters=num_clusters, n_init=5)
    labels = kmeans.fit_predict(field_values)

    # Zip the data and labels together
    clustered_data = list(zip(field_values, labels))

    # Re-labeling so that both data and labels are in ascending order
    old_label = -1
    new_label = 0
    for i, (value, label) in enumerate(clustered_data):
        if label != old_label:
            old_label = label
            new_label += 1
            label = new_label
            clustered_data[i] = (value, label)
        else:
            label = new_label
            clustered_data[i] = (value, label)
    return clustered_data

def predict_gross(mycursor, genre, budget, rating, runtime, num_clusters=10):
    # Execute SELECT query to get movies data filtered by genre
    query = "SELECT Budget, Rating, Runtime, Gross FROM movies WHERE Genre=%s"
    mycursor.execute(query, (genre,))

    # Load the data read from the database to an array
    data = list(mycursor.fetchall())

    # Convert the tuples in data to lists
    data = [list(row) for row in data]

    # Append budget point to data[4]
    for row in data:
        row.append(row[0])

    # Append runtime point to data[5]
    for row in data:
        row.append(row[2])

    clustered_data = []
    # Loop through rows 4 to 5 - budget_point to runtime_point
    clustered_data.append(cluster_data([row[4] for row in data], num_clusters))
    clustered_data.append(cluster_data([row[5] for row in data], num_clusters))

    # Assign labels to data[4] and data[5]
    for i in range(len(data)):
        budget_point = data[i][4]
        runtime_point = data[i][5]
        for value, label in clustered_data[0]:
            if budget_point <= value[0]:
                data[i][4] = label
                break
        for value, label in clustered_data[1]:
            if runtime_point <= value[0]:
                data[i][5] = label
                break
    
    # Calculate the average of budget_point, rating, and runtime_point
    for row in data:
        average = (row[1]+row[4]+row[5]) / 3
        row.append(average)

    # Print the updated data with labels
    print("Data with Labels:")
    for row in data:
        print(row)

    budget_point = []
    for val in data:
        value = val[0]  # Budget value
        label = val[4]  # Budget label
        distance = abs(value - budget)  # Calculate the absolute difference
        budget_point.append((label, distance))
    # Sort the budget_point in ascending order
    budget_point.sort(key=lambda z: z[1])
    # Get the label and value for the nearest neighbor
    nearest_budget_label = budget_point[0][0]
    print("Nearest Label and Value for Input Budget:")
    print(f"Budget: {budget}, Label: {nearest_budget_label}")

    runtime_point = []
    for val in data:
        value = val[2]  # runtime value
        label = val[5]  # runtime label
        distance = abs(value - runtime)  # Calculate the absolute difference
        runtime_point.append((label, distance))
    # Sort the runtime_point in ascending order
    runtime_point.sort(key=lambda z: z[1])
    # Get the label and value for the nearest neighbor
    nearest_runtime_label = runtime_point[0][0]
    print("Nearest Label and Value for Input runtime:")
    print(f"runtimet: {runtime}, Label: {nearest_runtime_label}")

    average_point = (nearest_runtime_label+nearest_budget_label+rating)/3
    print(average_point)

    distances = []
    for row in data:
        distance = abs(row[6] - average_point)
        distances.append((row[6], distance))

        # Get the top 5 nearest neighbors
    distances.sort(key=lambda x: x[1])
    top_5_nearest = distances[:5]

    # Calculate the average profit of the top 5 nearest neighbors
    total_profit = 0
    for row in top_5_nearest:
        index = int(row[0])
        total_profit += data[index][3]
        print(total_profit)
    print(total_profit)
    predicted_gross = total_profit / 5

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
    budget_ticks = [tick / 1000000 for tick in plt.xticks()[0]]
    gross_ticks = [tick / 1000000 for tick in plt.yticks()[0]]
    plt.xticks(plt.xticks()[0], ['${:.1f}M'.format(tick) for tick in budget_ticks])
    plt.yticks(plt.yticks()[0], ['${:.2f}M'.format(tick) for tick in gross_ticks])

    # Plot the regression line
    plt.plot(budget, predicted_gross, 'r-', label='Regression Line')
    plt.show()

def menu():
    # Connect to the database
    mydb = connect_database()
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

menu()


'''
#test data
genre = ("Action")
budget = 1000000
rating = 7.5
runtime = 120


genre = ("Science Fiction")
budget = 10000000
rating = 8
runtime = 120
'''


