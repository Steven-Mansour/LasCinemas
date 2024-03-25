from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify
from authMod.auth import auth_blueprint  # Import the auth blueprint
from flask_bcrypt import Bcrypt  # for hashing
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from DB import DB_ops, OMDBApi, YTAPI
from flask_mail import Mail, Message
import random



app = Flask(__name__)
app.register_blueprint(auth_blueprint)
app.config.update(auth_blueprint.config)
auth_blueprint.mail.init_app(app)

app.config['SECRET_KEY'] = "aljkdgba;kjbdsadsa"
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "" #Insert an email eg. person@outlook.com
app.config['MAIL_PASSWORD'] = "" #Insert your email password
app.config['MAIL_DEFAULT_SENDER'] = "" #Re Insert your email
mail = Mail(app)


@app.route("/")
def fct():
    return redirect(url_for("auth.login"))


@app.route("/delete_screening", methods=["POST", "GET"])
def delete_screening():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    screeningID = request.form.get('form_id')
    print("ID")
    print(screeningID)
    DB_ops.delete_screening(screeningID)
    return redirect(url_for('manage_screenings'))


@app.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    session['balance'] = DB_ops.find_balance(username)
    balance = session['balance']
    info = {
    'total_reviews': DB_ops.get_total_reviews(),
    'total_clients': DB_ops.get_total_clients(),
    'total_movies_displayed': DB_ops.get_total_movies_displayed(),
}
    
    return render_template("home.html", username=username, balance=balance, info = info)


@app.after_request
def add_no_cache_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/reserve_seat", methods=["POST", "GET"])
def reserve_seat():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    screeningID = session['screeningID']
    seatID = request.form.get('form_id')
    balance = DB_ops.find_balance(username)
    price = 4
    newBalance = DB_ops.deduct_balance(price, username)
    DB_ops.create_ticket(seatID, screeningID, username)
    if newBalance < 0:
        newBalance = balance
    session['balance'] = newBalance
    return redirect(url_for('seats'))


@app.route("/seats", methods=["POST", "GET"])
def seats():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    balance = session['balance']
    if request.method =='POST':
        screeningID = request.form.get('form_id')
        session['screeningID'] = screeningID
    else:
       screeningID = session['screeningID'] 
    seats = DB_ops.get_all_seats_for_screening(screeningID)
    takenSeats = DB_ops.get_reserved_seats_for_screening(screeningID)
    price = 4
    return render_template("seats.html", allSeats=seats, takenSeats=takenSeats, username=username, balance=balance, price=price)


@app.route("/about_us")
def about_us():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template("about_us.html", username=session['username'], balance=session['balance'])


@app.route("/admin_home", methods=['GET', 'POST'])
def admin_home():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    return render_template("admin_home.html", name=session['admin'])

# add movie to DB using movie title


@app.route('/get_suggestions')
def get_suggestions():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    query = request.args.get('query')
    suggestions = get_matching_suggestions(query)
    return jsonify(suggestions)


@app.route('/upload_review', methods=["POST", "GET"])
def upload_review():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    movie = request.form.get('movieName')
    print(movie)
    movie = DB_ops.get_ID_from_title(movie)
    review = request.form.get('reviewText')
    username = session['username']
    DB_ops.insret_review(username, movie, review)
    return redirect(url_for('reviews'))


@app.route('/get_usernames')
def get_usernames():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    query = request.args.get('query')
    usernames = get_matching_usernames(query)
    return jsonify(usernames)


def get_matching_usernames(query):
    usernames = DB_ops.list_all_usernames()
    return [username[0] for username in usernames if query.lower() in username[0].lower()]


def get_matching_suggestions(query):
    movies = DB_ops.list_all_movies()
    return [movie[0] for movie in movies if query.lower() in movie[0].lower()]

# add movie to DB using title


@app.route("/addMovie", methods=['GET', 'POST'])
def addMovie():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    if request.method == 'POST':
        title = request.form['movieTitle']
        movie_info = OMDBApi.get_movie_info(title)
        if movie_info is not None:
            title = movie_info[1]
            trailerLink = YTAPI.get_movie_trailer(title)
            movie_info.append(trailerLink)
            DB_ops.insert_movie(movie_info)
            success_message = f"{title} added successfully!"
            return render_template('admin_home.html', success_message=success_message, name=session['admin'])
        error_message = f"Movie with title '{title}' not found"
        return render_template('admin_home.html', error_message=error_message, name=session['admin'])
    return redirect(url_for('admin_home'))

