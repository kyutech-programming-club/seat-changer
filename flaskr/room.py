from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import itertools
import random
from . import seat

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('room', __name__)

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

      db.execute(
        'INSERT INTO seat (room_id, smoke, alcohol, hobby, gender, shape)'
        ' VALUES (?, ?, ?, ?, ?, ?)',
        (id, smoke_check, alcohol_check, hobby_check, gender_check, shape_check)
      )
      db.commit()

      print("--------------------------------------------------")
      print(smoke_check)
      print(alcohol_check)
      print(hobby_check)
      print(gender_check)
      print(shape_check)
      print(seat_order)
      print("--------------------------------------------------")

      return redirect(url_for('room.result', id=id))
    
    return render_template('room/category.html', participants=participants, id=id)

@bp.route('/<int:id>/result', methods=('GET', 'POST'))
@login_required
def result(id):
  seat_order = seat.seat_change(participants, smoke_alcohol_check, hobby_check, gender_check)

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
    'DELETE FROM seat'
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

