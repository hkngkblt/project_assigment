
import copy
import json
from requests import Session
from flask import Flask, abort, request, Response

app = Flask(__name__)
app.config['SECRET_KEY'] = "helloworld"


# get usdt price with Coinmarketcap API
def get_usd_price():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'slug': 'tether',
        'convert': 'TRY'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '1656c8dc-ff25-480b-85c5-683679d9c12c'
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)[
        'data']['825']['quote']['TRY']['price']  # float price
    return data

@app.route('/')
def home():
    # if user login => redirect login
    # else redirect => homepage
    abort(Response("empty page",401))
    #return "<p>This site is a prototype API for assignment.</p>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    # login and redirect homepage
    abort(Response("empty page",401))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # register and redirect home
    abort(Response("empty page",401))

users = [
    {
        "id": 1,
        "wallet": 100.0,
        "username": "hakan",
        "password": "h1.",
        "preferred_currency": "TRY",
        "cart": []
    },
]

orders = [
]

items = [
    {"id": 1, "name": "orange", "price": 9},
    {"id": 2, "name": "blueberries", "price": 17},
    {"id": 3, "name": "strawberries", "price": 14},
    {"id": 4, "name": "apple", "price": 8},
    {"id": 5, "name": "banana", "price": 16}
]

# get items with preferred currency
@app.route('/api/v1/items/', methods=['GET'])
def get_items():
    try:
        preferred_currency = users[0]["preferred_currency"]

        if preferred_currency == 'TRY':
            return {'success': True, "msg": "items with TRY currency", "items": items}
        elif preferred_currency == 'USD':
            temp_arr = copy.deepcopy(items)
            for i in temp_arr:
                i['price'] = float(i['price']) / get_usd_price()
            return {'success': True, "msg": "items with USD currency", "items": temp_arr}
        else:
            return {'success': True, "msg": "Unvalid currency type"}
    except Exception as e:
        abort(Response(str(e), 401))

# toggle preferred currency USD and TRY
@app.route('/api/v1/toggle-preferred-currency/', methods=['GET'])
def toggle_currency():
    try:
        if users[0]["preferred_currency"] == "TRY":
            users[0]["preferred_currency"] = "USD"
            return {'success': True, "msg": "Preferrence changed to USD"}
        else:
            users[0]["preferred_currency"] = "TRY"
            return {'success': True, "msg": "Preferrence changed to TRY"}

    except Exception as e:
        abort(Response(str(e), 401))

# get user cart with preferred currency
@app.route('/api/v1/cart/', methods=['GET'])
def get_cart():
    try:
        cart = users[0]["cart"]
        if (len(cart) == 0):
            return {'success': True, "msg": "Your cart is empty"}

        total_amount_cart = 0

        for item in cart:
            total_amount_cart += item["price"]

        if users[0]["preferred_currency"] == "TRY":
            return {'success': True, "cart: ":cart, "total cart amount": total_amount_cart}
        else:
            usd_price = get_usd_price()
            temp_cart = copy.deepcopy(cart)

            for i in range(len(temp_cart)):
                temp_val = float(cart[i]["price"]) / usd_price
                temp_cart[i]["price"] = temp_val

            total_amount_cart = total_amount_cart / usd_price
            return {'success': True, "cart: ": temp_cart, "total cart amount": total_amount_cart}

    except Exception as e:
        abort(Response(str(e), 401))

# add item to cart
@app.route('/api/v1/add-item-to-cart/', methods=['POST'])
def add_item_to_cart():
    try:
        cart =  users[0]["cart"]
        for item in items:
            if item["id"] == int(request.args["id"]):
                cart.append(item)
                return {"succes": True, "msg": "Item added to cart"}

        return {"succes": True, "msg": "Entered invalid item id"}

    except Exception as e:
        abort(Response(str(e), 401))

