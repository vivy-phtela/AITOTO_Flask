from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db.init_app(app)
class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)  # ID
    title = db.Column(db.String(100), nullable=True) # タイトル
    memo = db.Column(db.Text, nullable=True) # メモ

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview_page', methods = ['GET', 'POST'])
def preview_page():
    if request.method == 'POST': # POST
        title = request.form.get('title')
        memo = request.form.get('memo')
        data = Database(title = title, memo = memo) # インスタンス化

        db.session.add(data) # 追加
        db.session.commit() # 反映
        return redirect('/list') # トップページに戻る

    else: # GET
        return render_template('preview_page.html')

@app.route('/list')
def list():
    posts = Database.query.all()
    return render_template('list.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)