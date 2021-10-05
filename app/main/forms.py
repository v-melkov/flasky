from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('Как твоё имя?', validators=[DataRequired()])
    submit = SubmitField('Отправить')
