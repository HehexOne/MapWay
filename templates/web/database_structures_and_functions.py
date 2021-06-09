from mysql.connector import connect
from hashlib import sha256

connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
db = connection.cursor()
db.execute("USE std_1450_mw;")
connection.commit()

def insert_query_get_id(query):
    db.execute(query)
    connection.commit()
    db.execute("SELECT LAST_INSERT_ID()")
    return db.fetchone()[0]


def select_query_fetchone(query):
    db.execute(query)
    return db.fetchone()


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


class Category:

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Object:

    def __init__(self, id, name, longitude, latitude, image_url, description, rating, age_restriction_level):
        self.id = id
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.image_url = image_url
        self.description = description
        self.rating = rating
        self.age_restriction_level = age_restriction_level


class ObjectCategory:

    def __init__(self, id, object_id, category_id):
        self.id = id
        self.object_id = object_id
        self.category_id = category_id


class ObjectInRoute:

    def __init__(self, id, position, object_id, route_id):
        self.id = id
        self.position = position
        self.object_id = object_id
        self.route_id = route_id


class ObjectTag:

    def __init__(self, id, object_id, tag_id):
        self.id = id
        self.object_id = object_id
        self.tag_id = tag_id


class Review:

    def __init__(self, id, objet_in_route, text, rating):
        self.id = id
        self.object_in_route = objet_in_route
        self.text = text
        self.rating = rating


class Route:

    def __init__(self, id, user_id, date, rating):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.rating = rating


class Tag:

    def __init__(self, id, name):
        self.id = id
        self.name = name


def create_user_by_user_object(user_obj: User):
    query = f"INSERT INTO User (name, surname, email, password_hash, rights_level, subscription_level, birthday)" \
            f"VALUES ('{user_obj.name}', '{user_obj.surname}', '{user_obj.email}', '{user_obj.password_hash}'," \
            f"{user_obj.right_level}, {user_obj.subscription_level}, '{user_obj.birthday}');"
    return insert_query_get_id(query)


def get_user_by_credentials(email, password):
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    query = f"SELECT * FROM User WHERE email='{email}' AND password_hash='{password_hash}' LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        # Converting database response to object
        return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    else:
        return None


def get_user_by_id(ident):
    query = f"SELECT * FROM User WHERE id={ident} LIMIT 1;"
    result = select_query_fetchone(query)
    if result:
        return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    else:
        return None


def get_category_by_id(ident):
    query = f"SELECT * FROM Category WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return Category(result[0], result[1])
    else:
        return None


def create_category_by_category_object(category_object: Category):
    query = f"INSERT INTO Category (name) VALUES ('{category_object.name}')"
    return insert_query_get_id(query)


def get_object_by_id(ident):
    query = f"SELECT * FROM Object WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return Object(result[0],
                      result[1],
                      result[2],
                      result[3],
                      result[4],
                      result[5],
                      result[6],
                      result[7])
    else:
        return None


def create_object_by_object_object(object: Object):
    query = f"INSERT INTO Object (name, longitude, latitude, image_url," \
            f" description, rating, age_restriction_level) " \
            f"VALUES ('{object.name}', {object.longitude}, {object.latitude}," \
            f"'{object.image_url}', '{object.description}', {object.rating}," \
            f"{object.age_restriction_level})"
    return insert_query_get_id(query)


def get_object_category_by_id(ident):
    query = f"SELECT * FROM Category WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return ObjectCategory(result[0], result[1], result[2])
    else:
        return None


def create_object_category_by_object_category_object(object_category: ObjectCategory):
    query = f"INSERT INTO ObjectCategory (object_id, category_id)" \
            f" VALUES ({object_category.object_id}, {object_category.category_id})"
    return insert_query_get_id(query)


def get_object_in_route_by_id(ident):
    query = f"SELECT * FROM ObjectInRoute WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return ObjectInRoute(result[0],
                             result[1],
                             result[2],
                             result[3])
    else:
        return None


def create_object_in_route_by_Object_in_route_object(object_in_route: ObjectInRoute):
    query = f"INSERT INTO ObjectInRoute (position, object_id, route_id) " \
            f"VALUES ({object_in_route.position}, {object_in_route.object_id}," \
            f"{object_in_route.route_id})"
    return insert_query_get_id(query)


def get_object_tag_by_id(ident):
    query = f"SELECT * FROM ObjectTag WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return ObjectTag(result[0],
                         result[1],
                         result[2])
    else:
        return None


def create_object_tag_by_object_tag_object(object_tag: ObjectTag):
    query = f"INSERT INTO ObjectTag (object_id, tag_id) " \
            f"VALUES ({object_tag.object_id}, {object_tag.tag_id})"
    return insert_query_get_id(query)


def get_review_by_id(ident):
    query = f"SELECT * FROM Review WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return Review(result[0],
                      result[1],
                      result[2],
                      result[3])
    else:
        return None


def create_review_by_review_object(review_object: Review):
    query = f"INSERT INTO Review (object_in_route, text, rating) " \
            f"VALUES ({review_object.object_in_route}," \
            f" '{review_object.text}', {review_object.rating})"
    return insert_query_get_id(query)


def get_route_by_id(ident):
    query = f"SELECT * FROM Route WHERE id={ident} LIMIT 1"
    result = select_query_fetchone(query)
    if result:
        return Route(result[0],
                     result[1],
                     result[2],
                     result[3])
    else:
        return None


def create_route_by_route_object(route_object: Route):
    query = f"INSERT INTO Route (user_id, date, rating) " \
            f"VALUES ({route_object.user_id}, '{route_object.date}', {route_object.rating})"
    return insert_query_get_id(query)


def get_tag_by_id(ident):
    query = f"SELECT * FROM Tag WHERE id={ident}"
    result = select_query_fetchone(query)
    if result:
        return Tag(result[0], result[1])
    else:
        return None


def create_tag_by_tag_object(tag_object: Tag):
    query = f"INSERT INTO Tag (name) VALUES ('{tag_object.name}')"
    return insert_query_get_id(query)
