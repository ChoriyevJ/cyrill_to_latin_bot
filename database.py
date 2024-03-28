import sqlite3 as sql

db = sql.connect('database.db', check_same_thread=False)
cursor = db.cursor()

# cursor.executescript(
#     """
#     drop table if exists message;
#     drop table if exists user;
#     create table if not exists user (
#         id integer primary key autoincrement,
#         user_id integer,
#         first_name varchar(50),
#         username varchar(50)
#     );
#
#     create table if not exists message (
#         id integer primary key autoincrement,
#         message_id integer,
#         content text,
#         translated_content text,
#         user_id integer references users(id)
#     );
#     """
# )

