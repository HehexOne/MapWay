from functools import wraps

from flask import Flask, request, render_template, redirect, url_for, session
from mysql.connector import connect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, EqualTo
from hashlib import sha256
import datetime
from newMapWay import *
from database_structures_and_functions import *
from libgravatar import Gravatar
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sup3rsecr3tp@ssw0rd'
connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
cursor = connection.cursor()
cursor.execute("USE std_1450_mw;")
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


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get('id') is None:
        return render_template("landing.html")
    else:
        user = get_user_by_id(session['id'])
        get_current_route_id_sql = 'SELECT id FROM Route ORDER BY id DESC LIMIT 1'
        cursor.execute(get_current_route_id_sql)
        current_route_id = cursor.fetchall()
        return render_template("main.html", user=user, current_route=current_route_id[0][0])


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
    three_years_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 365)
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


# поиск по достопримечательностям
@app.route("/objects", methods=["GET", "POST"])
def objects():
    user = get_user_by_id(session['id'])
    page = request.args.get('page', 1, type=int)

    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                 f"INNER JOIN Category C on OC.category_id = C.id " \
                 f"ORDER BY Object.id " \
                 f"LIMIT 3 OFFSET {(page - 1) * 3} "

    search_input = None
    sort = None
    filter = None

    if request.method == 'GET':
        if request.args.get('search_input'):
            search_input = request.args.get('search_input')

        if request.args.get('sort'):
            sort = request.args.get('sort')
            if sort == 'По имени':
                sort_condition = 'name'
            elif sort == 'По рейтингу':
                sort_condition = 'rating'
            else:
                sort_condition = 'id'

            filter = request.args.get('filter')
            if search_input:
                if filter != 'Все':
                    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                                 f"INNER JOIN Category C on OC.category_id = C.id " \
                                 f"WHERE C.name = '{filter}' AND Object.name LIKE '%{search_input}%' " \
                                 f"ORDER BY Object.{sort_condition} LIMIT 3 OFFSET {(page - 1) * 3}"
                else:
                    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                                 f"INNER JOIN Category C on OC.category_id = C.id " \
                                 f"WHERE Object.name LIKE '%{search_input}%' " \
                                 f"ORDER BY Object.{sort_condition} LIMIT 3 OFFSET {(page - 1) * 3})"
            else:
                if filter != 'Все':
                    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                                 f"INNER JOIN Category C on OC.category_id = C.id " \
                                 f"WHERE C.name = '{filter}' " \
                                 f"ORDER BY Object.{sort_condition} LIMIT 3 OFFSET {(page - 1) * 3}"
                else:
                    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                                 f"INNER JOIN Category C on OC.category_id = C.id " \
                                 f"ORDER BY Object.{sort_condition} LIMIT 3 OFFSET {(page - 1) * 3})"

    cursor.execute(object_sql)
    object_results = cursor.fetchall()

    category_sql = f"SELECT * FROM Category"
    cursor.execute(category_sql)
    category_results = cursor.fetchall()

    return render_template('Objects.html', object_results=object_results,
                           page=page, user=user, category_results=category_results,
                           search_input=search_input, sort=sort,
                           filter=filter)


# решить проблему с комментами
@app.route("/object")
def object():
    user = get_user_by_id(session['id'])
    id = request.args.get('id', 1, type=int)

    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                 f"INNER JOIN Category C on OC.category_id = C.id " \
                 f"WHERE Object.id = {id}"
    cursor.execute(object_sql)
    object_results = cursor.fetchall()

    object_comments = "SELECT Review.id, Review.text, Review.rating, O.id as 'object_id' FROM Review" \
                      "INNER JOIN ObjectInRoute OIR on Review.object_in_route = OIR.id" \
                      f"INNER JOIN Object O on OIR.object_id = O.id Where O.id = {id};"

    return render_template('Object.html', id=id, object_results=object_results,
                           object_comments=object_comments, user=user)


@app.route("/aboutUs")
def about():
    user = get_user_by_id(session['id'])
    return render_template("AboutUs.html", user=user)


