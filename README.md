# AITOTO

2023/11/22：データベース機能を追加

1. このリポジトリをクローン
```
git clone https://github.com/Tsubasa-Watanabe/AITOTO_Flask.git
```

2. pythonの対話型シェルを開く
```
python3
```

<!--
3 以下を実行して, dbファイルが作成されているか確認
```
from app import app, db
with app.app_context():
  db.create_all()
```
-->

4. 対話型シェルを閉じて, 以下のファイルを実行
```
cd AITOTO_Flask
python3 app.py
```

5. [ここ](http://127.0.0.1:5000)からローカルホストへ

※ 使用するには下記のインストールが必要
```
pip3 install flask
pip3 install Flask-SQLAlchemy
```
