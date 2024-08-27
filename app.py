from flask import Flask, jsonify,render_template,request,redirect
from database import order,removeItem,clearCart,authenticate_user,add_user,get_restaurants,get_restaurants_for_home,get_restaurants_by_categoryid,get_dishes_from_res_name,user_profile,update_user,get_dish,addToCart,get_cart,updateQuantity,book_table,get_bookings

app=Flask(__name__)

@app.route('/',methods=["POST", "GET"])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        
        if authenticate_user(username,password if password else "password"):
            return redirect("/home/" + username)
        else:
            return render_template('login.html',alert="Invalid username or password!!!!",alert_type='danger')
    return render_template('login.html',alert='',alert_type='')

@app.route('/register',methods=["POST", "GET"])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        confpassword=request.form['confpassword']
        email=request.form['email']
        fullname=request.form['fullname']
        phone=request.form['phone']
        
        if not confpassword==password:
            return render_template('register.html',alert="Re-enter confirmed password!!!",alert_type="danger")
        
        if authenticate_user(username,''):
            add_user(username,password,email,fullname,phone)
            return render_template('login.html',alert="Successfully registered!!",alert_type="success")
        else:
            return render_template('register.html',alert="Username already exists!!!",alert_type="danger")
    return render_template('register.html',alert='',alert_type='')

@app.route('/restaurant/<username>/<category>')
@app.route('/restaurant/takeAway/<username>')
def restaurant(username, category=None):
    if category:
        restaurants = get_restaurants_by_categoryid(category)
    else:
        restaurants = get_restaurants()
    
    return render_template("restaurant.html", restaurants=restaurants, username=username)


@app.route('/take_away/<restaurant>/<username>')
def take_away(restaurant, username):
    dishes = get_dishes_from_res_name(restaurant)
    cart = get_cart(username,restaurant)
    return render_template("take_away.html", dishes=dishes, username=username,restaurant=restaurant,cart=cart)


@app.route('/bookings/<username>')
def bookings(username):
    bookings = get_bookings(username)
    print(bookings)
    return render_template("your_bookings.html",username = username,bookings = bookings)    

@app.route('/restaurant/booking/<username>')
def booking(username):
    restaurants = get_restaurants()
    return render_template("restaurant_list_for_booking.html",restaurants=restaurants,username=username) 

@app.route('/reservation/<restaurant>/<username>',methods=["GET","POST"])
def reservation(username,restaurant):
    if request.method == "POST":
        date = request.form.get("date")
        hour = request.form.get("hours")
        fullname = request.form.get("fullname")
        phone_number = request.form.get("phone_number")
        people = request.form.get("people")
        book_table(username,date,hour,fullname,phone_number,people,restaurant)
        return render_template('book_table.html',username = username,restaurant=restaurant,reserved=True)
    return render_template('book_table.html',username = username,restaurant=restaurant)


@app.route('/home/<username>')
def home(username):
    restaurants = get_restaurants_for_home()
    booking_restaurants = get_restaurants_for_home()
    return render_template("Home.html", username=username, restaurants=restaurants, booking_restaurants=booking_restaurants)

@app.route('/profile/<username>',methods=["POST", "GET"])
def profile(username):
    profile_user = user_profile(username)
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        if not old_password and not new_password:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            if update_user(username,first_name,last_name,email,phone):
                profile_user = user_profile(username)
                return render_template("user_profile.html",username=username, profile=profile_user,alert='Saved Successfully!!!',alert_type='success')            
        else:
            if update_user(username,first_name,last_name,email,phone,old_password,new_password):
                profile_user = user_profile(username)
                return render_template("user_profile.html",username=username, profile=profile_user,alert='Saved Successfully!!!',alert_type='success')
            else:
                profile_user = user_profile(username)
                return render_template("user_profile.html", profile=profile_user,alert='Incorrect password!!!',alert_type='danger')                        
    return render_template("user_profile.html",username=username, profile=profile_user,alert='',alert_type='')
    
@app.route('/add_to_cart/<username>', methods=['POST'])
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart(username=None):
    if request.method == 'POST':
        data = request.json
        if username:
            user_json = data.get("username")
            dish_json = data.get("dish")
            restaurant_json = data.get("restaurant")
            qty = int(data.get("quantity"))
            updateQuantity(user_json,dish_json,restaurant_json,qty)
            print("Update successful")
            return jsonify({'message': 'Added to cart successfully'}), 200
        else:
            dish_id = data.get('dish_id')
            username_json = data.get("username")
            restaurant = data.get("restaurant")
            dish = get_dish(dish_id)

            if dish:
                order_data = {dish[0]: [float(dish[1]), restaurant, 1]}
                addToCart(username_json, order_data)
                return jsonify({'message': 'Added to cart successfully'}), 200
            else:
                return jsonify({'error': 'Invalid dish ID'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405
    
@app.route('/clear_cart/<user>', methods=["POST"])    
@app.route('/clear_cart', methods=["POST"])
def clear_cart(user=None):
    if request.method=='POST':
        data = request.json
        if user:
            username = data.get("username")
            order(username)
            clearCart(username)
            return jsonify({'message':'Successfully ordered'})
                
        username = data.get("username")
        clearCart(username)
        return jsonify({'message':'Successfully cleared'})
        
@app.route('/remove_item/<username>',methods=["POST"])
def remove_item(username):
    if request.method=='POST':
        data = request.json
        dish = data.get("dish")
        restaurant = data.get("restaurant")
        
        removeItem(username,dish,restaurant)
        return jsonify({'message':'Successfully removed'})

    
@app.route('/cart/<username>')
def cart(username):
    orders = get_cart(username)
    total_price=0
    tax=0
    taxPrice=0
    if orders:
        for order in orders:
            orders[order][2]=int(orders[order][2])
        prices = [order[0]*order[2] for key,order in orders.items()]
        total_price = sum(prices)
        tax = total_price*0.5
        taxPrice = total_price+tax+15
    return render_template("cart.html",orders=orders,total_price=round(total_price,2),tax=round(tax,2),taxPrice=round(taxPrice,2),username=username)
    
@app.route('/bill/<username>')
def bill(username):
    orders = get_cart(username)
    for order in orders:
            orders[order][2]=int(orders[order][2])
    prices = [order[0]*order[2] for key,order in orders.items()]
    total_price = sum(prices)
    return render_template("bill.html",username=username,orders=orders,subtotal=round(total_price,2))
    

if __name__=="__main__":
    app.run(debug=True)