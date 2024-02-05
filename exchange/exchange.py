from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import dotenv_values
import mysql.connector, hashlib

config = dotenv_values(".env")

app = Flask(__name__)

try:
    mydb = mysql.connector.connect(
        host=config["SQLHOST"],
        user=config["SQLUSER"],
        password=config["SQLPASSWORD"],
        port=config["SQLPORT"]
    )
except:
    print("Unable to connect to MySQL database. Exiting program.")
    exit()

mycursor = mydb.cursor()

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["300000 per day", "36000 per hour"]
)

# ==================================
# MySQL Table initialization
# ==================================
def createTables():
    mycursor.execute("SHOW TABLES LIKE 'users'")
    if not mycursor.fetchone():
        print("User table does not exist, creating...")
        mycursor.execute("CREATE TABLE users (account_id BIGINT NOT NULL, balance DOUBLE, private_key VARCHAR(255), PRIMARY KEY (account_id))")
        # account_id DOUBLE
        # balance BIGINT
        # private_key VARCHAR(255)

        sql = "INSERT INTO users (account_id, balance, private_key) VALUES (%s, %s, %s)"
        val = [
        (1, 1000, 'abc123'),
        (2, 20000, 'ijk123'),
        (3, 123456789, 'xyz123')
        ]

        mycursor.executemany(sql, val)
        mydb.commit()

    mycursor.execute("SHOW TABLES LIKE 'apikeys'")
    if not mycursor.fetchone():
        print("API Keys table does not exist, creating...")
        mycursor.execute("CREATE TABLE apikeys (api_key VARCHAR(255), account_id BIGINT, FOREIGN KEY (account_id) REFERENCES users(account_id))")
        # api_key VARCHAR(255)
        # account_id BIGINT

        sql = "INSERT INTO apikeys (api_key, account_id) VALUES (%s, %s)"
        val = [
        ('123', 1),
        ('456', 2),
        ('789', 3),
        ]
        
        mycursor.executemany(sql, val)
        mydb.commit()

    mycursor.execute("SHOW TABLES LIKE 'orders'")
    if not mycursor.fetchone():
        print("Order table does not exist, creating...")
        mycursor.execute("CREATE TABLE orders (symbol VARCHAR(255), side VARCHAR(255), type VARCHAR(255), quantity DOUBLE, price DOUBLE, time_in_force VARCHAR(255), account_id BIGINT, FOREIGN KEY (account_id) REFERENCES users(account_id))")
        # symbol VARCHAR(255)
        # side VARCHAR(255)
        # type VARCHAR(255)
        # quantity DOUBLE
        # price DOUBLE
        # time_in_force VARCHAR(255)
        # account_id BIGINT

try:
    mycursor.execute("USE exchange")
except:
    print("Database does not exist, creating...")
    mycursor.execute("CREATE DATABASE exchange")
    mycursor.execute("USE exchange")
print("Connected to exchange database")
createTables()

# ==================================
# Server Routes
# ==================================

# Root. Test to see if the server is running.
@app.route("/")
@limiter.limit("10 per second")
def welcome():
    return "Welcome to the Cinance Exchange!"

# Order route, rate limited to 1 request per 100 milliseconds.
@app.route("/api/order", methods = ['POST'])
@limiter.limit("10 per second")
def order():
    try:
        # Fetch account info based on API key
        apiKey = request.headers.get("X-MBX-APIKEY")
        mycursor.execute('SELECT account_id FROM apikeys WHERE api_key = %s', (apiKey,))
        accountId = mycursor.fetchone()[0]
        mycursor.execute('SELECT * FROM users WHERE account_id = %s', (accountId,))
        accountInfo = mycursor.fetchone()

        # Verify private key
        data = request.form.to_dict()
        hashObject = hashlib.sha256()
        privateKey = accountInfo[2]
        hashObject.update(privateKey.encode())
        hashPassword = hashObject.hexdigest()
        if not data['signature'] == hashPassword:
            return "Bad request", 400
        
        # Check balance
        balance = accountInfo[1]
        price = float(data["price"])
        quantity = float(data["quantity"])
        value = round(price * quantity,10)
        print(f"Balance: {balance}, Price: {price}, Quantity: {quantity}, Total: {value}")
        if (balance < value):
            return "Insufficient balance", 400
        
        # Deduct balance from account
        newBalance = round(balance - value,10)
        mycursor.execute('UPDATE users SET balance = %s WHERE account_id = %s', (newBalance, accountId))

        # Generate new order
        mycursor.execute('INSERT INTO orders VALUES (%s, %s, %s, %s, %s, %s, %s)', (data["symbol"], data["side"], data["type"], data["quantity"], data["price"], data["timeInForce"], accountId))
        mydb.commit()

        response = jsonify(message='Order placed', balance=round(newBalance,2))
        return response
    except:
        return "Bad request", 400

# Test order route, rate limited to 1 request per 100 milliseconds. Does not save anything to DB.
@app.route("/api/order_test", methods = ['POST'])
@limiter.limit("10 per second")
def order_test():
    try:
        # Fetch account info based on API key
        apiKey = request.headers.get("X-MBX-APIKEY")
        mycursor.execute('SELECT account_id FROM apikeys WHERE api_key = %s', (apiKey,))
        accountId = mycursor.fetchone()[0]
        mycursor.execute('SELECT * FROM users WHERE account_id = %s', (accountId,))
        accountInfo = mycursor.fetchone()

        # Verify private key
        data = request.form.to_dict()
        hashObject = hashlib.sha256()
        privateKey = accountInfo[2]
        hashObject.update(privateKey.encode())
        hashPassword = hashObject.hexdigest()
        if not data['signature'] == hashPassword:
            return "Bad request", 400
        
        # Check balance
        balance = accountInfo[1]
        price = float(data["price"])
        quantity = float(data["quantity"])
        value = round(price * quantity,10)
        print(f"Balance: {balance}, Price: {price}, Quantity: {quantity}, Total: {value}")
        if (balance < value):
            return "Insufficient balance", 400

        response = jsonify(message='Test order placed', balance=round(balance - value,2))
        return response
    except:
        return "Bad request", 400
    
# Reset all DBs to their starting state.
@app.route("/api/reset")
def reset():
    mycursor.execute("DROP TABLE IF EXISTS apikeys")
    mycursor.execute("DROP TABLE IF EXISTS orders")
    mycursor.execute("DROP TABLE IF EXISTS users")
    createTables()
    print("Tables reset")
    return "Tables reset"