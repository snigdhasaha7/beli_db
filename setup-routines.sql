-- Beli Final Project Procedural SQL

DROP FUNCTION   IF EXISTS top_restaurant_loc;
DROP FUNCTION   IF EXISTS top_restaurant_friends;
DROP PROCEDURE  IF EXISTS sp_find_chains;
DROP TRIGGER    IF EXISTS trg_new_rating;
DROP PROCEDURE  IF EXISTS sp_cuisinetoprest_newrating;
DROP TABLE      IF EXISTS mv_top_restaurants_by_cuisine;
DROP VIEW       IF EXISTS chain_rests;
DROP PROCEDURE  IF EXISTS sp_insert_users;

-- UDF 1
DELIMITER !

-- Get the top rated restaurant in the user-given location.
-- Arbitrarily breaks ties if multiple restaurants are equally rated.
-- Returns NULL if location is not found.
CREATE FUNCTION top_restaurant_loc (loc VARCHAR(200)) 
                                    RETURNS VARCHAR(50) DETERMINISTIC
BEGIN
    DECLARE highest_rated_restaurant VARCHAR(200);

    -- We get the rating number, restaurant rated, and other relevant
    -- restaurant info by doing natural left joins in the inner query.
    -- From that, we filter by location (it needs to match the input)
    -- and do a group by to aggregate and get the average rating. This
    -- gives all restaurant names and their average ratings in the
    -- specified location. Then, we sort and select the top row to get
    -- the most highly rated restaurant's name.
    SELECT restaurant_name
    INTO highest_rated_restaurant
    FROM (SELECT restaurant_name, AVG(rating) AS avg_rating
          FROM rating NATURAL LEFT JOIN user_rating
                      NATURAL LEFT JOIN restaurant
          WHERE restaurant_location = loc
          GROUP BY restaurant_location, restaurant_name)
          AS rest_ratings_in_loc
    order by avg_rating DESC
    LIMIT 1;

    RETURN highest_rated_restaurant;

END !
-- Back to the standard SQL delimiter
DELIMITER ;





-- UDF 2
DELIMITER !

-- Get the highest rated restaurant among a user's friends. This
-- function is not based on average ratings for a restaurant,
-- rather, it is entirely dependent on the singular ratings of 
-- a user's friends.
-- Breaks ties arbitrarily.
-- Returns NULL if there are no such restaurants.
CREATE FUNCTION top_restaurant_friends (input_username VARCHAR(50)) 
                                    RETURNS VARCHAR(50) DETERMINISTIC
BEGIN
    DECLARE highest_rated_restaurant VARCHAR(200);

    -- The inner query gets all the ratings from a particular user's
    -- friends, along with other relevant information. Then, it sorts
    -- by rating, and chooses the highest rated restaurant by only taking
    -- the first row.
    SELECT restaurant_name
    INTO highest_rated_restaurant
    FROM (SELECT friend_id
          FROM users_info NATURAL LEFT JOIN friend
          WHERE username = input_username) AS user_friends
         LEFT JOIN user_rating ON friend_id = user_id
         NATURAL LEFT JOIN rating
         NATURAL LEFT JOIN restaurant
    WHERE rating IS NOT NULL
    ORDER BY rating DESC
    LIMIT 1;

    RETURN highest_rated_restaurant;

END !
-- Back to the standard SQL delimiter
DELIMITER ;





-- TODO insert documention
-- and justification for why view
CREATE VIEW chain_rests AS
    SELECT restaurant_id, restaurant_name, website FROM restaurant
        WHERE restaurant_name IN
            (SELECT restaurant_name FROM 
                restaurant 
                    NATURAL LEFT JOIN 
                in_cuisine 
                    NATURAL LEFT JOIN 
                in_category
            GROUP BY restaurant_name, cuisine_id, category_id
            HAVING COUNT(*) > 1);  

DELIMITER !
CREATE PROCEDURE sp_find_chains()
BEGIN 
    DECLARE rest_name VARCHAR(50);
    DECLARE rest_id INTEGER;
    DECLARE rest_web VARCHAR(200); 
    DECLARE DONE INT DEFAULT 0;
    DECLARE curr_chain_id INTEGER;

    DECLARE cur CURSOR FOR
        SELECT restaurant_id, restaurant_name, website FROM chain_rests;

    -- When fetch is complete, handler sets flag
    -- 02000 is MySQL error for "zero rows fetched"
    DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
        SET done = 1;

    OPEN cur;
        
    WHILE NOT done DO
        FETCH cur INTO rest_id, rest_name, rest_web;
        IF NOT DONE THEN
            IF rest_name NOT IN (SELECT chain_name FROM chain) THEN
                INSERT INTO chain (chain_name, chain_website) VALUES
                    (rest_name, rest_web);
            END IF;
            
            IF rest_id NOT IN (SELECT restaurant_id FROM belongs_in_chain) THEN
                SELECT chain_id FROM chain 
                    WHERE chain_name=rest_name
                INTO curr_chain_id;
                INSERT INTO belongs_in_chain VALUES (rest_id, curr_chain_id);
            END IF;
        END IF;
    END WHILE;
    CLOSE cur;

END !

