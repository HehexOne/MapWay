DROP TABLE Review, ObjectInRoute, Route, ObjectTag, Tag,
    ObjectCategory, Category, Object, User;

CREATE TABLE User (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128),
    surname VARCHAR(128),
    email VARCHAR(128) UNIQUE,
    password_hash VARCHAR(256),
    rights_level INT UNSIGNED,
    subscription_level INT UNSIGNED,
    birthday DATE
);

CREATE TABLE Object (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256),
    longitude DOUBLE,
    latitude DOUBLE,
    image_url VARCHAR(256),
    description VARCHAR(2048),
    rating FLOAT UNSIGNED,
    # Age restriction levels 0+, 6+, 12+, 16+, 18+
    age_restriction_level INT
);

CREATE TABLE Category (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256)
);

CREATE TABLE ObjectCategory (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    object_id INT UNSIGNED,
    category_id INT UNSIGNED,
    FOREIGN KEY (object_id) REFERENCES Object(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Category(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Tag (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(32)
);

CREATE TABLE ObjectTag (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    object_id INT UNSIGNED,
    tag_id INT UNSIGNED,
    FOREIGN KEY (object_id) REFERENCES Object(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tag(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Route (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED,
    date DATETIME DEFAULT NOW(),
    rating FLOAT UNSIGNED,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ObjectInRoute (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    position INT UNSIGNED,
    object_id INT UNSIGNED,
    route_id INT UNSIGNED,
    FOREIGN KEY (object_id) REFERENCES Object(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (route_id) REFERENCES Route(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Review (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    object_in_route INT UNSIGNED,
    text VARCHAR(1024),
    rating INT UNSIGNED,
    FOREIGN KEY (object_in_route) REFERENCES ObjectInRoute(id) ON DELETE CASCADE ON UPDATE CASCADE
);