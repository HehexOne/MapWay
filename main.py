from functools import wraps

from flask import Flask, request, render_template, redirect, url_for, session
from mysql.connector import connect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, EqualTo
from hashlib import sha256
from newMapWay import *
from libgravatar import Gravatar
from geocoding import Geocoder
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sup3rsecr3tp@ssw0rd'
gc = Geocoder()


from database_structures_and_functions import *


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
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    if session.get('id') is None:
        return render_template("Landing.html")
    else:
        user = get_user_by_id(session['id'])

        if request.method == 'POST':
            try:
                if user.subscription_level == 0:
                    number_of_places = 2
                elif user.subscription_level == 1:
                    number_of_places = 6
                else:
                    number_of_places = 10

                start = request.form.get('start')
                finish = request.form.get('finish')

                if not start and not finish:
                    return redirect(url_for('error'))

                start_point = gc.get_coords(start)
                finish_point = gc.get_coords(finish)

                if "Россия, Москва" not in start_point[2] or "Россия, Москва" not in finish_point[2]:
                    return redirect(url_for('error'))

                start_latitude = start_point[1]
                start_longitude = start_point[0]

                finish_latitude = finish_point[1]
                finish_longitude = finish_point[0]

                create_route_sql = f"INSERT INTO Route (user_id, date, rating, " \
                                   f"start_name, start_longitude, start_latitude, " \
                                   f"finish_name, finish_longitude, finish_latitude) " \
                                   f"VALUES({user.id}, {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}, 0, " \
                                   f"'{start_point[2]}', {start_longitude}, {start_latitude}, " \
                                   f"'{finish_point[2]}', {finish_longitude}, {finish_latitude})"
                cursor.execute(create_route_sql)
                connection.commit()

                get_current_route_id_sql = 'SELECT LAST_INSERT_ID();'
                cursor.execute(get_current_route_id_sql)
                current_route_id = cursor.fetchone()[0]

                start_place = Place(name=start_point[2],
                                    longitude=start_longitude,
                                    latitude=start_latitude)

                finish_place = Place(name=finish_point[2],
                                     longitude=finish_longitude,
                                     latitude=finish_latitude)

                algo = MapWay()
                points = [start_place, finish_place]
                route = list(algo.findBestWay(points=points, number_of_places=number_of_places))

                object_position = 0

                for place in route:
                    if place.id is None:
                        continue

                    query = f"INSERT INTO ObjectInRoute (position, object_id, route_id) VALUES" \
                            f" ({object_position}, {place.id}, {current_route_id})"
                    cursor.execute(query)
                    connection.commit()
                    object_position += 1
                return redirect(f"/mapPage/{current_route_id}")
            except Exception as e:
                print(e)
                return redirect(url_for('error'))
        return render_template("Main.html", user=user)


@app.errorhandler(404)
@app.route("/not_found")
def not_found(err):
    return "Not found!", 404


@app.route("/login", methods=["GET", "POST"])
def login():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
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
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
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
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    page = request.args.get('page', 1, type=int)

    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                 f"INNER JOIN Category C on OC.category_id = C.id " \
                 f"ORDER BY Object.id " \
                 f"LIMIT 3 OFFSET {(page - 1) * 3} "

    search_input = None
    sort = request.args.get('sort')
    filter = request.args.get('filter')

    if request.method == 'POST':
        if request.form.get('search_input'):
            search_input = request.form.get('search_input')
            object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                         f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                         f"INNER JOIN Category C on OC.category_id = C.id " \
                         f"WHERE Object.name LIKE '%{search_input}%' " \
                         f"LIMIT 3 OFFSET {(page - 1) * 3} "

    if request.method == 'GET':
        if request.args.get('sort'):
            sort = request.args.get('sort')
            if sort == 'По имени':
                sort_condition = 'name'
            elif sort == 'По рейтингу':
                sort_condition = 'rating'
            else:
                sort_condition = 'id'

            filter = request.args.get('filter')
            print(sort_condition, filter)
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
                             f"ORDER BY Object.{sort_condition} LIMIT 3 OFFSET {(page - 1) * 3}"

    cursor.execute(object_sql)
    object_results = cursor.fetchall()

    category_sql = f"SELECT * FROM Category"
    cursor.execute(category_sql)
    category_results = cursor.fetchall()

    get_rating_by_review_sql = "SELECT *, ROUND((SELECT IFNULL(SUM(Review.rating) / COUNT(Review.rating), 0) FROM Review " \
                               "INNER JOIN ObjectInRoute OIR on Review.object_in_route = OIR.id " \
                               "WHERE object_id=Object.id), 2) as `rating` FROM Object LIMIT 3;"
    cursor.execute(get_rating_by_review_sql)
    get_rating_by_review = cursor.fetchall()

    return render_template('Objects.html', object_results=object_results,
                           page=page, user=user, category_results=category_results,
                           search_input=search_input, sort=sort,
                           filter=filter, rating=get_rating_by_review)


