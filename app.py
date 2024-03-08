import datetime
import os
import random
import time
from enum import unique

import pytz
# 決済システムstripeの導入
import stripe
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

stripe.api_key = 'sk_test_51OiS9FBJcq3dnxpdURiiEeGjg3ItDVUk9Z3kZUv1300ZMJATHqu2rdAU77W5HL4MyCVVGUWHZy90JyjvgOI1MbVY00uOkzgyyg'

import pandas as pd
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///info.db"
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ログインを管理するための設定
login_manager = LoginManager()
login_manager.init_app(app)


app.config['SECRET_KEY'] = 'secret_key'
app.config['USERNAME'] = 'user'
app.config['PASSWORD'] = 'pass'

UPLOAD_FOLDER = './static/up'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'biz.tsubasa.watanabe@gmail.com'
app.config['MAIL_PASSWORD'] = 'jhhxvrvitsle bgni'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Excelファイルを読み込む
df = pd.read_excel('./static/excel/recommend_table.xlsx')
df = df.to_dict(orient='records')
# print(df)

class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)  # ID
    date = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) # 日付と時間
    title = db.Column(db.String(100), nullable=True) # タイトル
    note = db.Column(db.Text, nullable=True) # メモ
    file_path = db.Column(db.String(255), nullable=True)
    saved = db.Column(db.Boolean, default=False)  # 保存フラグ

    # ユーザーの投稿管理
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ユーザーID

    # ユーザーとの関連付け
    user = db.relationship('User', back_populates='posts')

    def __init__(self, title, note, file_path, user_id, saved=False):
        self.title = title
        self.note = note
        self.file_path = file_path
        self.user_id = user_id
        self.date = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        self.saved = saved

# ユーザー情報を管理するデータベース
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID
    username = db.Column(db.String(30), nullable=False, unique=True)  # ユーザー名
    password = db.Column(db.String(12), nullable=False)  # パスワード
    birthday = db.Column(db.String(30), nullable=True) # 生年月日
    gender = db.Column(db.String(50)) #性別
    # ユーザーが投稿したデータの関連を定義する
    posts = db.relationship('Database', backref='user_posts')

    def __init__(self, username, password, birthday, gender):
    # def __init__(self, username, password, birthday):
        self.username = username
        self.password = password
        self.birthday = birthday
        self.gender = gender


# アンケート情報を管理するデータベース
class SurveyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(255))
    gender = db.Column(db.String(50))
    age = db.Column(db.String(50))
    relationship = db.Column(db.String(50))
    occasion = db.Column(db.String(50))
    budget = db.Column(db.String(50))
    additional_notes = db.Column(db.Text)

    post_id = db.Column(db.Integer, db.ForeignKey('database.id'), nullable=False)  # 投稿のIDを参照

# ユーザーローダー関数を設定
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# 乱数パラメータを格納するためのグローバル変数
success_param = None

# 乱数を生成し、success_paramに設定する関数
def generate_success_param():
    global success_param
    success_param = random.randint(1, 10000)

# トップページはシンプルにindex.htmlを表示するだけ
@app.route('/', methods=['GET', 'POST'])
def index():
    generate_success_param()
    if request.method == 'POST':
        return redirect(url_for('create_checkout_session'))
    return render_template('index.html', success=success_param)
	

# アンケートページ
@app.route('/submit_survey/<int:id>', methods=['GET', 'POST'])
def submit_survey(id):
    generate_success_param()
    if request.method == 'POST':
        # フォームからのデータを取得
        recipient_name = request.form.get('recipientName')
        gender = 'male' if request.form.get('genderMale') == 'male' else 'female'
        age = request.form.get('age')
        relationship = request.form.get('relationship')
        occasion = request.form.get('occasion')
        budget = request.form.get('budget')
        additional_notes = request.form.get('additionalNotes')

        # すべてのデータが入力されているかチェック
        if not recipient_name or not gender or not age or not relationship or not occasion or not budget:
            flash('必須項目を入力してください。', 'error')
            return redirect(url_for('submit_survey', id=id))
        else:
            # データをセッションに保存
            session['survey_result'] = {
                'recipient_name': recipient_name,
                'gender': gender,
                'age': age,
                'relationship': relationship,
                'occasion': occasion,
                'budget': budget,
                'additional_notes': additional_notes
            }
            # データベースに送信
            survey_data = SurveyData(
                post_id=id,  # 投稿の ID を追加
                recipient_name=recipient_name,
                gender=gender,
                age=age,
                relationship=relationship,
                occasion=occasion,
                budget=budget,
                additional_notes=additional_notes
            )

            db.session.add(survey_data)
            db.session.commit()

            return redirect(url_for('gift_return', id=id, success=success_param))
    else:
        return render_template('question.html', success=success_param, id=id)


# 会員登録機能を追加
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        birthday = request.form.get("birthday")
        # genderだけbuttonなのでif文で仕分け
        if request.form.get('genderMale') == 'male':
            gender = 'male'
        elif request.form.get('genderFemale') == 'female':
            gender = 'female'
        elif request.form.get('genderOther') == 'other':
            gender = 'other'
        else:
            gender = 'Null'

        # ユーザー名が既に使用されているかどうかをチェック
        if User.query.filter_by(username=username).first():
            flash('ユーザ名は既に使用されています')
            return redirect(url_for('register'))
        else:
            # ユーザー情報をデータベースに登録
            user = User(
                username=username,
                password=password,
                birthday=birthday,
                gender=gender,
                )
            db.session.add(user)
            db.session.commit()

        flash('会員登録が完了しました')
        return redirect(url_for('login'))

    else:
        return render_template('register.html')

