DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS participant;
DROP TABLE IF EXISTS friend;
DROP TABLE IF EXISTS hobby;
DROP TABLE IF EXISTS alcohol;
DROP TABLE IF EXISTS smoke;
DROP TABLE IF EXISTS hobbys;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  gender TEXT,
  password TEXT NOT NULL
);

CREATE TABLE room (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE participant (
  user_id INTEGER NOT NULL,
  room_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (room_id) REFERENCES room (id)
);

CREATE TABLE friend (
  host_id INTEGER NOT NULL,
  guest_id INTEGER NOT NULL,
  FOREIGN KEY (host_id) REFERENCES user (id),
  FOREIGN KEY (guest_id) REFERENCES user (id)
);

CREATE TABLE hobby (
  user_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (category) REFERENCES hobbys (category)
);

CREATE TABLE alcohol (
  user_id INTEGER NOT NULL,
  degree TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE smoke (
  user_id INTEGER NOT NULL,
  degree TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE hobbys (
  category TEXT UNIQUE NOT NULL
)
