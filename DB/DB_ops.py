from flask import flash
import mysql.connector
from datetime import datetime, timedelta, date

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "0000",
    "database": "cinemaDB"
}


def get_all_movies_info():
    connection = mysql.connector.connect(**db_config)
    # Use dictionary=True to get results as dictionaries
    cursor = connection.cursor(dictionary=True)
    query = """ 
        SELECT title, duration, genre, actors, poster, rating, description, trailerLink, startTime, date, pg, S.screeningID FROM MOVIE M, SCREENING S 
        WHERE M.movieID = S.movieID AND S.date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 6 DAY)
        ORDER BY S.date, S.startTime
    """
    cursor.execute(query)
    movies_info = cursor.fetchall()
    cursor.close()
    connection.close()
    return movies_info
# the results is returned as dictionaries, where column names are used as keys.


def change_client_password(username, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """UPDATE CLIENT SET password = %s WHERE username = %s ;"""
    cursor.execute(query, (password, username,))
    connection.commit()
    cursor.close()
    connection.close()
    return


def check_if_username_exists(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """SELECT COUNT(username) FROM CLIENT WHERE username = %s; """
    cursor.execute(query, (username,))
    occurence = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return occurence >= 1


def check_if_admin_exists(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """SELECT COUNT(username) FROM OPERATOR WHERE username = %s; """
    cursor.execute(query, (username,))
    occurence = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return occurence == 1


def find_balance(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT balance FROM CLIENT WHERE username = %s; """
    cursor.execute(query, (username,))
    balance = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return balance


def list_all_usernames():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT username FROM CLIENT"""
    cursor.execute(query)
    usernames = cursor.fetchall()
    cursor.close()
    connection.close()
    return usernames


def list_all_movies():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT title FROM MOVIE ORDER BY releaseDate DESC """
    cursor.execute(query)
    movies = cursor.fetchall()
    cursor.close()
    connection.close()
    return movies


def find_password(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT password FROM CLIENT WHERE username = %s; """
    cursor.execute(query, (username,))
    password = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return password


def insert_client(username, firstname, lastname, password, email):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ INSERT INTO CLIENT (username, firstname, lastname, password, email, balance)
            VALUES (%s, %s, %s, %s, %s, %s); """
    cursor.execute(query, (username, firstname, lastname, password, email, 0))
    connection.commit()
    cursor.close()
    connection.close()


def find_email(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT email FROM CLIENT WHERE username = %s; """
    cursor.execute(query, (username,))
    email = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return email


def find_admin_password(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT password FROM OPERATOR WHERE username = %s; """
    cursor.execute(query, (username,))
    password = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return password


def insert_movie(movie_info):
    if movie_info is None:
        print("Error: movie_info is None. Skipping insertion.")
        return

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """INSERT INTO MOVIE (movieID, title, duration, releaseDate, genre, actors, poster, rating, description, pg, trailerLink)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    try:
        cursor.execute(query, movie_info)
        connection.commit()
    except Exception as e:
        print(f"Error inserting movie: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def get_ID_from_title(movieTitle):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT movieID FROM MOVIE WHERE title = %s;'
    cursor.execute(query, (movieTitle,))
    movie_ID = cursor.fetchone()
    connection.close()
    if movie_ID is not None:
        return movie_ID[0]
    else:
        return None


def check_movie_details(movieID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT * FROM MOVIE WHERE movieID = %s;'
    cursor.execute(query, (movieID,))
    movie_details = cursor.fetchone()
    connection.close()
    return movie_details is not None


def delete_screening(screeningID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = 'DELETE FROM OPERATOR_SCREENING WHERE screeningID = %s;'
    cursor.execute(query, (screeningID,))
    connection.commit()
    query = 'DELETE FROM CORRESPONDS_TO WHERE screeningID = %s;'
    cursor.execute(query, (screeningID,))
    connection.commit()
    query = 'DELETE FROM SCREENING WHERE screeningID = %s;'
    cursor.execute(query, (screeningID,))
    connection.commit()
    connection.close()
    return


def list_recent_reviews():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = '''SELECT username, title, review, timestamp FROM REVIEW R, MOVIE M
    WHERE R.movieID = M.movieID ORDER BY timestamp DESC LIMIT 10;'''
    cursor.execute(query)
    reviews = cursor.fetchall()
    connection.close()
    if reviews is not None:
        return reviews
    else:
        return None


def list_all_reviews():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = '''SELECT username, title, review, timestamp FROM REVIEW R, MOVIE M
    WHERE R.movieID = M.movieID ORDER BY timestamp DESC;'''
    cursor.execute(query)
    reviews = cursor.fetchall()
    connection.close()
    if reviews is not None:
        return reviews
    else:
        return None


def insret_review(username, movie, review):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    current_datetime = datetime.now()
    query = """ INSERT INTO REVIEW (username, movieID, review, timestamp)
            VALUES (%s, %s, %s, %s); """
    cursor.execute(query, (username, movie, review, current_datetime,))
    connection.commit()
    cursor.close()
    connection.close()
    return


def list_screenings_and_operator():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    current_date = date.today()
    query = """
       SELECT title, date, startTime, roomNb, operations, operatorID, poster, s.screeningID, COUNT(c.ticketID) AS reserved
        FROM operator_screening os LEFT JOIN screening s ON os.screeningID = s.screeningID LEFT JOIN movie m ON s.movieID = m.movieID
        LEFT JOIN corresponds_to c ON c.screeningID = s.screeningID WHERE s.date >= %s
        GROUP BY title, date, startTime, roomNb, operations, operatorID, poster, s.screeningID;"""
    cursor.execute(query, (current_date,))
    screenings = cursor.fetchall()
    connection.close()
    return screenings


def insert_screening(movieID, roomNb, startTime, date, numberOfScreeningDays, operatorID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    numberOfScreeningDays = int(numberOfScreeningDays)
    action = "Created"
    error_message = ""

    for day in range(numberOfScreeningDays):
        screening_date = (datetime.strptime(date, '%Y-%m-%d') +
                          timedelta(days=day)).strftime('%Y-%m-%d')

        # Check if the screening date is before the current date
        screening_date_obj = datetime.strptime(
            screening_date, "%Y-%m-%d").date()
        current_date_obj = datetime.now().date()
        if screening_date_obj < current_date_obj:
            error_message = 'Screening date should be in the future.'
            return error_message

        available_slots = get_available_time_slots(screening_date, roomNb)

        # Check if the room is available at the specified time on the given date
        if not is_room_available(roomNb, screening_date, startTime):
            error_message = f'Room {roomNb} is not available at {startTime} on {screening_date}.'
            return error_message

        # if the day is full
        if not available_slots:
            error_message = f'No available time slots for {screening_date}.'
            return error_message

        # if movie duration more than 4 hours, it just fits in 22:00:00 timeslot
        movie_duration = get_movie_duration(movieID)
        if movie_duration != None:
            if movie_duration > timedelta(hours=4) and startTime != '22:00:00':
                error_message = f'The movie does not fit at {startTime}.'
                return error_message

        if not is_room_available(roomNb, screening_date, startTime) and startTime not in available_slots:
            error_message = f'Start time {startTime} is not available for {screening_date}.'
            return error_message

        else:
            query = '''
                INSERT INTO SCREENING (startTime, date, roomNb, movieID)
                VALUES (%s, %s, %s, %s);
            '''
            values = (startTime, screening_date, roomNb, movieID)
            try:
                cursor.execute(query, values)
                connection.commit()
                last_inserted_id = cursor.lastrowid
                insert_operator_action(operatorID, last_inserted_id, action)
            except Exception as e:
                connection.rollback()
                error_message = f'Error adding screening on {screening_date} at {startTime}: {str(e)}'

    connection.close()
    return error_message


def get_all_seats_for_screening(screeningID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    current_date = date.today()
    query = """
        SELECT seatID FROM seat WHERE roomNb IN (SELECT roomNb FROM SCREENING WHERE screeningID = %s) ORDER BY seatID ASC;  
    """
    cursor.execute(query, (screeningID,))
    seats = cursor.fetchall()
    connection.close()
    return seats


def create_ticket(seatID, screeningID, username):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        current_date = date.today()
        price = 4
        query = """
            INSERT INTO TICKET (price, purchaseDate, username)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (price, current_date, username,))
        connection.commit()
        ticket = cursor.lastrowid
        connection.close()
        reserve_seat(seatID, screeningID, ticket)
        print(f"Ticket created successfully. Ticket ID: {ticket}")

    except Exception as e:
        print(f"Error creating ticket: {str(e)}")


def reserve_seat(seatID, screeningID, ticket):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = """
            INSERT INTO CORRESPONDS_TO (ticketID, screeningID, seatID)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (ticket, screeningID, seatID,))
        connection.commit()
        connection.close()
        print("Seat reserved successfully.")

    except Exception as e:
        print(f"Error reserving seat: {str(e)}")


def get_reserved_seats_for_screening(screeningID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    current_date = date.today()
    query = """
        SELECT seatID FROM seat WHERE roomNb IN (SELECT roomNb FROM SCREENING WHERE screeningID = %s)
          AND seatID IN (SELECT seatID FROM CORRESPONDS_TO WHERE screeningID = %s) ORDER BY seatID ASC;  
    """
    cursor.execute(query, (screeningID, screeningID, ))
    seats = cursor.fetchall()
    connection.close()
    return seats


def insert_operator_action(operatorID, screeningID, action):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """INSERT INTO operator_screening (screeningID, operatorID, operations)
               VALUES (%s, %s, %s);"""
    try:
        cursor.execute(query, (screeningID, operatorID, action))
        connection.commit()
    except Exception as e:
        print(f"Error inserting movie: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    return


def get_available_time_slots(screening_date, roomNb):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT startTime
        FROM SCREENING
        WHERE date = %s AND roomNb = %s;
    """
    cursor.execute(query, (screening_date, roomNb,))
    taken_time_slots = [str(row[0]) for row in cursor.fetchall()]
    connection.close()
    # Fixed timeslots availables
    available_time_slots = ['14:00:00', '18:00:00', '22:00:00']
    available_time_slots = [
        slot for slot in available_time_slots if slot not in taken_time_slots]
    return available_time_slots


def get_movie_duration(movieID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT duration
        FROM MOVIE
        WHERE movieID = %s;
    """
    cursor.execute(query, (movieID,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    else:
        return None


def is_room_available(roomNb, screening_date, startTime):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT *
        FROM SCREENING
        WHERE roomNb = %s AND date = %s AND startTime = %s;
    """
    cursor.execute(query, (roomNb, screening_date, startTime))
    result = cursor.fetchone()
    connection.close()
    return result is None  # Room is available if no screening is found at the specified time


def is_screening_duplicate(movieID, roomNb, startTime, date):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT *
        FROM SCREENING
        WHERE movieID = %s AND roomNb = %s AND startTime = %s AND date = %s;
    """
    cursor.execute(query, (movieID, roomNb, startTime, date))
    result = cursor.fetchone()
    connection.close()
    return result is not None

# def determine_screening_time(movie_duration, available_slots):
#     if movie_duration > timedelta(hours=4):
#         return '22:00:00'
#     else:
#         return available_slots[0]

def get_total_movies_displayed():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT COUNT(DISTINCT (movieID)) FROM SCREENING; """
    cursor.execute(query,)
    movies_displayed = cursor.fetchone()[0]
    connection.close()
    return movies_displayed
    
def get_total_clients():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT COUNT(username) FROM CLIENT; """
    cursor.execute(query,)
    total_clients = cursor.fetchone()[0]
    connection.close()
    return total_clients

def get_total_reviews():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT COUNT(*) FROM REVIEW; """
    cursor.execute(query,)
    total_reviews = cursor.fetchone()[0]
    connection.close()
    return total_reviews

def deduct_balance(price, username):
    balance = find_balance(username)
    newBalance = balance - price
    if newBalance >= 0:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = """ UPDATE CLIENT SET balance = %s  WHERE username = %s; """
        cursor.execute(query, (newBalance,username,))
        connection.commit()
        connection.close()
        return newBalance
    return balance


def update_balance(username, difference, operatorID):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """ SELECT balance FROM CLIENT WHERE username = %s; """
    cursor.execute(query, (username,))
    balance = cursor.fetchone()[0]
    difference = int(difference)
    new_balance = balance+difference
    if new_balance > 0:
        query_balance = """UPDATE CLIENT SET balance = %s WHERE username = %s;"""
        cursor.execute(query_balance, (new_balance, username))
        connection.commit()
        print("Balance updated successfully")
        query_history = """INSERT INTO BALANCE (username, operatorID, updated, difference)
                VALUES (%s, %s, %s, %s);"""
        current_time = datetime.now()
        cursor.execute(query_history, (username, operatorID,
                       current_time, difference))
        connection.commit()
        print("History updated successfully")
        cursor.close()
        connection.close()
    print("Error: Credits not enough. Balance not updated.")
    new_balance = balance-difference
    return balance


def get_history(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT * FROM balance WHERE username=%s;'
    cursor.execute(query, (username,))
    balance_data = cursor.fetchall()
    connection.close()
    return balance_data
