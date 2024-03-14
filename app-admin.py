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
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def show_admin_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    print('What would you like to do? ')
    print('  (u) - get all users (exports to users.txt with user_id and username!)')
    print('  (aR) - add a restaurant')
    print('  (aC) - add a category')
    print('  (aCu) - add a cuisine')
    print('  (uR) - update an existing restaurant')
    print('  (c) - update chains data with restaurant chains')
    print('  (gC) - get all chains')
    print('  (gRU) - get recommended restaurants for each user (exports to recommendations.txt)')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ')
    if ans == 'q':
        quit_ui()
    elif ans == 'u':
        users = get_all_users()
        with open('users.txt', 'w') as write_file:
            write_file.write(json.dumps(users))
        print("Successfully exported to users.txt!")
        show_admin_options()
    elif ans == 'aR':
        print('Please enter the following information: ')
        category = input('Enter the category: ')
        restaurant_name = input('Enter the restaurant name: ')
        website = input('Enter the restaurant website: ').lower()
        location = input('Enter the location: ')
        cuisines = []
        while True:
            cuisine = input(('Enter the cuisine(s), '
                            'type done when you are done: '))
            if cuisine.lower() == 'done':
                break
            cuisines.append(cuisine)
        price_range = str(input('Choose from ($, $$, $$$, $$$)) [optional]: '))
        print(price_range)
        price_ranges = [None, '$', '$$', '$$$', '$$$$']
        while price_range not in price_ranges:
            print(('Invalid price range. Please either pick nothing ',
                  'or select 1 of $, $$, $$$, $$$$'))
            price_range = \
                input(f'Please enter the new value for price range: ').lower()
        add_a_restaurant(category, restaurant_name, website,\
                         location, cuisines, price_range)
        show_admin_options()
    elif ans == 'uR': 
        rest_name = input('Enter the restaurant you want to update: ')
        location = input(('Enter the location of the restaurant '
                          'you want to update: '))
        get_rest_id(rest_name, location)
        print('Enter the attribute you want to update: ')
        print('(c) - category')
        print('(n) - name')
        print('(w) - website')
        print('(l) - location')
        print('(cu) - cuisine')
        print('(p) - price range (optional, $, $$, $$$, or $$$$)')
        choice = input('Enter an option: ').lower()
        param = ''
        if choice == 'c': 
            param = 'category'
        elif choice == 'n':
            param = 'restaurant_name'
        elif choice == 'w':
            param = 'website'
        elif choice == 'l':
            param = 'restaurant_location'
        elif choice == 'cu':
            param = 'cuisine'
        elif choice == 'p':
            param = 'price_range'
        else:
            print("Option not found")
            return
        # we will only take one cuisine at a time to error if the cuisine
        # already exists for this restaurant
        val = input(f'Please enter the new value for {param}: ').lower()
        price_ranges = [None, '$', '$$', '$$$', '$$$$']
        while param == 'price_range' and val not in price_ranges:
            print('Invalid price range. Please either pick nothing ',
                  'or select 1 of $, $$, $$$, $$$$')
            val = input(f'Please enter the new value for {param}: ').lower()
        update_a_restaurant(param, val, rest_name, location)
        show_admin_options()
    elif ans == 'c':
        find_chains() 
        show_admin_options()
    elif ans == 'gC': 
        chains = get_chains()
        print("Here are all the existing chains in the data: ")
        for i, chain_name in enumerate(chains):
            print(f'{i+1}. {chain_name[0]}')
        show_admin_options()
    elif ans == 'gRU':
        recommendations = get_recommended_restaurants_per_user()
        if len(recommendations) == 0:
            print("No recommendations retrieved!")
        else:
            with open('recommendations.txt', 'w') as write_file:
                write_file.write(json.dumps(recommendations))
            print("Successfully exported to recommendations.txt!")
        show_admin_options()
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
        rows = cursor.fetchall()
        users = {}
        for row in rows:
            (user_id, username) = (row)
            users[user_id] = username
        return users
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred fetching all users')
            show_admin_options()


def get_rest_id(restaurant_name, location):
    cursor = conn.cursor()
    restaurant_name = restaurant_name.replace('\'', '\'\'')
    rest_id_query = 'SELECT restaurant_id FROM restaurant\
        WHERE restaurant_name = \'%s\' AND restaurant_location = \'%s\';' \
            % (restaurant_name, location)
    try:
        cursor.execute(rest_id_query)
        temp_id = cursor.fetchone()
        cursor.fetchall()
        if temp_id is None:
            print(f'{restaurant_name} not found in {location}')
            show_admin_options()
            return
        rest_id = int(temp_id[0])
        return rest_id
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print(f'{restaurant_name} not found in {location}')
            show_admin_options()


def get_cuisine_id(cuisine):
    cursor = conn.cursor()
    cuisine_id_query = 'SELECT cuisine_id FROM cuisine\
        WHERE cuisine_name = \'%s\';' % (cuisine)
    try:
        cursor.execute(cuisine_id_query)
        temp_id = cursor.fetchone()
        cursor.fetchall()
        if temp_id is None:
            print(f'Cuisine {cuisine} not found!')
            show_admin_options()
            return
        cuisine_id = int(temp_id[0])
        return cuisine_id
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print(f'cuisine not found')
            exit()


