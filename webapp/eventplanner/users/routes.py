from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify, g
from flask_login import login_user, current_user, logout_user, login_required
from eventplanner import db, bcrypt, auth, csrf
from eventplanner.models import User, Event, Role, UserRoles, UserBookings
from eventplanner.users.forms import (
    RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, ManagerRegistrationForm)
from eventplanner.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()

    # we see that the post actually worked, we use a flash message to confirm it
    if form.validate_on_submit():
        # success is a bootstrap argument
        # we hash the password inserted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        user.roles.append(Role(name='SimpleUser'))
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you can now log in', 'success')
        return redirect(url_for('main.home'))  # name of the function

    return render_template('register.html', title='Register', form=form)


@users.route("/register/manager/", methods=['GET', 'POST'])
def register_manager():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ManagerRegistrationForm()

    # we see that the post actually worked, we use a flash message to confirm it
    if form.validate_on_submit():
        # success is a bootstrap argument
        # we hash the password inserted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        user.roles.append(Role(name='Manager'))
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you can now log in', 'success')
        return redirect(url_for('users.login'))  # name of the function

    return render_template('register_manager.html', title='Register', form=form)


@users.route("/login/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # log in the user
            # if the remember me box is checked
            login_user(user, remember=form.remember.data)
            # args is a dictionary, don't access using key would give error, use get
            next_page = request.args.get('next')
            print("next page is: ",next_page)
            if next_page == '/start-payment-flow':
                return redirect(url_for('main.home'))
            if next_page == '/generate-booking/':
                return redirect(url_for('main.home'))


            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('login failed, check email and password', 'danger')
            return redirect(url_for('main.home'))
    return render_template('login.html', title='Login', form=form)


@users.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/account-info/", methods=['GET'])
#@login_required
def account_info():
    return render_template("account_info.html")


# @users.route("/user/<string:username>")
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     # passing an argument to a template
#     # we want to paginate them
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_posts.html', posts=posts, user=user)


@users.route("/user/<string:username>")
def user_events(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    # passing an argument to a template
    # we want to paginate them
    events = Event.query.filter_by(manager=user)\
        .order_by(Event.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_events.html', events=events, user=user)

# to see the tickets bought by a user


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or exiperd token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # success is a bootstrap argument
        # we hash the password inserted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, you can now log in', 'success')
        return redirect(url_for('users.login'))  # name of the function
    return render_template('reset_token.html', title='Reset Password', form=form)


# ######### API #########

# # @users.route("/api/login", methods=['POST'])
# # def api_login():

# #     # to login i need email and password

# #     if current_user.is_authenticated:
# #         return redirect(url_for('main.home'))
# #     form = LoginForm()
# #     if form.validate_on_submit():
# #         user = User.query.filter_by(email=form.email.data).first()
# #         if user and bcrypt.check_password_hash(user.password, form.password.data):
# #             # log in the user
# #             # if the remember me box is checked
# #             login_user(user, remember=form.remember.data)
# #             # args is a dictionary, don't access using key would give error, use get
# #             next_page = request.args.get('next')

# #             return redirect(next_page) if next_page else redirect(url_for('main.home'))
# #         else:
# #             flash('login failed, check email and password', 'danger')
# #     return render_template('login.html', title='Login', form=form)

# # hashed_password = bcrypt.generate_password_hash(
# #             form.password.data).decode('utf-8')
# #         user = User(username=form.username.data,
# #                     email=form.email.data, password=hashed_password)
# #         db.session.add(user)
# #         db.session.commit()

# @users.route('/api/register', methods=['POST'])
# def api_register():
#     username = request.json.get('username')
#     email = request.json.get('email')
#     password = request.json.get('password')
#     confirm_password = request.json.get('confirm_password')
#     if username is None or password is None or confirm_password is None:
#         abort(400)  # missing arguments
#         # different error types
#     if User.query.filter_by(username=username).first() is not None:
#         abort(400)  # existing user
#         hashed_password = bcrypt.generate_password_hash(
#             password).decode('utf-8')
#         user = User(username=username,
#                     email=email, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#     return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}


# @users.route('/api/users/<int:id>')
# def get_user(id):
#     user = User.query.get(id)
#     if not user:
#         abort(400)
#     return jsonify({'username': user.username})


# @users.route('/api/token')
# @auth.login_required
# def get_auth_token():
#     token = g.user.generate_auth_token()
#     return jsonify({'token': token.decode('utf-8')})  # was ascii before


# @auth.verify_password
# def verify_password(username_or_token, password):
#     # first try to authenticate by token
#     user = User.verify_auth_token(username_or_token)
#     if not user:
#         # try to authenticate with username/password
#         user = User.query.filter_by(username=username_or_token).first()
#         if not user or not user.verify_password(password):
#             return False
#     g.user = user
#     return True


# @auth.verify_password
# # https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
# # In token-based authentication, the client sends
# # the login credentials to a special URL that generates
# # authentication tokens. Once the client has a token
# # it can use it in place of the login credentials
# # to authenticate requests. For security reasons,
# # tokens are issued with an associated expiration.
# # The generate_auth_token() method returns a signed
# # token that encodes the user’s id field.
# # An expiration time given in seconds is also used.
# # The verify_auth_token() method takes a token and,
# # if found valid, it returns the user stored in it.
# # This is a static method, as the user will be known
# # only after the token is decoded.
# # To authenticate requests that come with a token,
# # the verify_password callback for Flask-HTTPAuth
# # must be modified to accept tokens as well as
# # regular credentials.
