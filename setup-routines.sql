DROP FUNCTION   IF EXISTS top_restaurant_loc;
DROP FUNCTION   IF EXISTS top_restaurant_friends;
DROP PROCEDURE  IF EXISTS sp_find_chains;
DROP TRIGGER    IF EXISTS trg_new_rating;
DROP PROCEDURE  IF EXISTS sp_cuisinetoprest_newrating;
DROP TABLE      IF EXISTS mv_top_restaurants_by_cuisine;
DROP VIEW       IF EXISTS chain_rests;
DROP PROCEDURE  IF EXISTS sp_insert_users;

-- UDF

DELIMITER !

-- Get the top rated restaurant in a given location
CREATE FUNCTION top_restaurant_loc (loc VARCHAR(200)) 
                                    RETURNS VARCHAR(50) DETERMINISTIC
BEGIN
    DECLARE highest_rated_restaurant VARCHAR(200);

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






-- UDF

DELIMITER !

-- Get the highest rated restaurant among a user's friends
CREATE FUNCTION top_restaurant_friends (input_username VARCHAR(50)) 
                                    RETURNS VARCHAR(50) DETERMINISTIC
BEGIN
    DECLARE highest_rated_restaurant VARCHAR(200);

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

PROCEDURE

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

                INSERT INTO belongs_in_chain VALUES (curr_chain_id, rest_id);
            END IF;
        END IF;
    END WHILE;
    CLOSE cur;

END !

DELIMITER ;




-- Trigger with procedure on materialized view
-- Have an MV of the highest average rating restaurants by cuisine
-- Will update this MV every time a new rating is added

CREATE TABLE mv_top_restaurants_by_cuisine (
    cuisine_id 	         INTEGER         NOT NULL,
    restaurant_id        INTEGER         NOT NULL,
    avg_rating           NUMERIC(3, 1)   NOT NULL
                         CHECK (avg_rating <= 10.0),
    PRIMARY KEY (cuisine_id, restaurant_id)
);

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

    SELECT cuisine_id, restaurant_id, ROUND(avg_rating, 1)
    INTO cuis_id, rest_id, new_avg_rating
    FROM (SELECT restaurant_id, AVG(rating) AS avg_rating
        FROM rating NATURAL LEFT JOIN user_rating
        WHERE restaurant_id = new_restaurant_id
        GROUP BY restaurant_id) AS rest_rating
        NATURAL LEFT JOIN in_cuisine;

    SELECT avg_rating
    INTO old_avg_rating
    FROM mv_top_restaurants_by_cuisine
    WHERE restaurant_id = new_restaurant_id;

    IF (old_avg_rating IS NOT NULL) THEN
        IF (new_avg_rating >= 8.0) THEN
            UPDATE mv_top_restaurants_by_cuisine
            SET avg_rating = new_avg_rating
            WHERE restaurant_id = new_restaurant_id;
        ELSE
            DELETE FROM mv_top_restaurants_by_cuisine
            WHERE restaurant_id = new_restaurant_id;
        END IF;
    ELSE
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






DELIMITER ! 
CREATE PROCEDURE sp_insert_users () 
BEGIN 
    DECLARE DONE INT DEFAULT 0;
    DECLARE cur_user_id             INT DEFAULT 0;
    DECLARE cur_username            VARCHAR(50);
    DECLARE cur_email               VARCHAR(50);
    DECLARE cur_pwd                 VARCHAR(50);
    DECLARE cur_real_name           VARCHAR(50);
    DECLARE cur_user_picture        VARCHAR(200);
    DECLARE cur_user_location       VARCHAR(200);

    DECLARE cur CURSOR FOR  
        SELECT * FROM users_temp;

    DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
        SET DONE = 1;

    OPEN cur;

    WHILE NOT DONE DO
        FETCH cur INTO cur_user_id, cur_username, cur_email, cur_pwd,
                       cur_real_name, cur_user_picture, cur_user_location;
        IF NOT DONE THEN
            CALL sp_add_user(cur_user_id, cur_username, cur_email, cur_pwd,
                cur_real_name, cur_user_picture, cur_user_location);
        END IF;
    END WHILE;
    CLOSE cur;

END ! 
DELIMITER ;

CALL sp_insert_users();