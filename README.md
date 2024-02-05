# Exchange Simulation

A minimal application in Python, simulating the interaction between an API end-user and online exchange server. The end-user runs a script to place consecutive orders from a number of accounts, and the server processes these orders as long as the user has an adequate balance. The API format used is based on Binance's API endpoints.

## Required External Dependencies

### Client-side
- [requests](https://pypi.org/project/requests/)
- [dotenv](https://pypi.org/project/python-dotenv/)

### Server-side
- [flask](https://pypi.org/project/Flask/)
- [flask-limiter](https://pypi.org/project/Flask-Limiter/)
- [dotenv](https://pypi.org/project/python-dotenv/)
- [mysql.connector](https://pypi.org/project/mysql-connector-python/)
- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)

## Installation / Setup
Install all required Python dependencies using Pip.

MySQL Workbench should be downloaded and installed with a generic setup.
A local SQL instance will need to be created and run on the hosting server computer. In the .env file in the **exchange folder**, replace the variables with your own hosted instance's variables.
- SQLHOST (Server's IP address)
- SQLPORT (Port assigned to SQL instance)
- SQLUSER (Username for SQL instance. This user should have the appropriate permissions to modify the database)
- SQLPASSWORD (Password for SQL instance)

In the .env file in the **client folder**, modify the ENDPOINT and ENDPOINT_TEST variables to fit your server's IP address and port. If both client and server are being run on the same computer, no modification is necessary.

## Usage - Server
Your MySQL instance must be running before starting up the server.

To run the server, navigate to the **exchange folder** on your terminal and input:
> python -m flask --app exchange run

Order endpoints are rate limited to 10 requests per second. The API endpoints are as follow:
- /api/order
- /api/order_test

Upon server startup, the program will check if your exchange database exists, and if it doesn't, will generate a new database and tables with pre-populated users and API keys.

To reset the database, navigate on your web browser to:
> http://[IP address]:[host]/api/reset

## Usage - Client
The server must first be running in order for the client to interact with it.

To run the client, navigate to the **client folder** on your terminal and input:
> python client.py

The Orders.csv and Precision.csv files will be summary of # of orders and # of users will be given.

The end-user can then choose **[Y]** to proceed with sending actual orders, **[T]** to send simulated test orders that do not affect the server's databases, or **[N]** to cancel.

For every order sent, the end-user will receive a response for whether the order placement succeeded or failed.

- Successful responses return a success message and the account's new balance after placing the order
- Failed responses return a message on why the order failed, and prints out the details of the order