# add movie to DB using IMDBID


@app.route("/addMovieUsingImdbId", methods=['GET', 'POST'])
def addMovieUsingImdbId():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    if request.method == 'POST':
        id = request.form['movieID']
        movie_info = OMDBApi.get_movie_info_by_imdb_id(id)
        if movie_info is not None:
            title = movie_info[1]
            trailerLink = YTAPI.get_movie_trailer(title)
            movie_info.append(trailerLink)
            DB_ops.insert_movie(movie_info)
            success_message = f'{movie_info[1]} added successfully!'
            return render_template('admin_home.html', success_message=success_message, name=session['admin'])
        error_message = f"Movie with id '{id}' not found"
        return render_template('admin_home.html', error_message=error_message, name=session['admin'])
    return redirect(url_for('admin_home'))

# add screening to DB using movie title


@app.route("/createScreeningUsingIMDBID", methods=['GET', 'POST'])
def createScreeningUsingIMDBID():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    if request.method == 'POST':
        operatorID = session['admin']
        movieTitle = request.form['screeningMovieTitle']
        IMDBID = DB_ops.get_ID_from_title(movieTitle)
        error_message = ""
        if IMDBID is None:
            error_message = f'{movieTitle} not found in the database.'
        else:
            room = request.form['room']
            startTime = request.form['startTime']
            date = request.form['date']
            numberOfScreeningDays = request.form['numberOfScreeningDays']

            # Check if the screening already exists
            if DB_ops.is_screening_duplicate(IMDBID, room, startTime, date):
                error_message = f'A screening for {movieTitle} at {startTime} on {date} in room {room} already exists.'
                # error_message = 'Duplicate screening found.'
                return render_template('admin_home.html', error_message=error_message, name=session['admin'])
            else:
                movie_info = DB_ops.check_movie_details(IMDBID)
                if movie_info:
                    error_message = DB_ops.insert_screening(
                        IMDBID, room, startTime, date, numberOfScreeningDays, operatorID)
                    if error_message:
                        return render_template('admin_home.html', error_message=error_message, name=session['admin'])
                    else:
                        success_message = f'Screening for {movieTitle} added successfully!'
                        return render_template('admin_home.html', success_message=success_message, name=session['admin'])
                else:
                    error_message = f'Movie details not found for IMDb ID: {movieTitle}'

        return render_template('admin_home.html', error_message=error_message, name=session['admin'])
    return redirect(url_for('admin_home'))

# Delete screenings for admin


@app.route("/manage_screenings")
def manage_screenings():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    screenings = DB_ops.list_screenings_and_operator()
    return render_template('manage_screenings.html', screenings=screenings)

# update balance of user and DB
@app.route('/updateBalance', methods=['GET', 'POST'])
def updateBalance():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    if request.method == 'POST':
        username = request.form['username']
        balance_str = request.form['balance']
        if balance_str:  # Check if not empty
            difference = int(balance_str)
            operatorID = session['admin']
            userExists = DB_ops.check_if_username_exists(username)
            if userExists:
                DB_ops.update_balance(username, difference, operatorID)
                if difference > 0:
                    alert_message = f"${difference} added to {username}'s balance"
                elif difference < 0:
                    alert_message = f"${abs(difference)} removed from {username}'s balance"
                else:
                    alert_message = "No change in balance"
                return render_template('admin_home.html', success_message=alert_message, name=session['admin'])
            return render_template('admin_home.html', error_message='User not found', name=session['admin'])
    return render_template('admin_home.html')


@app.route("/screenings", methods=['GET', 'POST'])
def screenings():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    movies_info = DB_ops.get_all_movies_info()
    return render_template("screenings.html", username=username, balance=session['balance'], movies_info=movies_info)


# update history of user and DB

@app.route('/history', methods=['GET', 'POST'])
def history():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    balance_data = DB_ops.get_history(username)
    return render_template('history.html', username=username, balance=session['balance'], transaction_history=balance_data)


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    movie_name = request.args.get('movie', '').lower()
    reviews = DB_ops.list_all_reviews()
    if movie_name:
        filtered_reviews = [
            review for review in reviews if movie_name in review['title'].lower()]
    else:
        filtered_reviews = reviews

    return jsonify(filtered_reviews)


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    review_list = DB_ops.list_recent_reviews()
    movies = DB_ops.list_all_movies()
    return render_template('reviews.html', username=session['username'], balance=session['balance'], reviews=review_list, movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
