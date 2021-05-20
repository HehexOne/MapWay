from functools import wraps

from flask import Flask, session, request, render_template, redirect, url_for
# from login import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, EqualTo
from mysql.connector import connect
from hashlib import sha256

app = Flask(__name__)
app.config["SECRET_KEY"] = "sup3rsecr3tp@ssw0rd"
connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
db = connection.cursor()
db.execute("USE std_1450_mw;")
connection.commit()


class User:

    def __init__(self, id, name, surname, email, password_hash, rights_level, subscription_level, birthday):
        self.id = id
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = password_hash
        self.right_level = rights_level
        self.subscription_level = subscription_level
        self.birthday = birthday


def create_user_by_user_object(user_obj: User):
    query = f"INSERT INTO User (name, surname, email, password_hash, rights_level, subscription_level, birthday)" \
            f"VALUES ('{user_obj.name}', '{user_obj.surname}', '{user_obj.email}', '{user_obj.password_hash}'," \
            f"{user_obj.right_level}, {user_obj.subscription_level}, '{user_obj.birthday}');"
    db.execute(query)
    connection.commit()
    db.execute("SELECT LAST_INSERT_ID()")
    return db.fetchone()


def get_user_by_credentials(email, password):
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    query = f"SELECT * FROM User WHERE email='{email}' AND password_hash='{password_hash}' LIMIT 1"
    db.execute(query)
    result = db.fetchone()
    if result:
        # Converting database response to object
        return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    else:
        return None


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
    return "<a href='/logout'>Выйти</a><br>Hello, world"


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
        print(new_user.birthday)
        session['id'] = create_user_by_user_object(new_user)
        return redirect(url_for("index"))
    errors = form.name.errors + form.surname.errors + form.email.errors + \
             form.password.errors + form.password_repeat.errors + form.pc_agreement.errors + \
             form.birthday.errors
    if type(errors) == tuple:
        errors += tuple(our_errors)
    else:
        errors += our_errors
    return render_template("login/registration.html", form=form, errors=errors)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