def get_category_id(category):
    cursor = conn.cursor()
    category_id_query = 'SELECT category_id FROM category\
        WHERE category_name = \'%s\';' % (category)
    try:
        cursor.execute(category_id_query)
        temp_id = cursor.fetchone()
        cursor.fetchall()
        if temp_id is None:
            print(f'Category {category} not found!')
            show_admin_options()
            return
        category_id = int(temp_id[0])
        return category_id
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print(f'category not found')
            exit()


def add_a_restaurant(category, restaurant_name, 
                     website, location,
                     cuisines, price_range):
    cursor = conn.cursor()

    sql = 'INSERT INTO restaurant (restaurant_name, restaurant_location,\
           price_range, website) VALUES\
          (\'%s\',\'%s\', \'%s\', \'%s\');' \
            % (restaurant_name, location, price_range, website)
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when inserting the restaurant.')
            show_admin_options()

    rest_id_sql = "SELECT LAST_INSERT_ID();"

    try:
        cursor.execute(rest_id_sql)
        rest_id = int(cursor.fetchone()[0])
        cursor.fetchall()
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred')
            show_admin_options()

    category_id = get_category_id(category)

    category_sql = "INSERT INTO in_category VALUES (\'%d\', \'%d\');"\
                    % (rest_id, category_id)
    
    try:
        cursor.execute(category_sql)
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred')
            show_admin_options()

    for cuisine in cuisines:
        cuisine_id = get_cuisine_id(cuisine)

        cuisine_sql = "INSERT INTO in_cuisine VALUES (\'%d\', \'%d\');" \
                        % (rest_id, cuisine_id)
        
        try:
            cursor.execute(cuisine_sql)
            print(f'Successfully added {restaurant_name} in {location} ',
                  f'with cuisine {cuisine} in category {category}.')
        except mysql.connector.Error as err:
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('An error occurred')
                show_admin_options()
    

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
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('An error occurred.')
                show_admin_options()

        category_sql = "INSERT INTO in_category VALUES (\'%d\', \'%d\');" \
                    % (rest_id, category_id)
    
        try:
            cursor.execute(category_sql)
            print(f'Successfully updated category for {rest_name}!')
        except mysql.connector.Error as err:
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('An error occurred')
                show_admin_options()

    elif param == 'cuisine':
        cuisine_id = get_cuisine_id(new_val)

        cuisine_sql = "INSERT INTO in_cuisine VALUES (\'%d\', \'%d\');" \
                        % (rest_id, cuisine_id)
        
        try:
            cursor.execute(cuisine_sql)
            print(f'Successfully added {new_val} to cuisines for {rest_name}!')
        except mysql.connector.Error as err:
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('This restaurant is aready associated '
                           'with this cuisine')
                show_admin_options()

    else:
        sql = 'UPDATE restaurant SET %s = \'%s\' \
            WHERE restaurant_name = \'%s\' AND restaurant_location = \'%s\';' \
                % (param, new_val, rest_name, location)
        try:
            cursor.execute(sql)
            print(f'Successfully updated {rest_name}!')
        except mysql.connector.Error as err:
            if DEBUG:
                print(err)
                sys.exit(1)
            else:
                print('An error occurred when updating the restaurant.')
                show_admin_options()


def find_chains():
    cursor = conn.cursor()
    sql = 'CALL sp_find_chains();'
    try:
        cursor.execute(sql)
        print('Successfully updated chains data!')
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when updating chains.')
            show_admin_options()


def get_chains():
    cursor = conn.cursor()

    sql = 'SELECT chain_name FROM chain;'

    try:
        cursor.execute(sql)
        chains = []
        rows = cursor.fetchall()
        for row in rows:
            (chain_name) = row 
            chains.append(chain_name)
        return chains
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when getting chains.')
            show_admin_options()


def get_recommended_restaurants_per_user():
    cursor = conn.cursor()

    sql = 'SELECT user_id, username, user_location, restaurant_name, \
                  avg_rating\
            FROM users_info LEFT JOIN \
            (SELECT user_rating.restaurant_id AS restaurant_id,\
                    restaurant_name,\
                    restaurant_location,\
                    AVG(rating) AS avg_rating\
            FROM rating NATURAL LEFT JOIN user_rating \
                NATURAL LEFT JOIN restaurant\
            GROUP BY user_rating.restaurant_id\
            HAVING avg_rating >= 8.0) AS rest_ratings\
        ON user_location = restaurant_location\
        WHERE restaurant_name IS NOT NULL\
        ORDER BY user_location;'
    
    try:
        cursor.execute(sql)
        recommendations = []
        rows = cursor.fetchall()
        for row in rows:
            (user_id, username, location, rest_name, avg_rating) = row
            recommendations.append({"user_id": user_id, "user_name": username,
                                    "user_location": location, 
                                    "restaurant": rest_name,
                                    "avg_rating": float(avg_rating)})
        return recommendations
    except mysql.connector.Error as err:
        if DEBUG:
            print(err)
            sys.exit(1)
        else:
            print('An error occurred when getting recommendations.')
            show_admin_options()


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