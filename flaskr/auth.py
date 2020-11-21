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
  db = get_db()

  hobbys = db.execute(
    'SELECT category FROM hobbys'
  ).fetchall()

  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    gender = request.form.get('gender')
    alcohol = request.form.get('alcohol')
    smoke = request.form.get('smoke')
    hobbys = request.form.getlist('check')
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
        'INSERT INTO user (username, password, gender) VALUES (?, ?, ?)',
        (username, generate_password_hash(password), gender)
      )

      user_id = db.execute(
        'SELECT id FROM user'
        ' WHERE username = ?',
        (username,)
      ).fetchone()

      db.execute(
        'INSERT INTO alcohol (user_id, degree)'
        ' VALUES (?, ?)',
        (user_id['id'], alcohol)
      )

      db.execute(
        'INSERT INTO smoke (user_id, degree)'
        ' VALUES (?, ?)',
        (user_id['id'], smoke)
      )

      for hobby in hobbys:
        db.execute(
          'INSERT INTO hobby (user_id, category)'
          ' VALUES (?, ?)',
          (user_id['id'], hobby)
        )

      db.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html', hobbys=hobbys)

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
  #カテゴリーの表示
  gender = db.execute(
    'SELECT gender'
    ' FROM user'
    ' WHERE id = ?',
    (id,)
  ).fetchone()

  alcohol = db.execute(
    'SELECT degree'
    ' FROM alcohol'
    ' WHERE user_id = ?',
    (id,)
  ).fetchone()

  smoke = db.execute(
    'SELECT degree'
    ' FROM smoke'
    ' WHERE user_id = ?',
    (id,)
  ).fetchone()

  hobbys = db.execute(
    'SELECT category FROM hobby'
    ' WHERE user_id = ?',
    (id,)
  ).fetchall()

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

  return render_template(
    'auth/user.html',
    user=user,
    id=id,
    maybe_friends=maybe_friends,
    is_maybe_friend=is_maybe_friend,
    is_friend=is_friend,
    gender=gender,
    alcohol=alcohol,
    smoke=smoke,
    hobbys=hobbys
    )

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
  db = get_db()
  gender_list = ['男', '女', 'その他']
  alcohol_list = ['たくさん飲む', '普通', 'あまり飲まない', '全く飲まない']
  smoke_list = ['吸う', '吸わない', '無理']
  rm_hobbys = []
  
  user_ge = db.execute(
    'SELECT gender FROM user'
    ' WHERE id = ?',
    (id,)
  ).fetchone()

  user_al = db.execute(
    'SELECT degree FROM alcohol'
    ' WHERE user_id = ?',
    (id,)
  ).fetchone()

  user_sm = db.execute(
    'SELECT degree FROM smoke'
    ' WHERE user_id = ?',
    (id,)
  ).fetchone()

  hobbys = db.execute(
    'SELECT category FROM hobbys'
  ).fetchall()

  my_hobbys = db.execute(
    'SELECT category, user_id FROM hobby'
    ' WHERE user_id = ?',
    (id,)
  ).fetchall()

  for hobby in hobbys:
    for my_hobby in my_hobbys:
      if hobby['category'] == my_hobby['category']:
        rm_hobbys.append(hobby)
        break

  for rm_hobby in rm_hobbys:
    hobbys.remove(rm_hobby)

  if request.method == 'POST':
    gender = request.form.get('gender')
    alcohol = request.form.get('alcohol')
    smoke = request.form.get('smoke')
    checked_hobbys = request.form.getlist('check')

    db.execute(
      'UPDATE user SET gender = ?'
      ' WHERE id = ?',
      (gender, id)
    )

    db.execute(
      'UPDATE alcohol SET degree = ?'
      ' WHERE user_id = ?',
      (alcohol, id)
    )

    db.execute(
      'UPDATE smoke SET degree = ?'
      ' WHERE user_id = ?',
      (smoke, id)
    )

    db.execute(
      'DELETE FROM hobby'
      ' WHERE user_id = ?',
      (id,)
    )

    for checked_hobby in checked_hobbys:
      db.execute(
        'INSERT INTO hobby (user_id, category)'
        ' VALUES (?, ?)',
        (id, checked_hobby)
      )

    db.commit()
    return redirect(url_for('auth.userpage', id=id))

  return render_template('auth/user_info.html', gender_list=gender_list, alcohol_list=alcohol_list, smoke_list=smoke_list, gender=user_ge['gender'], alcohol=user_al['degree'], smoke=user_sm['degree'], hobbys=hobbys, my_hobbys=my_hobbys)

@bp.route('/add_hobbys', methods=('GET', 'POST'))
@login_required
def add_hobbys():
  db = get_db()

  if request.method == 'POST':
    hobbys = request.form['hobbys']

    db.execute(
      'INSERT INTO hobbys VALUES (?)',
      (hobbys,)
    )
    db.commit()

    return redirect(url_for('auth.user_info', id=g.user['id']))

  return render_template('auth/add_hobbys.html')







