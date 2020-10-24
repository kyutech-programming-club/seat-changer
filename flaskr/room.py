from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

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
    
    users = db.execute(
      'SELECT guest_id, username'
      ' FROM friend f JOIN user u ON f.guest_id = u.id'
      ' WHERE host_id = ?',
      (g.user['id'],)
    ).fetchall()

    room = db.execute(
      'SELECT r.id, title, author_id, username'
      ' FROM room r JOIN user u ON r.author_id = u.id'
      ' WHERE r.id = ?', 
      (id,)
    ).fetchone()
    return render_template('room/invite.html', users=users, room=room)

@bp.route('/<int:id>/category', methods=('GET', 'POST'))
@login_required
def category(id):
    db = get_db()

    if request.method == 'POST':
      return redirect(url_for('room.result'))
    
    participants = db.execute(
      'SELECT user_id, username'
      ' FROM participant JOIN user ON user_id = id'
      ' WHERE room_id = ?',
      (id,)
    ).fetchall()

    return render_template('room/category.html', participants=participants)

@bp.route('/result')
@login_required
def result():
    return render_template('room/result.html')
