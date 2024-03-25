import mysql.connector

# 0000

# STEVEN db_config = {
#     "host": "127.0.0.1",
#     "user": "root",
#     "password": "0000",
#     "database": "cinemaDB"
# }

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "0000",
    "database": "cinemaDB"
}

# Establish a connection to the MySQL server
connection = mysql.connector.connect(**db_config)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Define the table creation query
table_creation_query = """
CREATE TABLE IF NOT EXISTS CLIENT (
    username VARCHAR(255) PRIMARY KEY COLLATE utf8mb4_bin,
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    password VARCHAR(255),
    email VARCHAR(255),
    balance INT
)
"""
# Execute the table creation query
cursor.execute(table_creation_query)
# Commit the changes
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    employeeID INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    phoneNb VARCHAR(11) 
)
"""
# assuming of the form 961 00 000 000 and lebanese
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS OPERATOR (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255), 
    email VARCHAR(255),
    employeeID INT AUTO_INCREMENT,
    FOREIGN KEY (employeeID) REFERENCES EMPLOYEE(employeeID) 
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS MOVIE (
    movieID VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    duration TIME,
    releaseDate DATE,
    genre VARCHAR(255),
    actors VARCHAR(255),
    poster VARCHAR(255),
    rating INT,
    pg VARCHAR(10),
    description VARCHAR(1000),
    trailerLink VARCHAR(255)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS ROOM (
    roomNb INT PRIMARY KEY,
    capacity INT
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS SCREENING (
    screeningID INT AUTO_INCREMENT PRIMARY KEY,
    startTime TIME,
    date DATE,
    roomNb INT,
    price decimal(6,2),
    movieID VARCHAR(255),
    FOREIGN KEY (roomNb) REFERENCES ROOM(roomNb),
    FOREIGN KEY (movieID) REFERENCES MOVIE(movieID) 
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS SEAT (
    seatID INT PRIMARY KEY,
    roomNb INT,
    FOREIGN KEY (roomNb) REFERENCES ROOM(roomNb)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS TICKET (
    ticketID INT AUTO_INCREMENT PRIMARY KEY,
    price INT,
    purchaseDate DATE,
    username VARCHAR(255) COLLATE utf8mb4_bin,
    FOREIGN KEY (username) REFERENCES CLIENT(username)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS REVIEW (
    username VARCHAR(255) COLLATE utf8mb4_bin,
    movieID VARCHAR(255),
    review TEXT,
    timestamp DATETIME,
    PRIMARY KEY (username, movieID, timestamp),
    FOREIGN KEY (username) REFERENCES CLIENT(username),
    FOREIGN KEY (movieID) REFERENCES MOVIE(movieID)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS BALANCE (
    username VARCHAR(255) COLLATE utf8mb4_bin,
    operatorID VARCHAR(255),
    updated DATETIME,
    difference INT,
    PRIMARY KEY (username, operatorID, updated),
    FOREIGN KEY (username) REFERENCES CLIENT(username),
    FOREIGN KEY (operatorID) REFERENCES OPERATOR(username)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS OPERATOR_SCREENING (
    screeningID INT AUTO_INCREMENT,
    operatorID VARCHAR(255),
    operations VARCHAR(255),
    PRIMARY KEY (screeningID, operatorID),
    FOREIGN KEY (screeningID) REFERENCES SCREENING(screeningID),
    FOREIGN KEY (operatorID) REFERENCES OPERATOR(username)
)
"""
cursor.execute(table_creation_query)
connection.commit()

table_creation_query = """
CREATE TABLE IF NOT EXISTS CORRESPONDS_TO (
    ticketID INT AUTO_INCREMENT,
    screeningID INT,
    seatID INT,
    PRIMARY KEY (screeningID, seatID),
    FOREIGN KEY (ticketID) REFERENCES TICKET(ticketID),
    FOREIGN KEY (screeningID) REFERENCES SCREENING(screeningID),
    FOREIGN KEY (seatID) REFERENCES SEAT(seatID)
)
"""
cursor.execute(table_creation_query)
connection.commit()

# Insert data into EMPLOYEE table
employee_data_to_insert = ("admin", "admin", "96100000000")
employee_insert_query = "INSERT INTO EMPLOYEE (firstName, lastName, phoneNb) VALUES (%s, %s, %s)"
cursor.execute(employee_insert_query, employee_data_to_insert)
connection.commit()

# Insert data into OPERATOR table
operator_data_to_insert = (
    "admin", "$2b$12$uKnYeRzYer5aJ5wE9imWfOQ/Z7Yi8VaJjRPXXMvuCNf4xzOH4OkAq", "admin@gmail.com", 1)
operator_insert_query = "INSERT INTO OPERATOR (username, password, email, employeeID) VALUES (%s, %s, %s, %s)"
cursor.execute(operator_insert_query, operator_data_to_insert)
connection.commit()



# Insert rooms in ROOM table
rooms_to_insert = [
    (1, 200),
    (2, 200),
    (3, 200),
    (4, 200),
]
for roomNb, capacity in rooms_to_insert:
    query = "INSERT INTO room (roomNb, capacity) VALUES (%s, %s);"
    values = (roomNb, capacity)
    cursor.execute(query, values)
    connection.commit()

# Inserting seats in SEAT table with the corresponding room number
seats_to_insert = []

for roomNb, capacity in rooms_to_insert:
    for seatID in range(1, capacity + 1):
        seat_number = seatID + (roomNb - 1) * 200
        seats_to_insert.append((seat_number, roomNb))

for seatID, roomNb in seats_to_insert:
    query = "INSERT INTO SEAT (seatID, roomNb) VALUES (%s, %s);"
    values = (seatID, roomNb)
    cursor.execute(query, values)
    connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()
