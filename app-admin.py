"""
TODO: Student name(s): Snigdha Saha, Sreemanti Dey
TODO: Student email(s): snigdha@caltech.edu, sdey@caltech.edu
TODO: Beli Food Review App
"""
import sys  # to print error messages to sys.stderr
import mysql.connector
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode
import json

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True

# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appadmin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='adminpw',
          database='belidb' # replace this with your database name
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def show_admin_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    print('What would you like to do? ')
    print('  (u) - get all users')
    print('  (aR) - add a restaurant')
    print('  (uR) - update an existing restaurant')
    print('  (rf) - update the ranking formula')
    print('  (c) - find restaurant chains')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'u':
        users = get_all_users()
        with open('users.txt', 'w') as write_file:
            write_file.write(json.dumps(users))
    elif ans == 'aR':
        print('Please enter the following information: ')
        category = input('Enter the category:').lower()
        restaurant_name = input('Enter the restaurant name').lower()
        website = input('Enter the restaurant website:').lower()
        location = input('Enter the location:').lower()
        cuisines = []
        while True:
            cuisine = input('Enter the cuisine(s),\
                            type done when you are done:').lower()
            if cuisine.lower() == 'done':
                break
            cuisines.append(cuisine)
        price_range = input('Enter the price range:').lower() 
        add_a_restaurant(category, restaurant_name, website,\
                         location, cuisines, price_range)
    elif ans == 'uR': 
        print('Enter the attribute you want to update: ')
        print('(c) - category')
        print('(n) - name')
        print('(w) - website')
        print('(l) - location')
        print('(cu) - cuisine')
        print('(p) - price range')
        rest_name = input('Enter the restaurant you want to update: ').lower()
        location = input('Enter the location of the restaurant you want to\
                         update').lower()
        choice = input('Enter an option: ').lower()
        param = ''
        if choice == 'c': 
            param = 'category'
        elif choice == 'n':
            param = 'restaurant_name'
        elif choice == 'w':
            param = 'website'
        elif choice == 'l':
            param = 'location'
        elif choice == 'cu':
            param = 'cuisine'
        elif choice == 'p':
            param = 'price_range'
        else:
            print("Option not found")
            return
        # we will only take one cuisine at a time to error if the cuisine
        # already exists for this restaurant
        val = input(f'Please enter the new value for {param}:').lower()
        update_a_restaurant(param, val, rest_name)
    elif ans == 'c':
        find_chains() 
    else:
        print("Invalid Choice. Please try again")
        show_admin_options() 

def quit_ui():
    """
    Quits the program, printing a good bye message to the user.
    """
    print('Good bye, admin!')
    exit()


def get_all_users():
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'SELECT user_id, username FROM users_info;'
    try:
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()
        users = {}
        for row in rows:
            (user_id, username) = (row)
            users[user_id] = username
        return users
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred fetching all users')


def get_rest_id(restaurant_name, location):
    cursor = conn.cursor()
    rest_id_query = 'SELECT restaurant_id FROM restaurant\
        WHERE restaurant_name = \'%s\' AND location = \'%s\';' \
            % (restaurant_name, location)
    try:
        cursor.execute(rest_id_query)
        rest_id = cursor.fetchone()
        return rest_id
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('restaurant not found')


def get_cuisine_id(cuisine):
    cursor = conn.cursor()
    cuisine_id_query = 'SELECT cuisine_id FROM cuisine\
        WHERE cuisine_name = \'%s\';' % (cuisine)
    try:
        cursor.execute(cuisine_id_query)
        cuisine_id = cursor.fetchone()
        return cuisine_id
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr(f'user {username} not found')


def get_category_id(category):
    cursor = conn.cursor()
    category_id_query = 'SELECT category_id FROM category\
        WHERE category_name = \'%s\';' % (category)
    try:
        cursor.execute(category_id_query)
        category_id = cursor.fetchone()
        return category_id
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr(f'user {username} not found')


def add_a_restaurant(category, restaurant_name, 
                     website, location,
                     cuisines, price_range):
    cursor = conn.cursor()

    sql = 'INSERT INTO restaurant (restaurant_name, website,\
           restaurant_location, price_range) VALUES\
          (\'%s\',\' %s\', \'%s\', \'%s\';' \
            % (restaurant_name, website, location, price_range)
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when inserting the restaurant.')

    rest_id_sql = "SELECT LAST_INSERT_ID();"

    try:
        cursor.execute(rest_id_sql)
        rest_id = cursor.fetchone() 
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred')

    category_id = get_category_id(category)

    category_sql = "INSERT INTO in_category VALUES (\'%d\', \'%d\');" \
                    (rest_id, category_id)
    
    try:
        cursor.execute(category_sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred')

    for cuisine in cuisines:
        cuisine_id = get_cuisine_id(cuisine)

        cuisine_sql = "INSERT INTO in_cuisine VALUES (\'%d\', \'%d\');" \
                        (rest_id, cuisine_id)
        
        try:
            cursor.execute(cuisine_sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred')
    

def update_a_restaurant(param, new_val, rest_name, location):
    cursor = conn.cursor()
    rest_id = get_rest_id(rest_name, location)

    if param == 'category':

        category_id = get_category_id(new_val)

        remove_sql = "DELETE FROM in_category WHERE rest_id = \'%s\';" \
                        % (rest_id)
        
        try:
            cursor.execute(remove_sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred.')

        category_sql = "INSERT INTO in_category VALUES (\'%d\', \'%d\');" \
                    (rest_id, category_id)
    
        try:
            cursor.execute(category_sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred')
        
        

    elif param == 'cuisine':
        cuisine_id = get_cuisine_id(new_val)

        cuisine_sql = "INSERT INTO in_cuisine VALUES (\'%d\', \'%d\');" \
                        (rest_id, cuisine_id)
        
        try:
            cursor.execute(cuisine_sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('This restaurant is aready associated \
                           with this cuisine')

    else:
        sql = 'UPDATE restaurants SET\
            \'%s\' = \'%s\' \
            WHERE restaurant_name = \'%s\' AND location = \'%s\';' \
                % (param, new_val, rest_name, location)
        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred when updating the restaurant.')


def find_chains():
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'CALL sp_find_chains();'
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when updating chains.')


def main():
    """
    Main function for starting things up.
    """
    show_admin_options()

if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()