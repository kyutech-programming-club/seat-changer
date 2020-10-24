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
    if request.method == 'POST':
        return redirect(url_for('room.result', id=id))
    
    return render_template('room/category.html')

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
  db.commit()

  db.execute(
    'DELETE FROM room'
    ' WHERE id = ?',
    (id,)
  )
  db.commit()

  return redirect(url_for('room.index'))
