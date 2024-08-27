import json
import psycopg2
import random

conn = psycopg2.connect(database = "Delish_dine", 
                        user = "postgres", 
                        host= 'localhost',
                        password = "Nahim@603d",
                        port = 5432)
cur = conn.cursor()


def book_table(username, date, hour, fullname, phone_number, people, restaurant):
    bookings = get_bookings(username)
    bookings = [json.dumps(booking) for booking in bookings]
    bookings.append(json.dumps({'username':username,'restaurant':restaurant,'date':date,'time':hour,'fullname':fullname,'phone_number':phone_number,'people':people}))
    cur.execute("UPDATE USERS SET BOOKINGS = %s WHERE USERNAME = %s", (bookings, username))
    conn.commit()
    
def get_bookings(username):
    cur.execute(f"SELECT BOOKINGS FROM USERS WHERE USERNAME = '{username}' ")
    conn.commit()
    bookings = cur.fetchall()[0][0]
    if not bookings :
        bookings = []
    bookings = [json.loads(booking) for booking in bookings]
    return bookings

def add_user(username,password,email,fullname,phone):
    cur.execute(f"INSERT INTO users(username,password,email,fullname,phone_number) VALUES('{username}','{password}','{email}','{fullname}','{phone}')")
    conn.commit()
    
def authenticate_user(username,password):
    if not password:
        cur.execute(f"SELECT * FROM users WHERE username='{username}'")
        usname=cur.fetchall()
        if usname:
            return False
        else:
            return True

    cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    credentials=cur.fetchall()
    if not credentials:
        return False
    else:
        return True
    
def get_restaurants():
    cur.execute("SELECT * FROM restaurants")
    result=cur.fetchall()
    return result


def get_restaurants_for_home():
    random_ids = random.sample(range(1, 16), 6)
    query = "SELECT * FROM restaurants WHERE res_id IN ({})".format(','.join(map(str, random_ids)))
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_restaurants_by_categoryid(category_id):
    cur.execute(f"SELECT DISTINCT r.* FROM restaurants r JOIN dishes d ON r.res_id = d.res_id WHERE d.category_id = {category_id};")
    result=cur.fetchall()
    return result
    
def get_dishes_from_res_name(rest_name):
     cur.execute(f"SELECT d.* FROM restaurants r JOIN dishes d ON r.res_id = d.res_id WHERE r.restaurant_name = '{rest_name}';")
     result=cur.fetchall()
     return result
 
def user_profile(username):
    cur.execute(f"SELECT * FROM users WHERE username='{username}'")
    result=cur.fetchone()
    return result

def update_user(username,first_name,last_name,email,phone,old_password=None,new_password=None):
    if old_password and new_password:
        cur.execute(f"SELECT password FROM users WHERE username='{username}'")
        result_password=cur.fetchone()
        if result_password[0] == old_password:
            cur.execute(f"UPDATE users SET password='{new_password}' WHERE username='{username}'")
            conn.commit()
            return True
        else:
            return False
    else:
        cur.execute(f"""UPDATE users SET email='{email}',phone_number='{phone}',fullname='{first_name+" "+last_name}' WHERE username='{username}'""")
        conn.commit()
        return True
    
def get_dish(dish_id):
    cur.execute(f"SELECT dish_name,price FROM dishes WHERE dish_id={dish_id}")
    result=cur.fetchone()
    return result

def get_cart(username,restaurant=None):
    cur.execute(f"SELECT orders FROM cart WHERE username = '{username}'")
    orders = cur.fetchone()
    if not restaurant and orders:
        return orders[0]
    
    if orders and orders[0]!=None:
        orders_data = orders[0]
        filtered_dishes = [dish_name for dish_name, details in orders_data.items() if details[1] == restaurant]
        return filtered_dishes
    else:
        return []

def addToCart(username,dish):
    cur.execute(f"SELECT orders FROM cart WHERE username='{username}'")
    order = cur.fetchone()
    
    if order and order[0]:
        order_data = order[0]
        for dish_name, details in dish.items():
            order_data[dish_name] = details
        cur.execute("UPDATE cart SET orders = %s WHERE username = %s", (json.dumps(order_data), username))   
        conn.commit() 
    else:
        cur.execute("INSERT INTO cart (username, orders) VALUES (%s, %s)", (username, json.dumps(dish)))
        conn.commit()
        
def updateQuantity(username,dish,restaurant,quantity):
    cur.execute(f"SELECT orders FROM cart WHERE username='{username}'")
    order = cur.fetchone()[0]
    
    for dishes,details in order.items():
        if dishes==dish and details[1]==restaurant:
            order[dish][2]=quantity
    cur.execute("UPDATE cart SET orders = %s WHERE username = %s", (json.dumps(order), username))
    conn.commit() 
    
def clearCart(username):
    cur.execute(f"DELETE FROM cart WHERE username='{username}'")
    conn.commit()
    
def removeItem(username,dish,restaurant):
    cur.execute(f"SELECT orders FROM cart WHERE username='{username}'")
    orders = cur.fetchone()[0]
    orders_data = dict(orders)
    
    for dishes,details in orders.items():
        if dish==dishes and restaurant==details[1]:
            orders_data.pop(dish)
    if orders_data:
        cur.execute("UPDATE cart SET orders = %s WHERE username = %s", (json.dumps(orders_data), username))
    else:
        cur.execute(f"DELETE FROM cart WHERE username='{username}'")
    conn.commit()

def order(username):
    orders = get_cart(username)
    cur.execute(f"SELECT orders FROM users WHERE username='{username}'")
    user_orders = cur.fetchone()
    order_data = user_orders[0]
    if not order_data:
        cur.execute("UPDATE users SET orders = %s WHERE username = %s", (json.dumps(orders), username))
    else:
        order_data.update(orders)
        cur.execute("UPDATE users SET orders = %s WHERE username = %s", (json.dumps(order_data), username))
    conn.commit()