DELIMITER ;





-- Trigger with procedure on a materialized view.
-- We keep an MV of the highest average rating restaurants by cuisine.
-- This MV will be updated every time a new rating is added.
CREATE TABLE mv_top_restaurants_by_cuisine (
    cuisine_id 	         INTEGER         NOT NULL,
    restaurant_id        INTEGER         NOT NULL,
    avg_rating           NUMERIC(3, 1)   NOT NULL
                         CHECK (avg_rating <= 10.0),
    PRIMARY KEY (cuisine_id, restaurant_id)
);

-- In the inner query, we get all restaurants with an average
-- rating of at least 8.0. Then, we left join cuisine with 
-- in_cuisine and the result of the inner query, so that
-- the highly rated restaurants become associated with their
-- cuisines. Some cuisines may not have any restaurants with 
-- a high enough average rating.
INSERT INTO mv_top_restaurants_by_cuisine (cuisine_id,
                                           restaurant_id,
                                           avg_rating)
SELECT cuisine_id, restaurant_id, ROUND(avg_rating, 1)
FROM cuisine NATURAL LEFT JOIN in_cuisine NATURAL LEFT JOIN
     (SELECT restaurant_id, avg(rating) AS avg_rating
      FROM rating NATURAL LEFT JOIN user_rating
      GROUP BY restaurant_id
      HAVING avg_rating >= 8.0) AS rest_ratings
WHERE avg_rating IS NOT NULL
ORDER BY cuisine_id ASC, avg_rating DESC;

DELIMITER !

CREATE PROCEDURE sp_cuisinetoprest_newrating(
    new_restaurant_id INTEGER
)
BEGIN 
    DECLARE rest_id INTEGER;
    DECLARE cuis_id INTEGER;
    DECLARE new_avg_rating NUMERIC(3, 1);

    DECLARE old_avg_rating NUMERIC(3, 1);

    -- Get the new information, most importantly the new average rating.
    SELECT cuisine_id, restaurant_id, ROUND(avg_rating, 1)
    INTO cuis_id, rest_id, new_avg_rating
    FROM (SELECT restaurant_id, AVG(rating) AS avg_rating
        FROM rating NATURAL LEFT JOIN user_rating
        WHERE restaurant_id = new_restaurant_id
        GROUP BY restaurant_id) AS rest_rating
        NATURAL LEFT JOIN in_cuisine;

    -- Get the old average.
    SELECT avg_rating
    INTO old_avg_rating
    FROM mv_top_restaurants_by_cuisine
    WHERE restaurant_id = new_restaurant_id;

    -- If this restaurant was already in the top restaurants per cuisine
    IF (old_avg_rating IS NOT NULL) THEN
        -- The new average rating is still high enough, so we just update
        -- the row in the MV.
        IF (new_avg_rating >= 8.0) THEN
            UPDATE mv_top_restaurants_by_cuisine
            SET avg_rating = new_avg_rating
            WHERE restaurant_id = new_restaurant_id;
        -- The new average rating is no longer high enough to be part of
        -- the MV, so this restaurant's row is deleted.
        ELSE
            DELETE FROM mv_top_restaurants_by_cuisine
            WHERE restaurant_id = new_restaurant_id;
        END IF;
    -- Otherwise, if this restaurant was not already in the MV
    ELSE
        -- If the new average ratin is at least 8.0 then it should
        -- be in the MV. If not, then it should not be, so we don't
        -- do anything.
        IF (new_avg_rating >= 8.0) THEN
            INSERT INTO mv_top_restaurants_by_cuisine (cuisine_id,
                                                    restaurant_id,
                                                    avg_rating)
            VALUES (cuis_id, rest_id, new_avg_rating);
        END IF;
    END IF;

END !

-- Handles new rows added to rating table, updates MV accordingly
CREATE TRIGGER trg_new_rating AFTER INSERT
       ON user_rating FOR EACH ROW
BEGIN
    CALL sp_cuisinetoprest_newrating(NEW.restaurant_id);
END !
DELIMITER ;





-- TODO document this
DELIMITER ! 
CREATE PROCEDURE sp_insert_users () 
BEGIN 
    DECLARE DONE INT DEFAULT 0;
    DECLARE cur_user_id             INT DEFAULT 0;
    DECLARE cur_username            VARCHAR(50);
    DECLARE cur_email               VARCHAR(50);
    DECLARE cur_pwd                 VARCHAR(50);
    DECLARE cur_real_name           VARCHAR(50);
    DECLARE cur_user_location       VARCHAR(200);
    DECLARE cur_user_picture        VARCHAR(200);

    DECLARE cur CURSOR FOR  
        SELECT * FROM users_temp;

    DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
        SET DONE = 1;

    OPEN cur;

    WHILE NOT DONE DO
        FETCH cur INTO cur_user_id, cur_username, cur_email, cur_pwd,
                       cur_real_name, cur_user_location, cur_user_picture;
        IF NOT DONE THEN
            CALL sp_add_user(cur_username, cur_email, cur_pwd,
                cur_real_name, cur_user_location, cur_user_picture);
        END IF;
    END WHILE;
    CLOSE cur;

END ! 
DELIMITER ;