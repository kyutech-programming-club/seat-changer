from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('room', __name__)

def hobby_of_users_create(participant):
  db = get_db()
  
  hobbys = db.execute(
    'SELECT category'
    ' FROM hobby'
    ' WHERE user_id = ?',
    (participant['user_id'],)
  ).fetchall()

  return hobbys

def hobby_search(hobbys_of_user1, hobbys_of_user2):
  match_number = 0

  for hobby1 in hobbys_of_user1:
    for hobby2 in hobbys_of_user2:
      if hobby1['category'] == hobby2['category']:
        match_number += 1
        break

  return match_number

def hobby_divide_sort_list(participants_list):
  search_list = []
  divide_sort_list = []

  for i, user1 in enumerate(participants_list):
    for user2 in participants_list[i + 1:]:
      match_num = hobby_search(hobby_of_users_create(user1), hobby_of_users_create(user2))

      search_list.append(user1['user_id'])
      search_list.append(user2['user_id'])
      search_list.append(match_num)
      divide_sort_list.append(search_list)

      search_list = []

  divide_sort_list.sort(key=lambda x: x[2], reverse=True)

  return divide_sort_list

def hobby_is_existing(existing_list, compare_list):
  for existing in existing_list:
    if existing == compare_list[:-1]:
      return True

  return False

def hobby_is_included(temporary_match_hobby_list, participants_list):
  check_number = 0

  for participant in participants_list:
    for temporary_match_hobby in temporary_match_hobby_list:
      if participant['user_id'] in temporary_match_hobby:
        check_number += 1
        break

  if check_number == len(participants_list):
    return True
  else:
    return False

def hobby_create_match_hobby_list(divide_sort_list, participants_list):
  match_hobby_list = []
  existing_list = []
  index_list = [[0, 0, 1, 0, 1],
                [0, 1, 1, 0, 0],
                [1, 1, 0, 1, 0],
                [1, 0, 0, 1, 1]]

  for i in range(len(divide_sort_list)):
    if hobby_is_existing(existing_list, divide_sort_list[i]) == False:
      check = 0
      for j in range(len(divide_sort_list) - i - 1):
        for index in index_list:
          if divide_sort_list[i][index[0]] == divide_sort_list[i + j + 1][index[1]]:
            match_list = [divide_sort_list[i][index[2]], divide_sort_list[i][index[3]], divide_sort_list[i + j + 1][index[4]]]
            match_hobby_list.append(match_list)

            exist = [divide_sort_list[i + j + 1][0], divide_sort_list[i + j + 1][1]]
            existing_list.append(exist)

            check = 1

        if check == 1:
          break

    if hobby_is_included(match_hobby_list, participants_list) == True:
      break

  return match_hobby_list

def hobby_change_user_id_to_user_ofbect_list(user_id_list):
  db = get_db()
  user_object_list = []

  for user_id in user_id_list:
    user = db.execute(
      'SELECT username'
      ' FROM user'
      ' WHERE id = ?',
      (user_id,)
    ).fetchone()

    user_object_list.append(user)

  return user_object_list

def hobby_seat_change(sort_participants_list, participants_list):
  result = []

  return result

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    
    if request.method == 'POST':
      title = request.form['title']
      error = None

      if not title:
        error = 'Title is requied.'

      if error is not None:
        flash(error)
      else:
        db.execute(
          'INSERT INTO room (title, author_id)'
          ' VALUES (?, ?)',
          (title, g.user['id'])
        )
        db.commit()
        room_id = db.execute(
          'SELECT *'
          ' FROM room'
          ' WHERE rowid = last_insert_rowid()'
        ).fetchone()
        return redirect(url_for('room.invite', id=room_id['id']))

    return render_template('room/room_index.html')

@bp.route('/<int:id>/invite', methods=('GET', 'POST'))
@login_required
def invite(id):
    db = get_db()

    if request.method == 'POST':
      participants = request.form.getlist('check')

      db.execute(
        'DELETE FROM participant'
        ' WHERE room_id = ?',
        (id,)
      )

      db.execute(
        'INSERT INTO participant (user_id, room_id)'
        ' VALUES (?, ?)',
        (g.user['id'], id)
      )
      db.commit()

      for participant in participants:
        db.execute(
          'INSERT INTO participant (user_id, room_id)'
          ' VALUES (?, ?)',
          (participant, id)
        )
        db.commit()

      return redirect(url_for('room.category', id=id))
    
    rm_users = []

    users = db.execute(
      'SELECT guest_id, username'
      ' FROM friend f JOIN user u ON f.guest_id = u.id'
      ' WHERE host_id = ?',
      (g.user['id'],)
    ).fetchall()

    participants = db.execute(
      'SELECT user_id, username'
      ' FROM participant p JOIN user u ON p.user_id = u.id'
      ' WHERE room_id = ?',
      (id,)
    ).fetchall()

    for user in users:
      for participant in participants:
        if user['guest_id'] == participant['user_id']:
          rm_users.append(user)
          break

    for rm_user in rm_users:
      users.remove(rm_user)

    room = db.execute(
      'SELECT r.id, title, author_id, username'
      ' FROM room r JOIN user u ON r.author_id = u.id'
      ' WHERE r.id = ?', 
      (id,)
    ).fetchone()


    return render_template('room/invite.html', users=users, participants=participants, room=room)

@bp.route('/<int:id>/category', methods=('GET', 'POST'))
@login_required
def category(id):
    db = get_db()

    participants = db.execute(
      'SELECT user_id, username'
      ' FROM participant JOIN user ON user_id = id'
      ' WHERE room_id = ?',
      (id,)
    ).fetchall()

    if request.method == 'POST':
      smoke_check = request.form.get('smoke')
      alcohol_check = request.form.get('alcohol')
      hobby_check = request.form.get('hobby')
      gender_check = request.form.get('gender')
      shape_check = request.form.get('shape')

      print("--------------------------------------------------")
      print(smoke_check)
      print(alcohol_check)
      print(hobby_check)
      print(gender_check)
      print(shape_check)
      print("--------------------------------------------------")

      print("--------------------------------------------------")
      print(hobby_divide_sort_list(participants))
      print(hobby_create_match_hobby_list(hobby_divide_sort_list(participants), participants))
      print("--------------------------------------------------")

      return redirect(url_for('room.result', id=id))
    
    return render_template('room/category.html', participants=participants, id=id)

@bp.route('/<int:id>/result', methods=('GET', 'POST'))
@login_required
def result(id):
    return render_template('room/result.html', id=id)

@bp.route('/<int:id>/delete_room', methods=('POST',))
@login_required
def delete_room(id):
  db = get_db()
  db.execute(
    'DELETE FROM participant'
    ' WHERE room_id = ?',
    (id,)
  )

  db.execute(
    'DELETE FROM room'
    ' WHERE id = ?',
    (id,)
  )
  db.commit()

  return redirect(url_for('room.index'))

