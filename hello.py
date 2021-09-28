from datetime import datetime

from flask import Flask, request, render_template, url_for, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'very very very long secret key'


@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Кажется вы поменяли своё имя!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form, name=session.get('name'))


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

if __name__ == '__main__':
    app.run()
