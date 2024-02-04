import csv
from dotenv import dotenv_values

config = dotenv_values(".env")

# Load Precision.csv into precision dictionary
precisionFile = open('Precision.csv', newline='')
precisionFile = csv.reader(precisionFile, delimiter=',')

precision = {}

next(precisionFile, None) # Skip header
for row in precisionFile:
    precision[row[0]] = {"pricePrecision": row[1], "quantityPrecision": row[2]}

# Load Orders.csv into orders list
ordersFile = open('Orders.csv', newline='')
ordersFile = csv.reader(ordersFile, delimiter=',')

orders = []
# Pair / Direction / Price / Quantity / Account / Value
# JTOUSDT / BUY / 1.7101 / 8.000 / 3 / 13.68
next(ordersFile, None) # Skip header
for row in ordersFile:
    orders.append({"pair": row[0], "direction": row[1], "price": row[2], "quantity": row[3], "account": row[4], "value": row[5]})

keystroke = input(f"{len(precision)} accounts and {len(orders)} orders loaded. Proceed? (Y/N): ")

while True:
    if keystroke == "N".casefold():
        exit()
    elif keystroke == "Y".casefold():
        print("Proceed")
        break
    else:
        keystroke = input("Please input Y or N: ")

print(config["DOMAIN"])