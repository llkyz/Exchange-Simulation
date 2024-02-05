import csv, time, requests, hashlib
from dotenv import dotenv_values

config = dotenv_values(".env")

# ==================================
# Load API endpoints
# ==================================

endpoint = config["ENDPOINT"]
endpointTest = config["ENDPOINT_TEST"]

# ==================================
# Load Orders and Precision files
# ==================================

# Load Precision.csv into precision dictionary
precisionFile = open('Precision.csv', newline='')
precisionFile = csv.reader(precisionFile, delimiter=',')

users = {}

next(precisionFile, None) # Skip header
for row in precisionFile:
    users[row[0]] = {"pricePrecision": row[1], "quantityPrecision": row[2]}

# Load Orders.csv into orders list
ordersFile = open('Orders.csv', newline='')
ordersFile = csv.reader(ordersFile, delimiter=',')

orders = []
# Pair / Direction / Price / Quantity / Account / Value
# JTOUSDT / BUY / 1.7101 / 8.000 / 3 / 13.68
next(ordersFile, None) # Skip header
for row in ordersFile:
    orders.append({"pair": row[0], "direction": row[1], "price": row[2], "quantity": row[3], "account": row[4]})

# ==================================
# Await user input
# ==================================
    
# [Y] = Actual orders. [T] = Test orders. [N] = Abort
keystroke = input(f"{len(users)} accounts and {len(orders)} orders loaded. To proceed, input Y. To do a test run, input T. To abort, input N: ")

while True:
    if keystroke.casefold() == "n":
        exit()
    elif keystroke.casefold() == "y":
        print("Proceeding with order placement")
        break
    elif keystroke.casefold() == "t":
        print("Running test order placement")
        break
    else:
        keystroke = input("Please input Y, T, or N: ")

# ==================================
# Load private keys, API keys, and API endpoint
# ==================================

# For simulation purposes, the private key is stored unencrypted in the .env file
users["1"]["privateKey"] = config["PRIVATE_KEY1"]
users["1"]["apiKey"] = config["API_KEY1"]

users["2"]["privateKey"] = config["PRIVATE_KEY2"]
users["2"]["apiKey"] = config["API_KEY2"]

users["3"]["privateKey"] = config["PRIVATE_KEY3"]
users["3"]["apiKey"] = config["API_KEY3"]


# ==================================
# Order execution
# ==================================
        
for order in orders:
    # Round price and quantity to specified decimal places
    pricePrecision = int(users[order["account"]]["pricePrecision"])
    quantityPrecision = int(users[order["account"]]["quantityPrecision"])
    order["price"] = round(float(order["price"]), pricePrecision)
    order["quantity"] = round(float(order["quantity"]), quantityPrecision)

    # Add request headers
    headers = {
	    "X-MBX-APIKEY": users[order["account"]]["apiKey"]
    }

    # Add request params
    params = {
        "symbol": order["pair"],
	    "side": order["direction"],
	    "type": "LIMIT",
	    "quantity": str(order["quantity"]),
	    "price": str(order["price"]),
	    "timeInForce": "GTC"
    }

    # Add timestamp
    timestamp = int(time.time() * 1000) # UNIX timestamp in milliseconds
    params['timestamp'] = timestamp

    # Sign request using a simulated encryption method
    hashObject = hashlib.sha256()
    hashObject.update(users[order["account"]]["privateKey"].encode())
    hashPassword = hashObject.hexdigest()
    params['signature'] = hashPassword

    # Send request to API endpoint
    try:
        if keystroke.casefold() == "y": # Actual order
            response = requests.post(endpoint, headers=headers, data=params)
        elif keystroke.casefold() == "t": # Test order
            response = requests.post(endpointTest, headers=headers, data=params)
        if (response.ok):
            json = response.json()
            print(f"[{json['message']}] AccountID: {order['account']}, Balance: {json['balance']}")
        else:
            print(f"[Failed: {response.text}] AccountID: {order['account']}, {order['pair']} {order['quantity']} @ ${order['price']}")
    except requests.exceptions.Timeout:
        print(f"[Failed: Request timed out] AccountID: {order['account']}, {order['pair']} {order['quantity']} @ ${order['price']}")
    time.sleep(0.1) # Sleep 100ms to adhere to API rate limit

if keystroke.casefold() == "y":
    print("Order placement complete")
elif keystroke.casefold() == "t":
    print("Test order placement complete")