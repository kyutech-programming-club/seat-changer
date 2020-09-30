from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room')
def create_room():
    return render_template('room.html')

@app.route('/room/category')
def select_category():
    return render_template('category.html')

@app.route('/room/category/result')
def result():
    return render_template('result.html')

@app.route('/user')
def my_page():
    return render_template('user.html')

if __name__ == '__main__':
    app.run()
