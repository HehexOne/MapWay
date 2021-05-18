from flask import Flask, session, request, render_template
# from login import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config["SECRET_KEY"] = "sup3rsecr3tp@ssw0rd"


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(
        message="Поле имени пользователя не должно быть путсым!"),
        Length(min=8, max=32,
               message="Имя пользователя должно быть в диапазоне от 8 до 32 символов!")],
                           render_kw={"placeholder": 'Имя пользователя', "class": "input is-medium"})
    password = PasswordField('password', validators=[DataRequired(message="Поле пароля не должно быть пустым!"),
                                                     Length(min=8, max=32,
                                                            message="Пароль должен быть в диапазоне от 8 до 32 символов!")],
                             render_kw={"placeholder": 'Пароль', "class": "input is-medium"})
    submit = SubmitField('Войти', render_kw={"class": "button is-medium is-dark"})


class RegisterForm(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message="Поле имени не может быть пустым!"),
                                   Length(min=3, max=32, message="Имя должно быть от 3 до 32 символов!")],
                       render_kw={"placeholder": 'Имя', "class": "input is-medium"})
    surname = StringField('surname',
                          validators=[DataRequired(message="Поле фамилии не может быть пустым!"),
                                      Length(min=2, max=32, message="Фамилия должна быть от 2 до 32 символов!")])
    # email =
    # password
    # password_repeat
    # pc_agreement


@app.route("/")
def index():
    return "Hello, world"


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.username.errors)
        print(form.username.data, form.password.data)
    errors = form.username.errors + form.password.errors
    return render_template("login/login.html", form=form, errors=errors)


if __name__ == "__main__":
    app.run()
