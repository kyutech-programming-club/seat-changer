from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import itertools
import random

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

def hobby_score_number(participants_order, divide_list):
  score = 0

  for i in range(len(participants_order) - 2):
    for j in range(1, 3):
      for divide in divide_list:
        next_to_order = [participants_order[i]['user_id'], participants_order[i + j]['user_id']]
        if next_to_order == divide[:-1]:
          score += divide[2] * j

  last_next_order = [participants_order[-2]['user_id'], participants_order[-1]['user_id']]
  for divide in divide_list:
    if last_next_order == divide[:-1]:
      score += divide[2]

  return score

def hobby_high_score_index(score_list):
  index_list = []
  high_score_list = sorted(score_list, reverse=True)

  for i, score in enumerate(score_list):
    for high_score in high_score_list[:3]:
      if high_score == score:
        index_list.append(i)
        break

  return index_list

def hobby_high_score_list(participants_list, divide_list):
  all_pattern_list = list(itertools.permutations(participants_list))
  score_list = []
  high_score_list = []

  for one_pattern_order in all_pattern_list:
    score_list.append(hobby_score_number(one_pattern_order, divide_list))

  for index in hobby_high_score_index(score_list):
    high_score_list.append(all_pattern_list[index])

  return high_score_list

def hobby_seat_change(participants_list):
  divide_list = hobby_divide_sort_list(participants_list)
  seat_result = hobby_high_score_list(participants_list, divide_list)
  random.shuffle(seat_result)

  return seat_result[0]

def smoke_or_alcohol_shuffle_list(divide_list):
  order_list = []

  for one_list in divide_list:
    random.shuffle(one_list)

    for one_id in one_list:
      order_list.append(one_id)

  return order_list

def smoke_or_alcohol_change_object_list(id_list, participants_list):
  object_list = []

  for list_id in id_list:
    for participant in participants_list:
      if list_id == participant['user_id']:
        object_list.append(participant)
        break

  return object_list

def smoke_create_user_list(participants_list):
  db = get_db()

  smoke_list = []

  for participant in participants_list:
    smoke = db.execute(
      'SELECT user_id, degree'
      ' FROM smoke'
      ' WHERE user_id = ?',
      (participant['user_id'],)
    ).fetchone()

    smoke_list.append(smoke)

  return smoke_list

def smoke_divide_list(participants_list):
  smoke_list = smoke_create_user_list(participants_list)
  divide_list = [[] for i in range(3)]

  for smoke in smoke_list:
    if smoke['degree'] == "吸う":
      divide_list[0].append(smoke['user_id'])
    elif smoke['degree'] == "吸わない":
      divide_list[1].append(smoke['user_id'])
    elif smoke['degree'] == "無理":
      divide_list[2].append(smoke['user_id'])

  return divide_list

def smoke_seat_change(participants_list):
  divide_list = smoke_divide_list(participants_list)
  id_order_list = smoke_or_alcohol_shuffle_list(divide_list)
  seat_result = smoke_or_alcohol_change_object_list(id_order_list, participants_list)

  return seat_result

#--------------------------------------------------
def alcohol_create_user_list(participants_list):
  db = get_db()
  alcohol_list = []
  
  for participant in participants_list:
    alcohol = db.execute(
      'SELECT user_id, degree'
      ' FROM alcohol'
      ' WHERE user_id = ?',
      (participant['user_id'],)
    ).fetchone()

    alcohol_list.append(alcohol)

  return alcohol_list

def alcohol_divide_list(participants_list):
  alcohol_list = alcohol_create_user_list(participants_list)
  divide_list = [[] for i in range(4)]

  for alcohol in alcohol_list:
    if alcohol['degree'] == "たくさん飲む":
      divide_list[0].append(alcohol['user_id'])
    elif alcohol['degree'] == "普通":
      divide_list[1].append(alcohol['user_id'])
    elif alcohol['degree'] == "あまり飲まない":
      divide_list[2].append(alcohol['user_id'])
    elif alcohol['degree'] == "全く飲まない":
      divide_list[3].append(alcohol['user_id'])

  return divide_list

def alcohol_seat_change(participants_list):
  divide_list = alcohol_divide_list(participants_list)
  id_order_list = smoke_or_alcohol_shuffle_list(divide_list)
  seat_result = smoke_or_alcohol_change_object_list(id_order_list, participants_list)

  return seat_result
#--------------------------------------------------

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

      # print("--------------------------------------------------")
      # print(smoke_check)
      # print(alcohol_check)
      # print(hobby_check)
      # print(gender_check)
      # print(shape_check)
      # print("--------------------------------------------------")

      print("--------------------------------------------------")
      # print(hobby_seat_change(participants))
      # print(smoke_seat_change(participants))
      print(alcohol_seat_change(participants))
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

