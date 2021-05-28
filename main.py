from functools import wraps

from flask import Flask, session, request, render_template, redirect, url_for
# from login import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, EqualTo
from mysql.connector import connect
from hashlib import sha256
import datetime
from database_structures_and_functions import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "sup3rsecr3tp@ssw0rd"
connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
db = connection.cursor()
db.execute("USE std_1450_mw;")
connection.commit()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


class Constants:
    text_field_class = "input is-medium"
    button_submit_class = "button is-medium is-dark"


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(
        message="Поле почты не должно быть путсым!"),
        Length(min=8, max=32,
               message="Почта должна быть в диапазоне от 8 до 32 символов!")],
                        render_kw={"placeholder": 'Почта', "class": Constants.text_field_class, "type": "email"})
    password = PasswordField('password', validators=[DataRequired(message="Поле пароля не должно быть пустым!"),
                                                     Length(min=8,
                                                            max=32,
                                                            message="Пароль должен быть в диапазоне от 8 до 32 символов!")],
                             render_kw={"placeholder": 'Пароль', "class": Constants.text_field_class})
    submit = SubmitField('Войти', render_kw={"class": Constants.button_submit_class})


class RegisterForm(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message="Поле имени не может быть пустым!"),
                                   Length(min=3, max=32, message="Имя должно быть от 3 до 32 символов!")],
                       render_kw={"placeholder": 'Имя', "class": Constants.text_field_class})
    surname = StringField('surname',
                          validators=[DataRequired(message="Поле фамилии не может быть пустым!"),
                                      Length(min=2, max=32, message="Фамилия должна быть от 2 до 32 символов!")],
                          render_kw={"placeholder": "Фамилия", "class": Constants.text_field_class})
    birthday = DateField('birthday', validators=[DataRequired(message="Поле даты рождения должно быть заполнено!")],
                         render_kw={"placeholder": "Дата рождения", "class": Constants.text_field_class,
                                    "type": "date"})
    email = StringField('email',
                        validators=[DataRequired(message="Поле почты должно быть заполнено!"),
                                    Length(min=5, max=64, message="Почта должна содержать от 5 до 64 символов!")],
                        render_kw={"placeholder": "Почта", "class": Constants.text_field_class, "type": "email"})
    password = PasswordField('password',
                             validators=[DataRequired(message="Введите пароль!"),
                                         Length(min=8, max=32,
                                                message="Длина пароля должна быть в диапазоне от 8 до 32 символов!")],
                             render_kw={"placeholder": "Пароль", "class": Constants.text_field_class})
    password_repeat = PasswordField('password_repeat',
                                    validators=[EqualTo('password', message="Пароли должны совпадать!")],
                                    render_kw={"placeholder": "Повтор пароля", "class": Constants.text_field_class})
    pc_agreement = BooleanField('pc_agreement', validators=[DataRequired(message="Требуется соглашение с условиями!")],
                                render_kw={"class": "checkbox"})
    submit = SubmitField('Зарегистрироваться', render_kw={"class": Constants.button_submit_class})


@app.route("/")
@login_required
def index():
    user = get_user_by_id(session['id'])
    return render_template("new/MainPage.html", user=user)


@app.route("/about")
@login_required
def about():
    user = get_user_by_id(session['id'])
    return render_template("new/AboutUs.html", user=user)


@app.route("/object<int:ident>")
@login_required
def object(ident):
    user = get_user_by_id(session['id'])
    object_from_db = get_object_by_id(ident)
    # if not object_from_db:
    #     return redirect(url_for("not_found"))
    return render_template("new/Object.html", user=user, object=object_from_db)


@app.errorhandler(404)
@app.route("/not_found")
def not_found():
    return "Not found!", 404


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    our_errors = list()
    if form.validate_on_submit():
        user = get_user_by_credentials(form.email.data, form.password.data)
        if user:
            session['id'] = user.id
            return redirect(url_for("index"))
        else:
            our_errors.append("Такого пользователя не существует!")
    errors = form.email.errors + form.password.errors
    if type(errors) == tuple:
        errors += tuple(our_errors)
    else:
        errors += our_errors
    return render_template("login/login.html", form=form, errors=errors)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    three_years_ago = datetime.datetime.now() - datetime.timedelta(days=3*365)
    form = RegisterForm()
    our_errors = list()
    if form.validate_on_submit():
        new_user = User(None,
                        form.name.data,
                        form.surname.data,
                        form.email.data,
                        sha256(form.password.data.encode("utf-8")).hexdigest(),
                        0,
                        0,
                        form.birthday.data)
        session['id'] = create_user_by_user_object(new_user)
        return redirect(url_for("index"))
    errors = form.name.errors + form.surname.errors + form.email.errors + \
             form.password.errors + form.password_repeat.errors + form.pc_agreement.errors + \
             form.birthday.errors
    if type(errors) == tuple:
        errors += tuple(our_errors)
    else:
        errors += our_errors
    return render_template("login/registration.html", form=form, errors=errors, three_years_ago=three_years_ago.date())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()