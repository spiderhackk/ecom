
import datetime
from functools import wraps
import jwt
from flask import Flask, request, jsonify,session
from flask_cors import  CORS
from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client.shilajit
app = Flask(__name__)
app.config['SECRET_KEY']="hidude"
cors = CORS(app)
app.secret_key='rs'

def check_auth(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        token = None
        data = request.headers
        if 'Authorization' in data:
            token = data['Authorization']
        if not token:
            return jsonify("missing token"),403
        try:
            value=jwt.decode(token,app.config['SECRET_KEY'])
            user=value['email']
        except:
            return jsonify("invalid token"),403
        return func(user,*args,**kwargs)
    return wrapped




@app.route('/login', methods=['POST', 'GET'])
def logedin():
    login_data_req = request.get_json()
    email = login_data_req["email"]
    psw = login_data_req["psw"]

    name = db.user.find({'email': email, "psw": psw})
    if name.count() == 1:
        token = jwt.encode(
            {'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=240)},
            app.config['SECRET_KEY'])
        return jsonify("login succesfully", token.decode('UTF-8'), 201)
    else:
        return jsonify("username or password is incorrect"), 401



@app.route('/profile',methods=["POST","GET"])
@check_auth
def profile(user):
    email=user
    data_req = db.user.find({"email": email},
                            {"_id": 0, "name": 1, "email": 1, "gender": 1, "username": 1, "num": 1})
    user_data_list = []
    for i in data_req:
        user_data_list.append(i)
    return jsonify(user_data_list)


@app.route('/signup', methods=['POST', "GET"])
def signup():
    user_data = request.get_json()
    email = user_data["email"]
    sand = db.user.find({'email': email})
    if sand.count() > 0:
        return jsonify(err="Email already exsit"), 403
    psw = user_data['psw']
    num = user_data['num']
    name = user_data['username']
    gender = user_data['gender']
    db.user.insert_one({'email': email, 'psw': psw, 'num': num, 'username': name, 'gender': gender, "add": []})
    db.orderhistory.insert_one({"email": email})
    return jsonify({"message": "user created successfully"}), 200


@app.route('/category', methods=['POST', 'GET'])
@check_auth
def catogory_handler():
    get_category = (db.category.find({}, {"_id": 0}))
    list_category = []
    for i in get_category:
        list_category.append(i)
    return jsonify(list_category)


@app.route('/subcategory', methods=['POST', 'GET'])
@check_auth
def subcategory_handler():
    list_subcategory = []
    get_subcategory = (db.subcategory.find({}, {"_id": 0}))
    for j in get_subcategory:
        list_subcategory.append(j)
    return jsonify(list_subcategory)



@app.route('/products', methods=['POST', 'GET'])
def products_handler():
    list_products = []
    get_products = (db.products.find({}, {"_id": 0}))
    for k in get_products:
        list_products.append(k)
    return jsonify(list_products)


@app.route('/checkout/address' ,methods=["GET","POST"])
@check_auth
def checkout_address(user):
    email=user
    userdata_list = []
    customer_details = db.user.find({'email': email}, {"_id": 0, 'add': 1})
    for i in customer_details:
        userdata_list.append(i)
    return jsonify(userdata_list)


@app.route('/address', methods=['POST', 'GET'])
@check_auth
def add_addres(user):
        email=user
        data_for_address = request.get_json()
        name = data_for_address['firstname']
        address = data_for_address['add']
        city = data_for_address['city']
        state = data_for_address['state']
        pincode = data_for_address['zip']
        mail = data_for_address['email']
        AddType = data_for_address["gender"]

        user_db = db.user.find({"email": email})
        for i in user_db:
            get_id = i["_id"]
            if AddType == "Home":
                data_found_home = db.user.find({"add.addressType": "Home"})
                if data_found_home.count() == 0:
                    db.user.update({"_id": get_id}, {"$push": {
                        "add": {"addressType": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
                else:
                    return jsonify({"message": "Home type address already exist"})

            if AddType == "office":
                data_found_office = db.user.find({"add.addressType1": "office"})
                if data_found_office.count() == 0:
                    db.user.update({"_id": get_id}, {"$push": {
                        "add": {"addressType1": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
                else:
                    return jsonify({"message": "Office type address already exist"})

            if AddType == "other":
                db.user.update({"_id": get_id}, {"$push": {"add": [
                    {"addressType2": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                     "zip": pincode, "state": state, }]}})
        return jsonify({"message": "address added"})


@app.route('/editAddress', methods=['POST', 'GET'])
def edit_address():
    if "email" in session:
        email = session['email']
        name = request.form.get('firstname')
        address = request.form.get('add')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('zip')
        mail = request.form.get('email')
        AddType = request.form.get("gender")
        user_db = db.user.find({"email": email})
        for i in user_db:
            get_id = i["_id"]
            if AddType == "Home":
                data_found_home = db.user.find({"add.addressType": "Home"})
                if data_found_home:
                    db.user.update({"_id": get_id}, {"$set": {
                        "add": {"addressType": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
            if AddType == "office":
                data_found_office = db.user.find({"add.addressType1": "office"})
                if data_found_office:
                    db.user.update({"_id": get_id}, {"$set": {
                        "add": {"addressType1": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
    return jsonify({"message": "address successfully modified "})


@app.route('/order_tracker', methods=["GET", "POST"])
@check_auth
def Order_summary(user):
    email = user
    req_data = request.get_json()
    products_id = req_data["ProductsId"]
    products_list = []
    get_products_details = db.products.find({"ProductsId": products_id},
                                            {"_id": 0, "ProductsName": 1, "ProductsPrice": 1,
                                             "ProductsDescription": 1, "ProductsId": 1})
    for i in get_products_details:
        products_list.append(i)
    return jsonify(products_list)



@app.route('/paynow', methods=["POST", "GET"])
def Order_placed():
    if "email" in session:
        email = session["email"]
        data_req = request.get_json()
        data_session = data_req["email"]
        products_id = data_req["ProductsId"]
        get_products_details = db.products.find({"ProductsId": products_id},
                                                {"_id": 0, "ProductsName": 1, "ProductsPrice": 1,
                                                 "ProductsDescription": 1, "ProductsId": 1})
        item_list = []

        for i in get_products_details:
            item_list.append(i)
        current_datetime = datetime.now()
        db.orderid.update({"d_id": "1"}, {"$inc": {"OrderId": 1, "InvoiceId": 1}})
        get_data = db.orderid.find({}, {"_id": 0, "OrderId": 1})
        data_found = "OR"
        for j in get_data:
            data_found += str(j["OrderId"])
        db.orderhistory.update({"email": data_session}, {"$push": {"OrderDetails":
                                                                       {"orderid": data_found,
                                                                        "TimeOfPlaceTheOrder": current_datetime,
                                                                        "orderStatus": "placed",
                                                                        "productsDetails": i}}}, upsert=True)
        return jsonify(data_found, current_datetime, item_list)
    else:
        return jsonify("login please")


@app.route('/myorderhistory', methods=["POST", "GET"])
def my_order_history():
    if "email" in session:
        email = session["email"]
        req_id = request.get_json()
        email = req_id["email"]
        get_data = db.orderhistory.find({"email": email}, {"_id": 0})
        data_return = []
        for i in get_data:
            data_return.append(i)
        return jsonify(data_return)
    else:
        return jsonify("login please")


@app.route('/cancel', methods=['POST', 'GET'])
def cancel_order():
    if "email" in session:
        email = session["email"]
        data = request.get_json()
        data_order_id = data["orderid"]
        db.orderhistory.update(
            {"OrderDetails.orderid": data_order_id, "email": email},
            {"$set": {"OrderDetails.$.orderStatus": "cancel"}})
        return jsonify("Order has been cancel")
    else:
        return jsonify("please login")


@app.route('/add/cart', methods=["POST", "GET"])
@check_auth
def addcart(user):
    email = user
    data = request.get_json()
    cart = data["ProductsId"]
    count=0
    item_search = db.products.find({"ProductsId": cart}, {"_id": 0})
    data_result = []
    for i in item_search:
        data_result.append(i)
    db.cart.update({"email": email}, {"$push": {"ItemDetails": i}}, upsert=True)
    return jsonify("item added to cart")


@app.route('/cart', methods=["POST", "GET"])
@check_auth
def view_cart(user):
        email = user
        get_total_price = db.cart.aggregate(
            [{"$project": {"email": 1, "_id": 0, "totalamount": {"$sum": "$ItemDetails.ProductsPrice"}}}])
        total_price = []
        for j in get_total_price:
            total_price.append(j)
        item = db.cart.find({"email": email}, {"_id": 0, "email": 0})
        item_list = []
        for i in item:
            item_list.append(i)
        return jsonify(item_list, total_price)


@app.route('/delete/cart', methods=["POST", "GET"])
@check_auth
def remove_cart(user):
    email = user
    data = request.get_json()
    cart = data["ProductsId"]
    db.cart.update({"email": email}, {"$pull": {"ItemDetails": {"ProductsId": cart}}}, upsert=True)
    return jsonify( "Item remove from cart")



@app.route('/search', methods=["POST"])
def search_item():
    if "email" in session:
        data = request.get_json()
        user_req = data["context"]
        item = db.products.find({"ProductsName": {"$regex": user_req, "$options": "$ix"}}, {"_id": 0})
        item_list = []
        i = 0
        for i in item:
            item_list.append(i)
        if i == 0:
            return jsonify(err="item not found")

        else:
            return jsonify(item_list)
    else:
        return jsonify("login please")


@app.route('/logout')
def logout():
    session.pop('email', None)
    return jsonify({"message": "logout"})


@app.route('/forgot/password', methods=['POST', 'GET'])
def forgotpass():
    data = request.get_json()
    email = data["email"]
    fpass = data["psw"]
    db.user.update({"email": email}, {"$set": {"psw": fpass}})
    return jsonify({"message": "password has successfully updated"})


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    data = request.get_json()
    email = data['email']
    get_data = db.user.find({'email': email})
    if get_data.count() > 0:
        return jsonify({"message": "successfully updated"})
    else:
        return jsonify({"message": "Username Does not exist"})


if __name__ == '__main__':
    app.run(debug=True)
