import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'
    elif db.execute(
      'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
      error = 'User {} is already registered.'.format(username)

    if error is None:
      db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        (username, generate_password_hash(password))
      )
      db.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
      error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
      error = 'Incorrect password.'

    if error is None:
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))

    flash(error)

  return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))


@bp.route('/<int:id>/user')
@login_required
def userpage(id):
  db = get_db()
  #idに対応する人の情報
  user = db.execute(
    'SELECT username'
    ' FROM user'
    ' WHERE id = ?',
    (id,)
  ).fetchone()
  #自分のカテゴリー
  #カテゴリーの編集
  #知り合いかも
  added_lists = db.execute(
    'SELECT host_id, username'
    ' FROM friend f JOIN user u ON f.host_id = u.id'
    ' WHERE guest_id = ?',
    (g.user['id'],)
  ).fetchall()
  
  add_lists = db.execute(
    'SELECT guest_id'
    ' FROM friend'
    ' WHERE host_id = ?',
    (g.user['id'],)
  ).fetchall()

  maybe_friends = []

  for added_list in added_lists:
    is_ok = True
    for add_list in add_lists:
      if add_list['guest_id'] == added_list['host_id']:
        is_ok = False
    if is_ok == True:
      maybe_friends.append(added_list)

  is_maybe_friend = False
  for maybe_friend in maybe_friends:
    if maybe_friend is not None:
      is_maybe_friend = True
  
  #友達追加の有無
  is_friend = True

  for add_list in add_lists:
    if add_list['guest_id'] == id:
      is_friend = False

  return render_template('auth/user.html', user=user, id=id, maybe_friends=maybe_friends, is_maybe_friend=is_maybe_friend, is_friend=is_friend)

@bp.route('/friends', methods=('GET', 'POST'))
@login_required
def friends():
  db = get_db()
  #友達検索？
  if request.method == 'POST':
    username = request.form['username']
    error = None

    if not username:
      error = 'Username is required'
    
    if error is not None:
      flash(error)
    else:
      user = db.execute(
        'SELECT id'
        ' FROM user'
        ' WHERE username = ?',
        (username,)
      ).fetchone()

      if user == None:
        error = 'User is None'
        flash(error)
      else:
        return redirect(url_for('auth.userpage', id=user['id']))


  #自分の友達
  friends = db.execute(
    'SELECT guest_id, username'
    ' FROM friend f JOIN user u ON f.guest_id = u.id'
    ' WHERE host_id = ?',
    (g.user['id'],)
  ).fetchall()

  return render_template('auth/friends.html', friends=friends)

@bp.route('/<int:id>/add_friend')
@login_required
def add_friend(id):
  db = get_db()
  db.execute(
    'INSERT INTO friend (host_id, guest_id)'
    ' VALUES (?, ?)',
    (g.user['id'], id)
  )
  db.commit()
  return redirect(url_for('auth.friends'))

@bp.route('/<int:id>/user_info', methods=('GET', 'POST'))
@login_required
def user_info(id):
  if request.method == 'POST':
    db = get_db()
    gender = request.form.get('gender')
    alcohol = request.form.get('alcohol')
    smoke = request.form.get('smoke')

    db.execute(
      'UPDATE user SET gender = ?'
      ' WHERE id = ?',
      (gender, id)
    )

    db.execute(
      'INSERT INTO alcohol (user_id, degree)'
      ' VALUES (?, ?)',
      (id, alcohol)
    )

    db.execute(
      'INSERT INTO smoke (user_id, degree)'
      ' VALUES (?, ?)',
      (id, smoke)
    )
    db.commit()
    return redirect(url_for('auth.userpage', id=id))

  return render_template('auth/user_info.html')