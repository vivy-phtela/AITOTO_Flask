from flask import render_template
from testapp import app

@app.route('/')
def index():
    return render_template('testapp/index.html')

@app.route('/preview_page')
def another_page():
    return render_template('testapp/preview_page.html')