# решить проблему с комментами
@app.route("/object")
def object():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    id = request.args.get('id', 1, type=int)

    object_sql = f"SELECT Object.id, Object.name, longitude, latitude, image_url, description, rating, age_restriction_level, C.name as 'category_name' FROM Object " \
                 f"INNER JOIN ObjectCategory OC on Object.id = OC.object_id " \
                 f"INNER JOIN Category C on OC.category_id = C.id " \
                 f"WHERE Object.id = {id}"
    cursor.execute(object_sql)
    object_results = cursor.fetchall()

    object_comments_sql = f"SELECT Review.id, Review.text, Review.rating, O.id as 'object_id', U.name as 'user_name' FROM Review " \
                          f"INNER JOIN ObjectInRoute OIR on Review.object_in_route = OIR.id " \
                          f"INNER JOIN Object O on OIR.object_id = O.id " \
                          f"INNER JOIN Route R on OIR.route_id = R.id " \
                          f"INNER JOIN User U on R.user_id = U.id " \
                          f"WHERE O.id = {id}"
    cursor.execute(object_comments_sql)
    object_comments_results = cursor.fetchall()

    get_object_rating = "SELECT ROUND((SELECT IFNULL(SUM(Review.rating) / COUNT(Review.rating), 0) FROM Review " \
                        "INNER JOIN ObjectInRoute OIR on Review.object_in_route = OIR.id " \
                        f"WHERE object_id={id}), 2)"
    cursor.execute(get_object_rating)
    object_rating = cursor.fetchall()[0][0]

    return render_template('Object.html', id=id, object_results=object_results,
                           object_comments=object_comments_results, user=user,
                           object_rating=object_rating)


@app.route("/aboutUs")
def about():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    if session.get('id') is None:
        return render_template("AboutUs_landing.html")
    else:
        user = get_user_by_id(session['id'])
        return render_template("AboutUs.html", user=user)


@app.route('/mapPage/<int:ident>', methods=["GET", "POST"])
@login_required
def mapPage(ident):
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    try:
        query = f"SELECT * FROM Route WHERE id={ident}"
        cursor.execute(query)

        route_data = cursor.fetchone()

        connection.commit()

        if route_data[1] != user.id:
            return redirect(url_for("not_found"))

        query = f"SELECT O.id, O.name, O.longitude, O.latitude, O.image_url, O.description, C.name," \
                f"(SELECT ROUND(IFNULL(SUM(Review.rating) / COUNT(Review.rating), 0), 2)" \
                f"FROM Review " \
                f"INNER JOIN ObjectInRoute OIR on Review.object_in_route = OIR.id " \
                f"WHERE object_id=O.id) as `rating`, ObjectInRoute.id " \
                f"FROM ObjectInRoute " \
                f"INNER JOIN Object O on ObjectInRoute.object_id = O.id " \
                f"INNER JOIN ObjectCategory OC on O.id = OC.object_id " \
                f"INNER JOIN Category C ON OC.category_id = C.id " \
                f"WHERE route_id={ident} ORDER BY ObjectInRoute.position"
        cursor.execute(query)

        objects_collection = cursor.fetchall()
        connection.commit()

        route_start = [route_data[6], route_data[5], route_data[4]]
        route_end = [route_data[9], route_data[8], route_data[7]]

        points_for_map = [route_start]
        for place in objects_collection:
            points_for_map.append([place[2], place[3], place[1]])
        points_for_map.append(route_end)

        js_map_points = []

        for i in range(len(points_for_map)):
            pnt = points_for_map[i]
            js_map_points.append("""myMap.geoObjects.add(new ymaps.Placemark([""" + str(pnt[0]) + ',' + str(pnt[1]) + """], {
            balloonContent: '""" + pnt[2] + """',
            iconCaption: '""" + str(i + 1) + """'
        }, {
            preset: 'islands#greenDotIconWithCaption'
        }));""")
        return render_template('MapPage.html', user=user, object_results=objects_collection,
                               current_route=ident,
                               start_point=route_start, finish_point=route_end,
                               points=js_map_points)
    except Exception as e:
        print(e)
        return redirect(url_for('error'))


