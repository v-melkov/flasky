from datetime import datetime
import os
from threading import Thread

from flask import Flask, request, render_template, url_for, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
from flask_mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'very very very long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # export MAIL_USERNAME=username
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # export MAIL_PASSWORD=app_password

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky site <v.melkov@gmail.com>'
app.config['FLASKY_ADMIN'] = 'Admin <v.melkov@gmail.com>'

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.shell_context_processor
def shell_context_processor():
    return dict(db=db, Role=Role, User=User)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():  # если форма прошла проверку
        user = User.query.filter_by(username=form.name.data).first()  # ищем пользователя в БД
        if user is None:  # если пользователь не найден
            print(Role.query.filter_by(name='user').first())
            user = User(username=form.name.data, role=Role.query.filter_by(name='user').first())  # то создаём переменную user
            db.session.add(user)
            db.session.commit()  # и записываем её в БД
            session['know'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New user', 'mail/new_user', user=user)
        else:
            session['know'] = True
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('Кажется вы поменяли своё имя!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form, name=session.get('name'), know=session.get('know', False))


@app.route('/user/<name>/')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


class NameForm(FlaskForm):
    name = StringField('Как твоё имя?', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    userpass = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<Username %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

if __name__ == '__main__':
    app.run()
