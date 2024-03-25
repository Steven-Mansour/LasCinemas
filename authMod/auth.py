
from flask import Blueprint, render_template, request, redirect, url_for
from flask import flash, session, make_response, jsonify, current_app
from flask_bcrypt import Bcrypt  # for hashing
from DB import DB_ops
from flask_mail import Mail, Message
import threading
import string
import secrets
from datetime import datetime, timedelta

bcrypt = Bcrypt()

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

auth_blueprint.config = {
    'SECRET_KEY': "aljkdgba;kjbdsadsa",
    'MAIL_SERVER': 'smtp.office365.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': "", #Insert an email eg. person@outlook.com
    'MAIL_PASSWORD': "", #Insert your email password
    'MAIL_DEFAULT_SENDER': "" #Re Insert your email
}

auth_blueprint.mail = Mail()


def generate_token(length=5):
    alphanumeric_chars = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphanumeric_chars) for _ in range(length))
    return token


@auth_blueprint.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        flag = DB_ops.check_if_username_exists(username)
        if not flag:
            flash('Username not found')
            return redirect(url_for('auth.forgot_password'))
        session['fPUsername'] = username
        return redirect(url_for('auth.verify_token'))
    return render_template("forgot_password.html")


def send_signup_email_async(app, email, username):
    with app.app_context():
        auth_blueprint.mail.init_app(app)

        subject = 'Account Creation'
        body = f"""Dear {username}, 
        
        \n🍿 Welcome to Las Cinemas! 🎬 We are thrilled to have you join our cinematic family, where the magic of movies comes to life!

       \nAt Las Cinemas, we believe in creating extraordinary experiences, and we are delighted that you've chosen us to be part of your movie-watching journey. Get ready for a world of blockbuster entertainment, exclusive screenings, and a front-row seat to the latest cinematic wonders!

       \nHere's a glimpse of what awaits you:

        \n🎁 Personalized Recommendations:
        \nOur team is dedicated to curating a personalized movie-watching experience just for you. From heartwarming dramas to pulse-pounding thrillers, we've got it all. Your next favorite film is just a click away!

        \n🎉 Exciting Events and Contests:
        \nBe on the lookout for our exciting events and contests. Win fabulous prizes, meet fellow movie enthusiasts, and immerse yourself in the vibrant Las Cinemas community.

        \n🤩 Sneak Peeks and Behind-the-Scenes Access:
        \nGet an insider's look at the movie-making magic with exclusive behind-the-scenes content and sneak peeks. You're in for a treat as we bring you closer to the world of cinema.

        \n📅 Stay Tuned for Upcoming Blockbusters:
        \nKeep an eye on your inbox for updates on upcoming blockbusters, special releases, and themed movie nights. We've got a lineup that will keep you on the edge of your seat!

        \nFeel free to explore our website, discover hidden gems in our extensive movie library, and make yourself at home. If you have any questions or need assistance, our friendly support team is just a message away.

        \nOnce again, welcome to Las Cinemas! 🎉 Let the cinematic adventure begin!

        \nLights, Camera, Action!

        \nWarm regards,

        \nLas Cinemas Team 🎥✨ """

        message = Message(subject, recipients=[email], body=body)

        # Send the email without printing unnecessary information to the console
        with auth_blueprint.mail.connect() as conn:
            conn.send(message)


def send_confirm_reset_email_async(app, email, username):
    with app.app_context():
        auth_blueprint.mail.init_app(app)

        subject = 'Password Updated Notice'
        body = f'Dear {username}, \nKindly be informed that your password has been changed. If you did not change it, we highly advise you to try changing it right now! '

        message = Message(subject, recipients=[email], body=body)

        # Send the email without printing unnecessary information to the console
        with auth_blueprint.mail.connect() as conn:
            conn.send(message)


def send_reset_email_async(app, email, token, username):
    with app.app_context():
        auth_blueprint.mail.init_app(app)

        subject = 'Password Reset Request'
        body = f'To reset your password for account "{username}", kindly use the following token: {token} '

        message = Message(subject, recipients=[email], body=body)

        # Send the email without printing unnecessary information to the console
        with auth_blueprint.mail.connect() as conn:
            conn.send(message)