@app.route('/mapPage', methods=["GET", "POST"])
@login_required
def mapPage():
    user = get_user_by_id(session['id'])
    try:
        if request.method == 'POST':
            start = request.form.get('start')
            finish = request.form.get('finish')

            points_sql = f'SELECT * FROM Object ' \
                         f'WHERE Object.name LIKE "{start}"' \
                         f'OR Object.name LIKE "{finish}"'
            cursor.execute(points_sql)
            points_results = cursor.fetchall()

            start_latitude = points_results[0][3]
            start_longitude = points_results[0][2]

            finish_latitude = points_results[1][3]
            finish_longitude = points_results[1][2]

            create_route_sql = f"INSERT INTO Route (user_id, date, rating, " \
                               f"start_name, start_longitude, start_latitude, " \
                               f"finish_name, finish_longitude, finish_latitude) " \
                               f"VALUES({user.id}, {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}, 0, " \
                               f"'{start}', {start_longitude}, {start_latitude}, " \
                               f"'{finish}', {finish_longitude}, {finish_latitude})"
            cursor.execute(create_route_sql)
            connection.commit()

            get_current_route_id_sql = 'SELECT id FROM Route ORDER BY id DESC LIMIT 1'
            cursor.execute(get_current_route_id_sql)
            current_route_id = cursor.fetchall()

            start_place = Place(id=points_results[0][0],
                                name=points_results[0][1],
                                longitude=start_longitude,
                                latitude=start_latitude)

            finish_place = Place(id=points_results[1][0],
                                 name=points_results[1][1],
                                 longitude=finish_longitude,
                                 latitude=finish_latitude)

            algo = MapWay()
            points = [start_place, finish_place]
            route = list(algo.findBestWay(user=user, points=points, number_of_places=10))

            object_sql_append = ''
            object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                         f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                         f"INNER JOIN Category C on OC.category_id = C.id "

            object_results = []
            object_position = 0
            for place in route:
                create_object_in_route_sql = "INSERT INTO ObjectInRoute " \
                                             "(position, object_id, route_id) " \
                                             f"VALUES ({object_position}, {place.id}, {current_route_id[0][0]})"
                cursor.execute(create_object_in_route_sql)
                connection.commit()

                object_sql_append = f"WHERE Object.name = '{place.name}'"
                sql = object_sql + object_sql_append
                cursor.execute(sql)
                object_results.append(cursor.fetchall())
                object_position += 1
    except Exception as e:
        return redirect(url_for('error'))
    return render_template('MapPage.html', user=user, object_results=object_results,
                           current_route=current_route_id[0][0])


@app.route('/tariffPay')
@login_required
def tariffPay():
    user = get_user_by_id(session['id'])
    return redirect(url_for('payments'))


@app.route('/payments')
@login_required
def payments():
    if request.method == 'GET':
        user = get_user_by_id(session['id'])
        subscription_level = request.args.get('tariff')
        tariff_sql = f'UPDATE User SET subscription_level = {subscription_level} WHERE id = {user.id}'
        cursor.execute(tariff_sql)
        connection.commit()
    return render_template('Payments.html', user=user)


@app.route('/tariffs')
@login_required
def tariffs():
    user = get_user_by_id(session['id'])
    return render_template('PlansPage.html', user=user)


# ссылки + работа с базой (объект и маршрут)
@app.route('/rateObject')
@login_required
def rateObject():
    user = get_user_by_id(session['id'])
    return render_template('RateObject.html', user=user)


# ссылки + работа с базой (маршрут)
@app.route('/rateRoute')
@login_required
def rateRoute():
    user = get_user_by_id(session['id'])
    return render_template('RateRoute.html', user=user)


@app.route("/privacy", methods=["GET", "POST"])
@login_required
def privacy():
    success = False
    error = None
    user_object = get_user_by_id(session['id'])
    if request.method == "POST":
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")
        if password and password_repeat and password == password_repeat:
            password = sha256(password.encode("utf-8")).hexdigest()
            query = f"UPDATE User SET password_hash='{password}' WHERE id={user_object.id};"
            try:
                db.execute(query)
                connection.commit()
                success = True
            except Exception as e:
                print(e)
                error = "Пароль не соответствует требованиям!"
        else:
            error = "Пароли либо не заполнены, либо не совпадают"
    return render_template('ChangePassword.html', user=user_object, error=error, success=success)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    error = None
    user_object = get_user_by_id(session['id'])
    if request.method == "POST":
        name = request.form.get("name") if request.form.get("name") is not None else user_object.name
        surname = request.form.get("surname") if request.form.get("surname") is not None else user_object.surname
        email = request.form.get("email") if request.form.get("email") is not None else user_object.email
        birthday = request.form.get("birthday") if request.form.get("birthday") is not None else user_object.birthday
        fields = []
        if name != user_object.name:
            fields.append(f"name='{name}'")
        if surname != user_object.surname:
            fields.append(f"surname='{surname}'")
        if email != user_object.email:
            fields.append(f"email='{email}'")
        if birthday != user_object.birthday:
            fields.append(f"birthday='{birthday}'")
        if len(fields) > 0:
            query = "UPDATE User SET " + ",".join(fields) + f" WHERE id={user_object.id}"
            try:
                db.execute(query)
                connection.commit()
            except Exception as e:
                print(e)
                error = "Невозможно изменить данные! Проверьте правильность введённых данных!"
            user_object = get_user_by_id(session['id'])
    avatar_path = Gravatar(user_object.email).get_image(size=512)
    return render_template("UserPage.html", user=user_object, avatar=avatar_path, error=error)


@app.route('/error')
def error():
    return render_template('Error.html')


if __name__ == "__main__":
    app.run()
