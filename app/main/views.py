from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..email import send_email
from ..models import User, Role


@main.route('/', methods=['GET', 'POST'])
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
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New user', 'mail/new_user', user=user)
        else:
            session['know'] = True
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('Кажется вы поменяли своё имя!')
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form, name=session.get('name'), know=session.get('know', False))


@main.route('/user/<name>/')
def user(name):
    return render_template('user.html', name=name)
