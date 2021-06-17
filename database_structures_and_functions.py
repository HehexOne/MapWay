from main import connect
from hashlib import sha256


def insert_query_get_id(query):
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    cursor.execute(query)
    connection.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    return cursor.fetchone()[0]


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
    return insert_query_get_id(query)


def get_user_by_credentials(email, password):
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    query = f"SELECT * FROM User WHERE email='{email}' AND password_hash='{password_hash}' LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    connection.commit()
    if result:
        # Converting database response to object
        return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    else:
        return None


def get_user_by_id(ident):
    connection = connect(host="std-mysql", username="std_1450_mw", password="11223344")
    cursor = connection.cursor()
    cursor.execute("USE std_1450_mw;")
    connection.commit()
    query = f"SELECT * FROM User WHERE id={ident} LIMIT 1;"
    cursor.execute(query)
    result = cursor.fetchone()
    connection.commit()
    if result:
        return User(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    else:
        return None
