"""
TODO: Student name(s): Snigdha Saha, Sreemanti Dey
TODO: Student email(s): snigdha@caltech.edu, sdey@caltech.edu
TODO: Beli Food Review App
"""
import sys  # to print error messages to print
import mysql.connector
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = False

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
          database='belidb', # replace this with your database name
          autocommit=True
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            print('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            print('Database does not exist.')
        elif DEBUG:
            print(err)
        else:
            # A fine catchall client-facing message.
            print('An error occurred, please contact the administrator.')
        sys.exit(1)

# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_options(welcome=False):
    
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    if welcome is True:
        print(f'Welcome, {username}!')
    print('What would you like to do? ')
    print('  (u) - update profile')
    print('  (r) - rank a new restaurant')
    print('  (uR) - update a ranking')
    print('  (a) - add a friend')
    print('  (l) - get all restaurants in a location')
    print('  (tL) - get top restaurant in a location')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ')
    if ans == 'q':
        quit_ui(username)
    elif ans == 'u':
        print('What do you want to update?')
        print('(u) - username')
        print('(n) - name')
        print('(e) - email')
        print('(pfp) - picture') 
        print('(pw) - password')
        print('(l) - location')
        choice = input('Enter an option: ').lower()
        param = ""
        if choice == 'u':
            param = 'username'
        elif choice == 'n':
            param = 'real_name'
        elif choice == 'e':
            param = 'email'
        elif choice == 'pw':
            param = 'pw'
        elif choice == 'l':
            param = 'user_location'
        elif choice == 'pfp':
            param = 'user_picture'

        val = input(f'Enter a new value for {param}: ')
        if choice != 'pw' and choice != 'n':
            val = val.lower() 
        update_user_profile(param, val)
        show_options()
    elif ans == 'r': 
        rest_name = input('Enter a restaurant name: ')
        location = input('Enter the restaurant location: ')
        ranking = float(input("Enter a ranking out of 10: "))
        description = input(("(optional) "
                            "Enter a description of your experience: "))
        rank_a_restaurant(username, rest_name, location, ranking, description)
        show_options()
    elif ans == 'uR': 
        rest_name = input('Enter a restaurant name: ')
        location = input('Enter the restaurant location: ')
        print('What do you want to update?')
        print('(r) - rating')
        print('(d) - description')
        choice = input('Enter a choice: ').lower()
        param = "" 
        if choice == "r":
            param = "rating"
        elif choice == "d":
            param = "rating_description"
        else:
            print("Invalid Choice")
            quit_ui(username)
        val = input(f'Enter a new value for {param}: ')
        if choice == 'r':
            val = float(val)
        update_a_ranking(username, rest_name, location, param, val)
        show_options()
    elif ans == 'a':
        friend_user = input('Enter a username to add to friends: ').lower() 
        add_a_friend(username, friend_user) 
        show_options()
    elif ans == 'l':
        location = input("Enter the location to search in: ")
        restaurants = get_all_restaurants_in_location(location)
        if len(restaurants) == 0:
            print(f'No restaurants found in {location}!')
        else:
            i = 1
            for rest in restaurants: 
                print(f'{i}. {rest}')
                cuisines = str(restaurants[rest]["cuisines"])[1:-1]\
                    .replace('\'', "")
                print(f'Cuisines: {cuisines}')
                print(f'Category: {restaurants[rest]["category"]}')
                i += 1
        show_options()
    elif ans == 'tL':
        location = input("Enter the location to search in: ")
        rest_name, cuisines, category = \
            get_top_restaurant_in_location(location)
        print(f'The top restaurant in {location} is {rest_name}.')
        print(f'They serve the following cuisine(s):')
        for cuisine in cuisines:
            print(cuisine[0])
        print(f'{rest_name} is in category {category}.')
        show_options()
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

    sql = "SELECT authenticate(\'%s\', \'%s\');" % (username, password)

    try:
        cursor.execute(sql)
        output = int(cursor.fetchone()[0])
        cursor.fetchall()
        return output
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('Invalid credentials!')
            main()


def create_user(username, email, password, real_name, user_picture, user_location):
    cursor = conn.cursor() 
    
    sql = "CALL sp_add_user(\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');"\
        % (username, email, password, real_name, user_picture, user_location)
    
    try:
        cursor.execute(sql)
        print(f'Successfully created user {username}!')
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            err_msg = ('Either the username or email is already taken, or '
                       'invalid data entered!')
            print(err_msg)
            main()


def update_user_profile(update_param, update_val):
    cursor = conn.cursor()
    global username

    if update_param == 'pw':
        sql = 'CALL sp_change_password(\'%s\', \'%s\');' \
                % (username, update_val)
    else:
        sql = 'UPDATE users_info SET\
            %s = \'%s\' \
            WHERE username = \'%s\';' % (update_param, update_val, username)
    
    if update_param == 'username':
        try:
            cursor.execute(sql)
            username = cursor.fetchone()[0].replace('\'', "")
            cursor.fetchall()
            print(f'Successfully updated username to {username}!')
            show_options(True)
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('Sorry, that username is taken!')
                show_options()
    else:
        try:
            cursor.execute(sql)
            print(f"Successfully updated {update_param}!")
        except mysql.connector.Error as err:
            # If you're testing, it's helpful to see more details printed.
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print(f'An error occurred updating your profile.')
                show_options()


def get_user_id(username):
    cursor = conn.cursor()
    user_id_query = 'SELECT user_id FROM users_info\
        WHERE username = \'%s\';' % (username)
    try:
        cursor.execute(user_id_query)
        temp_id = cursor.fetchone()
        cursor.fetchall()
        if temp_id is None:
            print(f'{username} not found!')
            show_options()
            return
        user_id = int(temp_id[0])
        return user_id
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print(f'user {username} not found')
            show_options()


def get_rest_id(restaurant_name, location):
    cursor = conn.cursor()
    restaurant_name = restaurant_name.replace('\'', '\'\'')
    rest_id_query = 'SELECT restaurant_id FROM restaurant\
        WHERE restaurant_name = \'%s\' AND \
        restaurant_location = \'%s\';' % (restaurant_name, location)
    
    try:
        cursor.execute(rest_id_query)
        temp_id = cursor.fetchone()
        cursor.fetchall()
        if temp_id is None:
            print(f'{restaurant_name} was not found in {location}!')
            show_options(username)
            return
        rest_id = int(temp_id[0])
        return rest_id
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print(f'{restaurant_name} was not found in {location}!')
            show_options()


def rank_a_restaurant(username, rest_name, location, ranking, description):
    cursor = conn.cursor()
    user_id = get_user_id(username)
    rest_id = get_rest_id(rest_name,location)

    sql = "INSERT INTO rating (rating, rating_description) VALUES \
        (\'%f\', \'%s\');" % (ranking, description)
    
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when ranking the restaurant')
            show_options()
    
    rating_id_sql = "SELECT LAST_INSERT_ID();"

    try:
        cursor.execute(rating_id_sql)
        rating_id = int(cursor.fetchone()[0])
        cursor.fetchall()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred')
            show_options()
    
    rating_sql = "INSERT INTO user_rating VALUES (\'%d\', \'%d\', \'%d\');" \
                    % (user_id, rest_id, rating_id)
    
    try:
        cursor.execute(rating_sql)
        print(f'Successfully added a ranking for {rest_name} in {location}!')
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred')
            show_options()


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
        rating_id = int(cursor.fetchone()[0])
        cursor.fetchall()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('You have not ranked this restaurant yet.')
            show_options()
    
    update_sql = 'UPDATE rating SET %s = \'%s\'\
                WHERE rating_id = \'%d\';'\
                % (param, new_val, rating_id)
    
    try:
        cursor.execute(update_sql)
        print(f'Successfully updated the ranking for {rest_name} in {location}!')
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when updating the rating')
            show_options()


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
            print(err)
            sys.exit(1)
        else:
            print('An error occurred.')
            show_options()


def get_all_restaurants_in_location(location):
    cursor = conn.cursor() 
    
    # calling UDF
    sql = 'SELECT restaurant_name, cuisine_name, category_name FROM\
        restaurant NATURAL LEFT JOIN in_cuisine NATURAL LEFT JOIN\
        cuisine NATURAL LEFT JOIN in_category NATURAL LEFT JOIN category\
        WHERE restaurant_location = \'%s\';' % location 
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        restaurants = {}
        for row in rows:
            (rest_name, cuisine_name, category_name) = (row)
            if rest_name in restaurants: 
                restaurants[rest_name]['cuisines'].append(cuisine_name)
            else:
                restaurants[rest_name] = \
                    {'cuisines': [cuisine_name], 'category': category_name}
        return restaurants
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred fetching restaurants')
            show_options()


def get_top_restaurant_in_location(location):
    cursor = conn.cursor()

    sql = "SELECT top_restaurant_loc(\'%s\');" % location

    try:
        cursor.execute(sql)
        rest_name = cursor.fetchone()[0]
        cursor.fetchall()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred.')
            show_options()

    if rest_name is None:
        print(f'No restaurants found in {location}!')
        show_options()
        return
    
    rest_id = get_rest_id(rest_name, location)
    
    cuisine_sql = 'SELECT cuisine_name FROM in_cuisine NATURAL LEFT JOIN cuisine\
                WHERE restaurant_id = \'%d\';' % (rest_id) 
    
    try:
        cursor.execute(cuisine_sql)
        rows = cursor.fetchall()
        cuisines = [] 
        for row in rows:
            (cuisine_name) = row
            cuisines.append(cuisine_name)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred.')
            show_options()

    category_sql = 'SELECT category_name FROM in_category NATURAL LEFT JOIN category\
                WHERE restaurant_id = \'%d\';' % (rest_id) 
    
    try:
        cursor.execute(category_sql)
        category = cursor.fetchone()[0]
        cursor.fetchall()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred.')
            show_options()
    
    return rest_name, cuisines, category


def main():
    """
    Main function for starting things up.
    """
    global username
    print("Sign Up or Log In?")
    print("(s) - sign up")
    print("(l) - log in")
    choice = input("Enter one of the above: ")
    if choice == "l":
        username = input('Enter your username: ').lower()
        userpw = input('Enter your password: ')
        output = authenticate_user(username, userpw)
        if output == 0:
            print("Invalid Credentials.")
            main()
        else:
            print("Successfully logged in.")
    elif choice == "s":
        print("Please enter the following details:")
        username = input("Username: ").lower() 
        email = input("Email: ").lower() 
        real_name = input("Full Name: ")
        user_picture = input("Enter a link to your pfp: ").lower()
        user_location = input("Enter your location: ").lower()
        password = input("Enter a strong password: ".lower())
        create_user(username, email, password, real_name,\
                    user_picture, user_location)
    else:
        print("Invalid choice. Goodbye!")
        main()
    show_options(True)


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()