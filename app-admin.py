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
        # TODO: save the users
    elif ans == 'aR':
        print('Please enter the following information: ')
        # TODO: handle empty values
        category = input('Enter the category:').lower()
        restaurant_name = input('Enter the restaurant name').lower()
        website = input('Enter the restaurant website:').lower()
        location = input('Enter the location as (City, State)').lower()
        cuisine = input('Enter the cuisine:').lower()
        price_range = input('Enter the price range:').lower() 
        add_a_restaurant(category, restaurant_name, website,\
                         location, cuisine, price_range)
    elif ans == 'uR': 
        print('Enter the attribute you want to update: ')
        print('(c) - category')
        print('(n) - name')
        print('(w) - website')
        print('(l) - location')
        print('(cu) - cuisine')
        print('(p) - price range')
        rest_name = input('Enter the restaurant you want to update: ').lower()
        # TODO: handle multiple restaurants with same name
        # IDEA: maybe display options to admin?
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
        val = input(f'Please enter the new value for {param}:').lower()
        update_a_restaurant(param, val, rest_name)
    elif ans == 'rf':
        # TODO: figure out how to update a formula
        # likely goes into updating a trigger / stored procedure
        update_ranking_formula()
    elif ans == 'c':
        find_chains()
        # TODO: handle updating chain 
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
    sql = 'SELECT user_id, username FROM users'
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

def add_a_restaurant(category, restaurant_name, 
                     website, location,
                     cuisine, price_range):
    cursor = conn.cursor()
    # TODO: handle null values
    category_query = 'SELECT category_id FROM categories WHERE\
        category_name=\'%s\';' % (category, )
    
    try:
        cursor.execute(category_query)
        category_id = cursor.fetchone()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Error extracting category_id')

    cuisine_query = 'SELECT cuisine_id FROM cuisines WHERE\
        cuisine_name=\'%s\';' % (cuisine, )
    
    try:
        cursor.execute(cuisine_query)
        cuisine_id = cursor.fetchone()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # TODO: Please actually replace this :) 
            sys.stderr('Error extracting category_id')

    sql = 'INSERT INTO restaurants VALUES ()\
          \'%s, %s, %s, %s, %s, %s, %f\';' \
            % (category_id, restaurant_name, \
                website, location, cuisine_id, price_range, 0.0)
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when inserting the restaurant.')

def update_a_restaurant(param, new_val, rest_name):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'UPDATE restaurants SET\
          \'%s\' = \'%s\' \
          WHERE restaurant_name = \'%s\';' % (param, new_val, rest_name)
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when updating the restaurant.')

def update_ranking_formula():
    # TODO: figure out how to do this with SQL
    return

def find_chains():
    # TODO: call stored procedure here
    return

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