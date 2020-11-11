import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import check_password_hash, generate_password_hash

from tarpeydev.db import get_users

bp = Blueprint('admin', __name__, url_prefix='/admin')
swag_bp = get_swaggerui_blueprint(
    '/swagger',
    'http://127.0.0.1:5000/static/swagger.json',
)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dbu, client = get_users()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not username.isalnum():
            error = 'Username must be alphanumeric.'
        elif not password.isalnum():
            error = 'Password must be alphanumeric.'
        elif (username != 'matt') & (username != 'annuitydew'):
            error = 'Registration is currently closed!'
        else:
            user = dbu.users.find_one({"_id": username})
            if user is not None:
                error = f'User {username} is already registered.'

        if error is None:
            dbu.users.insert_one({
                "_id": username,
                "password": generate_password_hash(password)
            })
            return redirect(url_for('admin.login'))

        flash(error)

    return render_template('admin/register.html')


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dbu, client = get_users()
        error = None
        user = dbu.users.find_one({"_id": username})

        if not username.isalnum():
            error = 'Username must be alphanumeric.'
        elif not password.isalnum():
            error = 'Password must be alphanumeric.'
        elif user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.get('password'), password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.get('_id')
            return redirect(url_for('swagger_ui.show'))
        
        flash(error)

    return render_template('admin/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        dbu, client = get_users()
        g.user = dbu.users.find_one({"_id": user_id})


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('admin.login'))

        return view(**kwargs)

    return wrapped_view


@swag_bp.before_request
def restrict_swagger():
    if g.user is None:
        return redirect(url_for('admin.login'))


@swag_bp.route('/adduser', methods=['POST'])
@login_required
def create():
    return


@swag_bp.route('/readuser/<username>', methods=['GET'])
@login_required
def read(username):
    dbu, client = get_users()
    user = dbu.users.find_one({"_id": username})
    if user is not None:
        return user
    else:
        return "Error!"


@swag_bp.route('/updateuser', methods=['POST', 'PUT'])
@login_required
def update():
    return


@swag_bp.route('/deleteuser', methods=['GET', 'DELETE'])
@login_required
def delete():
    return
