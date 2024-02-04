from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
import datetime
import os

app = Flask(__name__)

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="Test",
    password="abc123"
)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["300000 per day", "36000 per hour"]
)

@app.route("/")
@limiter.limit("10 per second")
def test():
    return "Hello"

@app.route("/seed_database_tables")
def seed_database_tables():
    return

@app.route("/")
def seed_accounts():
    return