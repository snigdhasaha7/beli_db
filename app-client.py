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

def get_conn(username, userpw):
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user=username,
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password=userpw,
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
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_options(username):
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    # TODO: talk to El to figure out how to handle making a new user
    # especially with database connection
    print('What would you like to do? ')
    print('  (u) - update profile')
    print('  (r) - rank a new restaurant')
    print('  (uR) - update a ranking')
    print('  (a) - add a friend')
    print('  (l) - get all restaurants in a location')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui(username)
    elif ans == 'u':
        print('What do you want to update?')
        print('(u) - username')
        print('(n) - name')
        print('(pfp) - profile picture') 
        print('(pw) - password')
        print('(l) - location')
        choice = input('Enter an option: ').lower()
        val = input(f'Enter a new value for {choice}')
        if choice != 'password':
            val = val.lower() 
        update_user_profile(username, choice, val) 
    elif ans == 'r': 
        rest_name = input('Enter a restaurant name').lower() 
        location = input('Enter the restaurant location').lower()
        # TODO: handle multiple restaurants in same location with same name
        # IDEA: give user the extracted options 
        ranking = float(input("Enter a ranking out of 10:"))
        description = input("(optional)\
                            Enter a description of your experience: ").lower()
        rank_a_restaurant(rest_name, location, ranking, description)
    elif ans == 'uR': 
        rest_name = input('Enter a restaurant name').lower() 
        location = input('Enter the restaurant location').lower()
        # TODO: handle multiple restaurants in same location with same name
        # IDEA: give user the extracted options 
        print('What do you want to update?')
        print('(r) - ranking')
        print('(d) - description')
        choice = input('Enter a choice: ').lower()
        val = input(f'Enter a new value for {choice}')
        if choice == ranking:
            val = float(val)
    elif ans == 'a':
        friend_user = input('Enter a username to add to friends:').lower() 
        add_a_friend(username, friend_user) 
    elif ans == 'l':
        location = input("Enter the location to search in: ").lower()
        restaurants = get_all_restaurants_in_location(location)
        # TODO: handle what to do with these restaurants
    else:
        print("Invalid Choice. Please try again")
        show_options(username) 

def quit_ui(username):
    """
    Quits the program, printing a good bye message to the user.
    """
    print(f'Good bye, {username}!')
    exit()

def update_user_profile(username, update_param, update_val):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'UPDATE users SET\
          \'%s\' = \'%s\' \
          WHERE username = \'%s\';' % (update_param, update_val, username)
    
    if update_param == 'username':
        try:
            cursor.execute(sql)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('Sorry, that username is taken!')
    else:
        try:
            cursor.execute(sql)
            # row = cursor.fetchone()
            rows = cursor.fetchall()
            for row in rows:
                (col1val) = (row) # tuple unpacking!
                # do stuff with row data
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred, give something useful for clients...')

def get_user_id(username):
    cursor = conn.cursor()
    user_id_query = 'SELECT user_id FROM users\
        WHERE username = \'%s\';' % (username)
    try:
        cursor.execute(user_id_query)
        user_id = cursor.fetchone()
        return user_id
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # TODO: Please actually replace this :) 
            sys.stderr(f'user {username} not found')

def get_rest_id(restaurant_name, location):
    cursor = conn.cursor()
    rest_id_query = 'SELECT restaurant_id FROM restaurants\
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
            # TODO: Please actually replace this :) 
            sys.stderr('user not found')

def rank_a_restaurant(username, rest_name, location, ranking, description):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    
    user_id = get_user_id(username)
    rest_id = get_rest_id(rest_name,location)

    # TODO: in the backend, there should be a trigger to update 
    # cuisines, categories, average ratings
    sql = "INSERT INTO ratings VALUES \
        (\'%s\', \'%s\', \'%f\', \'%s\');" \
            % (user_id, rest_id, ranking, description)
    
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when ranking the restaurant')

def update_a_ranking(username, rest_name, location, param, new_val):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    
    user_id = get_user_id(username)
    rest_id = get_rest_id(rest_name,location)

    # TODO: in the backend, there should be a trigger to update 
    # cuisines, categories, average ratings

    sql = 'UPDATE ratings SET \
            %s = \'%s\' \
            WHERE user_id = \'%s\' AND restaurant_id = \'%s\';'\
            % (param, new_val, user_id, rest_id)
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when updating the restaurant')

def add_a_friend(username, friend_user):
    cursor = conn.cursor()

    user_id = get_user_id(username)
    friend_id = get_user_id(friend_user)

    sql = 'INSERT INTO users VALUES (\'%s\', \'%s\');' % (user_id, friend_id) 

    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred fetchi')

def get_all_restaurants_in_location(location):
    # TODO: potentially allow to handle for further parameters
    cursor = conn.cursor() 
    
    # calling UDF
    sql = 'CALL get_restaurants_in_location(%s);' % location 
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        restaurants = {}
        for row in rows:
            (rest_name, cuisine, category) = (row) # tuple unpacking!
            restaurants[rest_name] = {'cuisine': cuisine, 'category': category}
        return restaurants
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred fetching restaurants')


def main():
    """
    Main function for starting things up.
    """
    show_options(username)


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    username = input('Enter your username: ').lower()
    userpw = input('Enter your password: ')
    conn = get_conn(username, userpw)
    main()