# ログイン機能を追加
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        # パスワードはハッシュ化されているので、check_password_hashを使ってユーザー名、パスワードが正しいかチェック
        if (user.password == password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('ユーザ名もしくはパスワードが異なります')
            return render_template('login.html')

    else:
        return render_template('login.html')

# ログアウト機能を追加
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/preview_page', methods=['GET', 'POST'])
@login_required
def preview():
    generate_success_param()
    if request.method == 'POST':

        user_id = current_user.id
        title = request.form.get('title')
        note = request.form.get('memo')
        file = request.files['file']
        dstr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = dstr + str(random.randint(0, 10000)) + ".jpg"

        if filename == '':
            flash("ファイルが選択されていません")
            return redirect(url_for('exit'))

        savepath = os.path.join('static', 'up', filename)
        file.save(savepath)
        data = Database(title=title, note=note, file_path=filename, user_id=user_id)
        db.session.add(data)
        db.session.commit()

        time.sleep(2)


        return redirect(url_for('list', success=success_param))
        #return jsonify({'success': 'データが正常に保存されました'}), 200
    else:
        return render_template('preview.html', success=success_param)

@app.route('/list')
@login_required
def list():
    generate_success_param()
    #success = request.args.get('success')
    # 現在のユーザーのIDを取得
    user_id = current_user.id
    # ユーザーIDに基づいて投稿をフィルタリング
    posts = Database.query.filter_by(user_id=user_id).all()
    success_param = random.randint(1, 10000)
    return render_template('list.html', posts=posts, success=success_param)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    generate_success_param()
    post = db.session.query(Database).get(id)
    # success_param = random.randint(1, 10000)

    if request.method == 'POST':
        title = request.form.get('title')
        note = request.form.get('note')
        file = request.files['file']

        # ファイルがアップロードされた場合のみ処理を行う
        if file:
            # 新しいファイル名を生成
            dstr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            filename = dstr + str(random.randint(0, 10000)) + ".jpg"

            # 既存のファイルがあれば削除
            if post.file_path:
                os.remove(os.path.join('static', 'up', post.file_path))

            # ファイル保存
            savepath = os.path.join('static', 'up', filename)
            file.save(savepath)

            # データベースの情報を更新
            post.file_path = filename

        # タイトルとノートの更新
        post.title = title
        post.note = note

        # データベースの情報をコミット
        db.session.commit()
        
        return redirect(url_for('list', success=success_param))

    return render_template('edit.html', post=post, success=success_param)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_entry(id):
    generate_success_param()
    entry = Database.query.get(id)

    if entry:
        # データベースからエントリを削除
        db.session.delete(entry)
        db.session.commit()
    # success_param = random.randint(1, 10000)

    return redirect('/list')

@app.route('/gift_return/<int:id>', methods=['GET', 'POST'])
@login_required
def gift_return(id):
    generate_success_param()
    post = Database.query.get_or_404(id)
    # セッションからデータを取得
    survey_result = session.get('survey_result', {})
    if request.method == 'POST':
        # POST メソッドでの処理
        post.saved = True  # saved を True に設定
        db.session.commit()  # データベースに保存
        return redirect(url_for('list', success=success_param, id=id))
    else:
        # GET メソッドでの処理
        # genderの値に基づいてdfからデータをフィルタリング
        if survey_result.get('gender') == 'female':
            df2 = [item for item in df if item['gender'] == 1]
            return render_template('gift_return.html', success=success_param, df=df2, id=id)
        else: 
            df3 = [item for item in df if item['gender'] == 0]
            return render_template('gift_return.html', success=success_param, df=df3, id=id)

@app.route('/view_survey/<int:id>', methods=['GET', 'POST'])
def view_survey(id):
    survey_data = SurveyData.query.filter_by(post_id=id).first_or_404()
    if request.method == 'POST':
        recipient_name = request.form.get('recipientName')
        gender = request.form.get('gender')
        age = request.form.get('age')
        relationship = request.form.get('relationship')
        occasion = request.form.get('occasion')
        budget = request.form.get('budget')
        additional_notes = request.form.get('additionalNotes')

        # 必須項目の入力チェック
        if not recipient_name or not gender or not age or not relationship or not occasion or not budget:
            flash('必須項目を入力してください。', 'error')
            return redirect(url_for('view_survey', id=id))

        # データベースに保存
        survey_data.recipient_name = recipient_name
        survey_data.gender = gender
        survey_data.age = age
        survey_data.relationship = relationship
        survey_data.occasion = occasion
        survey_data.budget = budget
        survey_data.additional_notes = additional_notes

        db.session.commit()

        return redirect(url_for('gift_return', success=success_param, id=id))

    return render_template('view_survey.html', survey_data=survey_data)


@app.route('/get_item/<int:index>')
def get_item(index):
    # 指定されたインデックスのデータを取得
    item = df[index % len(df)]
    return jsonify(item)

# 決済
@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1OiSYzBJcq3dnxpdbjGpmMOl',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
    except Exception as e:
        return str(e) # その他エラーの場合

    return redirect(checkout_session.url, code=303)

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'GET':
        return render_template('success.html')

@app.route('/send', methods=['POST'])
def send():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        msg = Message('おもいでノート', sender='biz.tsubasa.watanabe@gmail.com', recipients=['biz.tsubasa.watanabe@gmail.com'])
        msg.body = f"プレミアムプランが購入されました！！\n購入者名: {name}\nメールアドレス: {email}"
        mail.send(msg)

        return redirect(url_for('thank'))

@app.route('/thank', methods=['GET', 'POST'])
def thank():
    if request.method == 'GET':
        return render_template('thank.html')

@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == 'GET':
        return render_template('cancel.html')

if __name__ == '__main__':
    app.run(debug=True)