@auth_blueprint.route("/verify_token", methods=['GET', 'POST'])
def verify_token():
    if 'fPUsername' in session:
        username = session['fPUsername']
        flag = DB_ops.check_if_username_exists(username)
        if flag:
            email = DB_ops.find_email(username)
            # Set expiration time for the token (5 minutes from now)
            expiration_time = datetime.now() + timedelta(minutes=5)
            token = generate_token(5)
            token_thread = threading.Thread(target=send_reset_email_async, args=(
                current_app._get_current_object(), email, token, username))
            token_thread.start()
            return render_template('verifyToken.html', token=token, expiration_time=expiration_time)
        flash('No matching username was found')
        return redirect(url_for('auth.forgot_password'))
    else:
        return redirect(url_for('auth.forgot_password'))

# Function to hash a password


def hash_password(password):
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Store the hashed password in your database

    return hashed_password

# Function to verify a password


@auth_blueprint.route("/check_token", methods=['POST'])
def check_token():

    data = request.json
    entered_password = data.get('password')
    hashed_password = data.get('hashedPassword')

    # Your existing verify_password method
    is_valid = verify_password(entered_password, hashed_password)

    return jsonify({'isValid': is_valid})


@auth_blueprint.route('/change_password', methods=['POST', 'GET'])
def change_password():
    return render_template("change_password.html")


def verify_password(password, hashed_password):
    # Retrieve the hashed password from your database
    stored_hashed_password = hashed_password
    # Verify the entered password against the hashed password
    if bcrypt.check_password_hash(stored_hashed_password, password):
        return True
    else:
        return False


@auth_blueprint.route('/update_password', methods=['GET', 'POST'])
def update_password():
    successfully_changed_pass = ""
    if 'fPUsername' in session:
        username = session['fPUsername']
        password = request.form['password']
        password = hash_password(password)
        DB_ops.change_client_password(username, password)
        print("password changed")
        email = DB_ops.find_email(username)
        token_thread = threading.Thread(target=send_confirm_reset_email_async, args=(
            current_app._get_current_object(), email, username))
        token_thread.start()
        successfully_changed_pass = "You Have Successfully Changed Your Password"

    return redirect(url_for('auth.login', message = successfully_changed_pass))


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    change_password_str = request.args.get('message', '')
    session.clear()
    str = "Your credentials are wrong!"
    session['msg'] = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        flag1 = DB_ops.check_if_username_exists(username)
        if not flag1:
            session['msg'] = str
            return render_template("login.html", msg=session['msg'])

        flag2 = verify_password(password, DB_ops.find_password(username))
        if not flag2:
            session['msg'] = str
            return render_template("login.html", msg=session['msg'])
        session['username'] = username
        return redirect(url_for('home'))

    return render_template("login.html", msg=session['msg'], password_status = change_password_str)


@auth_blueprint.route("/signup", methods=['GET', 'POST'])
def sign_up():
    session['msg'] = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['verifyPassword']
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        flag = DB_ops.check_if_username_exists(username)
        if flag:
            session['msg'] = ("Username already taken")
        elif password != password2:
            session['msg'] = ("Passwords do not match")
        else:
            DB_ops.insert_client(username, fname, lname,
                                 hash_password(password), email)

            thread = threading.Thread(target=send_signup_email_async, args=(
                current_app._get_current_object(), email, username))
            thread.start()
            return render_template("login.html", msg="You have successfully created a new account")

    return render_template("signup.html", msg=session['msg'])


@auth_blueprint.route("/check_username_availability", methods=['POST'])
def check_username_availability():
    username = request.form['username']
    username_exists = DB_ops.check_if_username_exists(username)
    return jsonify({'exists': username_exists})


@auth_blueprint.route("/logout", methods=['GET', 'POST'])
def logout():
    # Clear session variables
    session.clear()
    response = make_response(render_template('login.html'))

    return response


@auth_blueprint.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    session.clear()
    str = "Your credentials are wrong!"
    session['msg'] = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if DB_ops.check_if_admin_exists(username):
            flag2 = verify_password(
                password, DB_ops.find_admin_password(username))
            if not flag2:
                session['msg'] = str
                return render_template("admin_login.html", msg=session['msg'])
            session['admin'] = username
            return redirect(url_for("admin_home"))
        session['msg'] = str

    return render_template("admin_login.html", msg=session['msg'])
