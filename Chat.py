from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from pymongo import MongoClient
from datetime import datetime
client = MongoClient('localhost', 27017)
db = client.shilajit
app = Flask(__name__)
app.secret_key = 'rs'

@app.route('/login', methods=['POST', 'GET'])
def logedin():
    if request.method == 'POST':
        login_data_req= request.get_json()
        email=login_data_req["email"]
        session['email'] = email
        psw=login_data_req["psw"]
        name = db.user.find({'email': email,"psw":psw})
        if name.count() == 1:
            return jsonify({"message":"Login successfully"}),200
        else:
            return jsonify({"message":"username or password is incorrect"}),403



@app.route('/signup', methods=['POST', "GET"])
def signup():
    user_data=request.get_json()
    email=user_data["email"]
    sand = db.user.find({'email': email})
    if sand.count() > 0:
        return jsonify(err="Email already exsit"),403
    psw =user_data['psw']
    num = user_data['num']
    name = user_data['username']
    gender =user_data['gender']
    db.user.insert_one({'email': email, 'psw': psw, 'num': num, 'username': name, 'gender': gender, "add": []})
    return jsonify({"message":"user created successfully"}),200


@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'email' in session:
        email = session['email']
        return render_template('home.html')
    else:
        return redirect(url_for('login'))


@app.route('/category', methods=['POST', 'GET'])
def catogory_handler():
    if 'email' in session:
        get_category = (db.category.find({},{"_id":0}))
        list_category = []
        for i in get_category:
            list_category.append(i)
        return jsonify(list_category)
    else:
        return redirect(url_for('login'))


@app.route('/subcategory', methods=['POST', 'GET'])
def subcategory_handler():
    if 'email' in session:
        list_subcategory = []
        get_subcategory = (db.subcategory.find({},{"_id":0}))
        for j in get_subcategory:
            list_subcategory.append(j)
        return jsonify(list_subcategory)
    else:
        return redirect(url_for('login'))


@app.route('/products', methods=['POST', 'GET'])
def products_handler():
    if 'email' in session:
        list_products = []
        get_products = (db.products.find({},{"_id":0}))
        for k in get_products:
            list_products.append(k)
        return jsonify(list_products)
    return jsonify({"message":"please login "})


@app.route('/checkout/address')
def checkout_address():
    if 'email' in session:
        email = session['email']
        userdata_list = []
        customer_details = db.user.find({'email': email}, {"_id": 0, 'add': 1})
        for i in customer_details:
            userdata_list.append(i)
        return jsonify(userdata_list)
    else:
        return redirect(url_for('login'))


@app.route('/addressnew')
def new_address():
    return render_template('check.html')


@app.route('/address', methods=['POST', 'GET'])
def add_addres():
    if 'email' in session:
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
            get_id= i["_id"]
            if AddType == "Home":
                data_found_home=db.user.find({"add.addressType":"Home"})
                if  data_found_home.count()==0:
                    db.user.update({"_id": get_id}, {"$push": {"add":{"addressType": AddType, "firstname": name,"email": mail,"add": address, "city": city,
                                                                   "zip": pincode, "state": state, }}})
                else:
                   return "Home Type Already Exist"



            if AddType == "office":
                data_found_office = db.user.find({"add.addressType1": "office"})
                if data_found_office.count() == 0:
                    db.user.update({"_id": get_id}, {"$push": {
                        "add": {"addressType1": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
                else:
                    return " Office Type Address Already Exist"


            if AddType == "other":
                db.user.update({"_id": get_id}, {"$push": {"add": [
                    {"addressType2": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                     "zip": pincode, "state": state, }]}})
        return redirect(url_for('checkout_address'))


@app.route('/editAddress',methods=['POST','GET'])
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
            if AddType=="Home":
                data_found_home = db.user.find({"add.addressType": "Home"})
                if data_found_home:
                    db.user.update({"_id": get_id}, {"$set": {
                        "add": {"addressType": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
            if AddType=="office":
                data_found_office = db.user.find({"add.addressType1": "office"})
                if data_found_office:
                    db.user.update({"_id": get_id}, {"$set": {
                        "add": {"addressType1": AddType, "firstname": name, "email": mail, "add": address, "city": city,
                                "zip": pincode, "state": state, }}})
    return redirect(url_for('checkout_address'))


@app.route('/order_tracker',methods=["GET","POST"])
def Order_summary():
    if "email" in session:
        req_data =request.get_json()
        products_id=req_data["ProductsId"]
        products_list = []
        get_products_details=db.products.find({"ProductsId":products_id},{"_id":0,"ProductsName":1,"ProductsPrice":1,"ProductsDescription":1,"ProductsId":1})
        for i in get_products_details:
            products_list.append(i)
        return jsonify(products_list)
    else:
       return redirect(url_for('login'))

@app.route('/paynow',methods=["POST","GET"])
def Order_placed():
    if "email" in session:
        db.orderid.update({"d_id":"1" },{ "$inc": { "OrderId":1, "InvoiceId": 1 } })
        get_data=db.orderid.find({},{"_id":0,"OrderId":1})
        data_found = []
        current_datetime = datetime.now()
        for j in get_data:
            data_found.append(j)
        return jsonify(data_found,current_datetime)
    else:
        return redirect(url_for('login'))


@app.route('/myorderhistory',methods=["POST","GET"])
def my_order_history():
    return "hi"





@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/forgotPassword', methods=['POST', 'GET'])
def forgotpass():
    return render_template('product.html')


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    email = request.form.get('email')
    get_data = db.user.find({'email': email})
    if get_data.count() > 0:
        return render_template('password.html')
    else:
        return "Username Does not exsit"


if __name__ == '__main__':
    app.run(debug=True)
