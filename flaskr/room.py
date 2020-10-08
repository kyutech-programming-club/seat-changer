from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('room', __name__)

@bp.route('/room')
def room_index():
    db = get_db()
    rooms = db.execute(
        'SELECT r.id, title, author_id'
        ' FROM room r JOIN user u ON r.author_id = r.id'
    ).fetchall()
    return render_template('room/room_index.html', rooms=rooms)

@bp.route('/introduce', methods=('GET', 'POST'))
@login_required
def introduce():
    if request.method == 'POST':
        return redirect(url_for('room.category'))
    
    return render_template('room/introduce.html')

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