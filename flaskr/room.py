from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('room', __name__)

@bp.route('/room', methods=('GET', 'POST'))
@login_required
def room_index():
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
        rooms = db.execute(
          'SELECT id, author_id'
          ' FROM room'
          ' WHERE author_id = ?', (g.user['id'],)
        )
        print(rooms)
        room = rooms[-1]
        return redirect(url_for('room.introduce', id=room['id']))

    rooms = db.execute(
        'SELECT r.id, title, author_id, username'
        ' FROM room r JOIN user u ON r.author_id = r.id'
    ).fetchall()
    return render_template('room/room_index.html', rooms=rooms)

@bp.route('/<int:id>/introduce', methods=('GET', 'POST'))
@login_required
def introduce(id):
    db = get_db()

    if request.method == 'POST':
        return redirect(url_for('room.category'))
    
    users = db.execute(
      'SELECT username, u.id'
      ' FROM user u'
    ).fetchall()
    room = db.execute(
      'SELECT r.id, title, author_id, username'
      ' FROM room r JOIN user u ON r.author_id = u.id'
      ' WHERE r.id = ?', 
      (id,)
    ).fetchone()
    return render_template('room/introduce.html', users=users, room=room)

@bp.route('/category', methods=('GET', 'POST'))
@login_required
def category():
    if request.method == 'POST':
        return redirect(url_for('room.result'))
    
    return render_template('room/category.html')

@bp.route('/result')
@login_required
def result():
    return render_template('room/result.html')
