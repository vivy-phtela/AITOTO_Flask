from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime, pytz

app = Flask(__name__)

db = SQLAlchemy()

app.config['SECRET_KEY'] = 'secret_key'
app.config['USERNAME'] = 'user'
app.config['PASSWORD'] = 'pass'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///info.db"
db.init_app(app)
class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)  # ID
    date = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) # 日付と時間
    title = db.Column(db.String(100), nullable=True) # タイトル
    note = db.Column(db.Text, nullable=True) # メモ

@app.route('/')
def upload():
    session["flag"] = False
    return redirect('/login')

@app.route('/login', methods=['GET'])
def login():
    if session["flag"]:
        return render_template('upload.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    if username != app.config['USERNAME'] or password != app.config['PASSWORD']:
        flash('ユーザ名もしくはパスワードが異なります')
    else:
        session["flag"] = True
    if session["flag"]:
        return render_template('upload.html')
    else:
        return redirect('/login')

@app.route('/preview_page', methods = ['GET', 'POST'])
def preview():
    if request.method == 'POST': # POST
        title = request.form.get('title')
        note = request.form.get('note')
        data = Database(title = title, note = note) # インスタンス化

        db.session.add(data) # 追加
        db.session.commit() # 反映
        return redirect('/list')

    else: # GET
        return render_template('preview.html')

@app.route('/list')
def list():
    posts = Database.query.all()
    return render_template('list.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)