from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime, pytz
import os
from werkzeug.utils import secure_filename
import datetime, random
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///info.db"
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config['SECRET_KEY'] = 'secret_key'
app.config['USERNAME'] = 'user'
app.config['PASSWORD'] = 'pass'

UPLOAD_FOLDER = './static/up'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)  # ID
    date = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) # 日付と時間
    title = db.Column(db.String(100), nullable=True) # タイトル
    note = db.Column(db.Text, nullable=True) # メモ
    file_path = db.Column(db.String(255), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def upload():
    session["flag"] = False
    return redirect('/preview_page')

# @app.route('/login', methods=['GET'])
# def login():
#     if session["flag"]:
#         return render_template('preview.html')
#     else:
#         return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login_post():
#     username = request.form["username"]
#     password = request.form["password"]
#     if username != app.config['USERNAME'] or password != app.config['PASSWORD']:
#         flash('ユーザ名もしくはパスワードが異なります')
#     else:
#         session["flag"] = True
#     if session["flag"]:
#         return render_template('preview.html')
#     else:
#         return redirect('/login')

@app.route('/preview_page', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        title = request.form.get('title')
        note = request.form.get('note')
        file = request.files['file']
        dstr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = dstr + str(random.randint(0, 10000)) + ".jpg"

        if filename == '':
            flash("ファイルが選択されていません")
            return redirect('/preview_page')

        savepath = os.path.join('static', 'up', filename)
        file.save(savepath)

        data = Database(title=title, note=note, file_path=filename)
        db.session.add(data)
        db.session.commit()

        return redirect('/list')
    else:
        return render_template('preview.html')

@app.route('/list')
def list():
    posts = Database.query.all()
    return render_template('list.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
