-- Beli Final Project DDL

DROP TABLE IF EXISTS belongs_in_chain;
DROP TABLE IF EXISTS chain;
DROP TABLE IF EXISTS user_rating;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS in_category;
DROP TABLE IF EXISTS in_cuisine;
DROP TABLE IF EXISTS restaurant;
DROP TABLE IF EXISTS cuisine;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS friend;
DROP TABLE IF EXISTS user;


-- Contains information about users of the app, including login
-- and authentication and personal information.
CREATE TABLE user (
    user_id	            INTEGER             AUTO_INCREMENT,
    -- screen username should be unique and reasonably short
    username		    VARCHAR(50)         NOT NULL    UNIQUE,
    -- fixed size salt for authentication
    salt                CHAR(8)             NOT NULL,
    -- fixed size pwd hash for authentication 
    password_hash		BINARY(64)          NOT NULL,
    -- user's real name, not mandatory
    real_name           VARCHAR(50),
    -- user's display photo, not mandatory
    -- should be a link to a file
    user_picture        VARCHAR(200),
    -- user's approx. location for restaurant recommendations, not mandatory
    user_location       VARCHAR(200),
    PRIMARY KEY (user_id)
);

-- A referencing relation to model a friendship between two users.
-- Each id has a cascading delete since if either user has been deleted, 
-- the row becomes meaningless.
-- Both friend_id and user_id are primary keys because it is a many-to-many
-- relationship.
CREATE TABLE friend (
    user_id             INTEGER,
    friend_id		    INTEGER,

    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) 
        REFERENCES user(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (friend_id) 
        REFERENCES user(user_id)
        ON DELETE CASCADE
);

-- Tracks the type of restaurants, e.g. cafe, bakery, etc
-- There will be materialized views for top restuarants and locations
-- per category.
CREATE TABLE category (
    category_id 	    INTEGER         AUTO_INCREMENT,
    category_name 	    VARCHAR(50)     NOT NULL    UNIQUE,
    -- should be a link to a file
    category_logo       VARCHAR(200),
    PRIMARY KEY (category_id)
);

-- Tracks cuisines, e.g. Japanese, Mediterranean, etc.
-- There will be materialized views for top restuarants and locations
-- per cuisine.
CREATE TABLE cuisine (
    cuisine_id 	        INTEGER         AUTO_INCREMENT,
    cuisine_name 	    VARCHAR(50)     NOT NULL    UNIQUE,
    -- should be a link to a file
    cuisine_logo        VARCHAR(200),
    PRIMARY KEY (cuisine_id)
);

-- Contains information about restaurants, with specific information such as
-- description, website, etc. Based on this table, there will be a
-- materialized view for average ratings of each restaurant.
CREATE TABLE restaurant (
    restaurant_id    	INTEGER             AUTO_INCREMENT,
    -- must have a restaurant name, but it need not be unique
    restaurant_name    	VARCHAR(50)         NOT NULL,
    -- website url not mandatory
    website    	        VARCHAR(200),
    -- approximate location of restaurant, for recommendations
    restaurant_location VARCHAR(200),
    -- describes price range with one of the following choices
    price_range    	    VARCHAR(4)
        CHECK (price_range IN (NULL, '$', '$$', '$$$', '$$$$')),

    PRIMARY KEY (restaurant_id)
);


-- A referencing relation to model a restaurant belonging to a certain
-- category, such as cafe, bakery, etc. One restaurant can only belong to
-- one category, but each category can have multiple restaurants associated
-- with them, hence restaurant_id is the primary key.
CREATE TABLE in_category (
    restaurant_id   INTEGER,
    category_id     INTEGER,

    PRIMARY KEY (restaurant_id),
    -- if either the restaurant or the category is removed, 
    -- this relationship can be removed.
    FOREIGN KEY (restaurant_id) REFERENCES restaurant(restaurant_id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON DELETE CASCADE
);

-- A referencing relation to model a restaurant belonging to potentially many
-- cuisines. Hence, both restaurant_id and cuisine_id are primary keys.
CREATE TABLE in_cuisine (
    restaurant_id   INTEGER,
    cuisine_id      INTEGER,

    PRIMARY KEY (restaurant_id, cuisine_id),
    -- if either the restaurant or the cuisine is removed, 
    -- this relationship can be removed.
    FOREIGN KEY (restaurant_id) REFERENCES restaurant(restaurant_id)
        ON DELETE CASCADE,
    FOREIGN KEY (cuisine_id) REFERENCES cuisine(cuisine_id)
        ON DELETE CASCADE
);

-- Represents a ranking in the database, with a unique database-wide id, 
-- and a mandatory rating value, and an optional rating_description/
CREATE TABLE rating (
    rating_id           INTEGER             AUTO_INCREMENT,
    -- rating should be between 0 (incl) and 10 (excl), allowing 1 decimal
    -- each rating row must have a rating
    rating 	            NUMERIC(2, 1)       NOT NULL,
    -- optional description of restaurant or reasoning for rating
    rating_description 	VARCHAR(5000),

    PRIMARY KEY (rating_id)
);

-- A referencing relation to model a user creating a rating of a
-- restaurant. A user and a restaurant can only be associated with one
-- rating.
CREATE TABLE user_rating (
    user_id          INTEGER,
    restaurant_id    INTEGER,
    rating_id        INTEGER,

    PRIMARY KEY (user_id, restaurant_id),
    -- if any of these foreign keys are deleted, this ranking should be
    -- removed.
    FOREIGN KEY (user_id) REFERENCES user(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurant(restaurant_id)
        ON DELETE CASCADE,
    FOREIGN KEY (rating_id) REFERENCES rating(rating_id)
        ON DELETE CASCADE
);

-- Represents a chain in the database, such as McDonald's or Olive Garden,
-- to identify if restaurants are part of this chain.
CREATE TABLE chain (
    chain_id         INTEGER         AUTO_INCREMENT,
    chain_name       VARCHAR(100)    NOT NULL,
    chain_website    VARCHAR(100),

    PRIMARY KEY (chain_id)
);

-- A referencing relation to model a restaurant belonging to a chain. 
-- A restaurant can only be part of one chain but a chain can have multiple
-- restaurants, hence we use restaurant_id as the primary key.
CREATE TABLE belongs_in_chain (
    restaurant_id    INTEGER,
    chain_id         INTEGER,

    PRIMARY KEY (restaurant_id), 
    -- if the restaurant or the chain is removed, we can remove
    -- this relationship
    FOREIGN KEY (restaurant_id) REFERENCES restaurant(restaurant_id)
        ON DELETE CASCADE,
    FOREIGN KEY (chain_id) REFERENCES chain(chain_id)
        ON DELETE CASCADE
);

-- We will look up restaurants based on locations for recommendations
-- frequently, so this index will help. Location is not a primary or
-- foreign key.
CREATE INDEX loc_idx ON restaurant(restaurant_location);