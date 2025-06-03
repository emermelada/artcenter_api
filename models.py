import pymysql
from flask import current_app

def get_connection():
    return pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        db=current_app.config["MYSQL_DB"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
        autocommit=True
    )
