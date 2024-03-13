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

def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appclient',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='clientpw',
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
        print('(e) - email')
        print('(pfp) - profile picture') 
        print('(pw) - password')
        print('(l) - location')
        choice = input('Enter an option: ').lower()
        val = input(f'Enter a new value for {choice}')
        if choice != 'pw' and choice != 'n':
            val = val.lower() 
        update_user_profile(username, choice, val) 
    elif ans == 'r': 
        rest_name = input('Enter a restaurant name').lower() 
        location = input('Enter the restaurant location').lower()
        ranking = float(input("Enter a ranking out of 10:"))
        description = input("(optional)\
                            Enter a description of your experience: ").lower()
        rank_a_restaurant(rest_name, location, ranking, description)
    elif ans == 'uR': 
        rest_name = input('Enter a restaurant name').lower() 
        location = input('Enter the restaurant location').lower()
        print('What do you want to update?')
        print('(r) - ranking')
        print('(d) - description')
        choice = input('Enter a choice: ').lower()
        val = input(f'Enter a new value for {choice}')
        if choice == 'r':
            val = float(val)
    elif ans == 'a':
        friend_user = input('Enter a username to add to friends:').lower() 
        add_a_friend(username, friend_user) 
    elif ans == 'l':
        location = input("Enter the location to search in: ").lower()
        restaurants = get_all_restaurants_in_location(location)
        for i, rest in enumerate(restaurants): 
            print(f'{i+1}: {rest}')
    else:
        print("Invalid Choice. Please try again")
        show_options()


def quit_ui(username):
    """
    Quits the program, printing a good bye message to the user.
    """
    print(f'Good bye, {username}!')
    exit()


def authenticate_user(username, password):
    cursor = conn.cursor() 

    sql = "CALL authenticate(\'%s\', \'%s\');" % (username, password)

    try:
        cursor.execute(sql)
        output = int(cursor.fetchone())
        return output
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Invalid credentials!')


def create_user(username, email, password, real_name, user_picture, user_location):
    cursor = conn.cursor() 

    sql = "CALL sp_add_user(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');"\
        % (username, email, password, real_name, user_picture, user_location)
    
    try:
        cursor.execute(sql)
        output = int(cursor.fetchone())
        return output
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Either the username or email is already taken, or\
                       invalid data entered!')

def update_user_profile(username, update_param, update_val):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    if update_param == 'pw':
        sql = 'CALL sp_change_password(\'%s\', \'%s\');' \
                % (username, update_val)
    else:
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
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr(f'An error occurred updating your profile.')

def get_user_id(username):
    cursor = conn.cursor()
    user_id_query = 'SELECT user_id FROM users_info\
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
            sys.stderr(f'user {username} not found')


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


def rank_a_restaurant(username, rest_name, location, ranking, description):
    cursor = conn.cursor()
    user_id = get_user_id(username)
    rest_id = get_rest_id(rest_name,location)

    sql = "INSERT INTO rating (rating, rating_description) VALUES \
        (\'%f\', \'%s\');" \
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
    
    rating_id_sql = "SELECT LAST_INSERT_ID();"

    try:
        cursor.execute(rating_id_sql)
        rating_id = cursor.fetchone() 
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred')
    
    rating_sql = "INSERT INTO user_rating VALUES (\'%d\', \'%d\', \'%d\');" \
                    % (user_id, rest_id, rating_id)
    
    try:
        cursor.execute(rating_sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred')


def update_a_ranking(username, rest_name, location, param, new_val):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    
    user_id = get_user_id(username)
    rest_id = get_rest_id(rest_name,location)

    id_sql = 'SELECT rating_id FROM user_rating \
            WHERE user_id = \'%s\' AND restaurant_id = \'%s\';'\
            % (user_id, rest_id)
    try:
        cursor.execute(id_sql)
        rating_id = cursor.fetchone()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('You have not ranked this restaurant yet.')
    
    update_sql = 'UPDATE rating SET \'%s\' = \'%s\'\
                WHERE rating_id = \'%s\';'\
                % (param, new_val, rating_id)
    
    try:
        cursor.execute(update_sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when updating the rating')

def add_a_friend(username, friend_user):
    cursor = conn.cursor()

    user_id = get_user_id(username)
    friend_id = get_user_id(friend_user)

    sql = 'INSERT INTO friend VALUES (\'%s\', \'%s\');' % (user_id, friend_id) 

    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred.')


def get_all_restaurants_in_location(location):
    cursor = conn.cursor() 
    
    # calling UDF
    sql = 'CALL top_restaurant_loc (%s);' % location 
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
    print("Sign Up or Log In?")
    print("(s) - sign up")
    print("(l) - log in")
    choice = input("Enter one of the above:")
    if choice == "l":
        username = input('Enter your username: ').lower()
        userpw = input('Enter your password: ')
        output = authenticate_user(username, userpw)
        if output == 0:
            print("Invalid Credentials.")
            return
    elif choice == "s":
        print("Please enter the following details:")
        username = input("Username:").lower() 
        email = input("Email:").lower() 
        real_name = input("Full Name:")
        user_picture = input("Enter a link to your pfp:").lower()
        user_location = input("Enter your location").lower()
        password = input("Enter a strong password:".lower())
        create_user(username, email, password, real_name,\
                    user_picture, user_location)
    else:
        print("Invalid choice. Goodbye!")
    show_options(username)


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()