@app.route('/tariffPay')
@login_required
def tariffPay():
    return redirect(url_for('payments'))


@app.route('/payments')
@login_required
def payments():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    subscription_level = request.args.get('tariff')
    if subscription_level:
        tariff_sql = f'UPDATE User SET subscription_level = {subscription_level} WHERE id = {user.id}'
        cursor.execute(tariff_sql)
        connection.commit()
    return render_template('Payments.html', user=user)


@app.route('/tariffs')
@login_required
def tariffs():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    return render_template('PlansPage.html', user=user)


# ссылки + работа с базой (объект и маршрут)
@app.route('/rateObject', methods=['GET', 'POST'])
@login_required
def rateObject():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    object_in_route_id = request.args.get('id')

    query = f"SELECT route_id FROM ObjectInRoute WHERE id={object_in_route_id}"
    cursor.execute(query)
    route_id = cursor.fetchone()[0]
    connection.commit()

    if request.method == 'POST':
        rate_object = request.form.get('rate')
        review = request.form.get('review')

        create_review_sql = f'INSERT INTO Review (object_in_route, ' \
                            f'text, rating) VALUES ({object_in_route_id}, ' \
                            f'\'{review}\', {rate_object})'
        cursor.execute(create_review_sql)
        connection.commit()

    return render_template('RateObject.html', user=user, route_id=route_id)


# ссылки + работа с базой (маршрут)
@app.route('/rateRoute', methods=['GET', 'POST'])
@login_required
def rateRoute():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])
    current_route_id = request.args.get('id')

    if request.method == 'POST':
        rate_route = request.form.get('rate')

        rate_current_route_sql = f'UPDATE Route SET rating = {rate_route} ' \
                                 f'WHERE id = {current_route_id}'
        cursor.execute(rate_current_route_sql)
        connection.commit()

    return render_template('RateRoute.html', user=user, route_id=current_route_id)


@app.route("/privacy", methods=["GET", "POST"])
@login_required
def privacy():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
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
                cursor.execute(query)
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
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
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
                cursor.execute(query)
                connection.commit()
            except Exception as e:
                print(e)
                error = "Невозможно изменить данные! Проверьте правильность введённых данных!"
            user_object = get_user_by_id(session['id'])
    avatar_path = Gravatar(user_object.email).get_image(size=512)
    return render_template("UserPage.html", user=user_object, avatar=avatar_path, error=error)


@app.route("/myRoutes")
@login_required
def user_routes():
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    user = get_user_by_id(session['id'])

    query = f"SELECT *, (SELECT COUNT(*) FROM ObjectInRoute WHERE route_id=Route.id) " \
            f"FROM Route WHERE user_id={user.id} ORDER BY date DESC"
    cursor.execute(query)
    routes = cursor.fetchall()
    connection.commit()

    return render_template("List.html", user=user, user_routes=routes)


@app.route('/error')
def error():
    return render_template('Error.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
