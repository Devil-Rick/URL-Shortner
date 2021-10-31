from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

# creating the database uri (using SQL Lite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///URL_Directory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# creating the database
url_db = SQLAlchemy(app)


@app.before_first_request
def create_table():
    url_db.create_all()

# creating the schema of the database


class URLS(url_db.Model):
    id_ = url_db.Column(url_db.Integer, primary_key=True)
    long_url = url_db.Column(url_db.String(), nullable=False)
    short_url = url_db.Column(url_db.String(20), nullable=False)

    def __init__(self, long_url, short_url):
        self.long_url = long_url
        self.short_url = short_url


@app.route('/')
def send_home():
    return redirect('/home')


def shorten_url():
    characterSet = string.ascii_lowercase + string.ascii_uppercase
    while True:
        letters = random.choices(characterSet, k=8)
        url = ''.join(letters)
        short_found = URLS.query.filter_by(short_url=url).first()
        if not short_found:
            url = url.replace(' ', '0')
            return url


@app.route("/home", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        url_long = request.form['long_url']

        found_url = URLS.query.filter_by(long_url=url_long).first()

        if found_url:
            return render_template('HomePage.html', url=found_url.short_url)
        else:
            url_short = shorten_url()
            n_url = URLS(url_long, url_short)
            url_db.session.add(n_url)
            url_db.session.commit()
            return render_template('HomePage.html', url=url_short)
    else:
        return render_template('HomePage.html')


@app.route("/history")
def history():
    urls = URLS.query.all()
    return render_template('History.html', url=urls)


@app.route('/<s_url>')
def open_url(s_url):
    main_url = URLS.query.filter_by(short_url=s_url).first()

    if main_url:
        return redirect(main_url.long_url)
    else:
        return f'<h1>URL Doesnot Exist</h1>'


@app.route('/delete')
def delete():
    url_db.session.query(URLS).delete()
    url_db.session.commit()
    return redirect('/history')


if __name__ == '__main__':
    app.run(debug=True)
