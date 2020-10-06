from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/introduce', methods=('GET', 'POST'))
@login_required
def introduce():
    if request.method == 'POST':
        return render_template('room/category.html')
    
    return render_template('room/introduce.html')

@bp.route('/category', methods=('GET', 'POST'))
@login_required
def category():
    if request.method == 'POST':
        return render_template('room/result.html')
    
    return render_template('room/category.html')

@bp.route('/result')
@login_required
def result():
    return render_template('room/result.html')