# if request id available in cart delete it
@app.route('/api/v1/delete-item/', methods=['POST']) 
def delete_item_from_cart():
    try:
        cart =  users[0]["cart"]
        if (len(cart) == 0):
            return {'success': True, "msg": "Your cart is empty"}

        for i in range(len(cart)):
            if cart[i]["id"] == int(request.args["id"]):
                del cart[i]
                return {"succes": True, "msg": "Item deleted"}

        return {"succes": True, "msg": "Entered invalid item id"}

    except Exception as e:
        abort(Response(str(e), 401))

# if wallet amount is enough subtract from wallet and add to orders
@app.route('/api/v1/cart-checkout/', methods=['POST']) 
def cart_checkout():
    try:
        cart = users[0]["cart"]
        if (len(cart) == 0):
            return {'success': True, "msg": "Your cart is empty"}

        wallet_amount = users[0]["wallet"]
        total_amount_cart = 0

        for i in cart:
            total_amount_cart += i["price"]
        
        if total_amount_cart <= wallet_amount:
            order = {"user_id": users[0]["id"],"order_id": len(orders)+1 ,"price": total_amount_cart, "status": "created", "cart": cart}
            orders.append(order)
            users[0]["wallet"] -= total_amount_cart
            users[0]["cart"] = []
            return {'success': True, "msg": "Order created", "order id: ": len(orders)}
        else:
            return {'success': True, "msg": "Wallet not enough"}

    except Exception as e:
        abort(Response(str(e), 401))

# if request id available on orders set order status to delivering, if order status=cancel subtract from wallet
@app.route('/api/v1/courier-accept/', methods=['POST']) 
def courier_accept():
    try:
        if (len(orders) == 0):
            return {'success': True, "msg": "No active order"}

        for i in range(len(orders)):
            if orders[i]["order_id"] == int(request.args["id"]):
                if orders[i]["status"] == "cancel":
                    users[0]["wallet"] -= orders[i]["price"]

                orders[i]["status"] = "delivering"
                return {'success': True, "msg": "Order delivering"}

        return {"succes": True, "msg": "Entered invalid order id"}
    except Exception as e:
        abort(Response(str(e), 401))

# if request id available on orders set order status to cancel and buyback, if order status=cancel subtract from wallet
@app.route('/api/v1/courier-cancel/', methods=['POST']) 
def courier_canceled():
    try:
        if (len(orders) == 0):
            return {'success': True, "msg": "No active order"}

        for i in range(len(orders)):
            if (orders[i]["order_id"] == int(request.args["id"])) and (orders[i]["status"] != "cancel"):
                orders[i]["status"] = "cancel"
                users[0]["wallet"] += orders[i]["price"]
                return {'success': True, "msg": "Order canceled and amount payback"}

        return {"succes": True, "msg": "Entered invalid order id"}
    except Exception as e:
        abort(Response(str(e), 401))

# get orders status with preferred currency
@app.route('/api/v1/order-status/', methods=['GET'])  
def order_status():
    try:
        if (len(orders) == 0):
            return {'success': True, "msg": "You have no active order"}

        if users[0]["preferred_currency"] == "TRY":
            return {'success': True, "order": orders}
        else:
            usd_price = get_usd_price()
            temp_orders = copy.deepcopy(orders)

            for i in range(len(temp_orders)):
                temp_val = float(orders[i]["price"]) / usd_price
                temp_orders[i]["price"] = temp_val
            return {'success': True, "order": temp_orders}
    except Exception as e:
        abort(Response(str(e), 401))


# get user informations 
@app.route('/api/v1/user-info/', methods=['GET'])  
def user_info():
    try:
        if (len(users) == 0):
            return {'success': True, "user_info": "no user found"}
        
        if users[0]["preferred_currency"] == "TRY":
            return {'success': True, "msg": users[0]}
        else:
            temp_user = copy.deepcopy(users[0])
            temp_user["wallet"] /= get_usd_price()
            return {'success': True, "msg": temp_user}

    except Exception as e:
        abort(Response(str(e), 401))

if __name__ == "__main__":
    app.run(debug=True)
