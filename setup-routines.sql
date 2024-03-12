DROP FUNCTION top_restaurant_loc;
DROP PROCEDURE sp_find_chains;
DROP TRIGGER trg_new_rating;


-- UDF

DELIMITER !

-- Get the top rated restaurant in a given location
CREATE FUNCTION top_restaurant_loc (loc VARCHAR(200)) 
                                    RETURNS VARCHAR(50) DETERMINISTIC
BEGIN
    DECLARE highest_rated_restaurant VARCHAR(200);
    DECLARE highest_avg_rating NUMERIC(2, 1);

    SELECT restaurant_name, MAX(avg_rating) AS max_avg_rating
    INTO highest_rated_restaurant, 
    FROM (SELECT restaurant_id, AVG(rating) AS avg_rating
          FROM rating LEFT JOIN user_rating
          GROUP BY restaurant_id) AS rest_ratings
          LEFT JOIN restaurant
    WHERE restaurant_loc = loc;

    RETURN highest_rated_restuarant;

END !
-- Back to the standard SQL delimiter
DELIMITER ;








DELIMITER !
CREATE PROCEDURE sp_find_chains(
)
BEGIN 
    CREATE TEMPORARY TABLE chain_rests
        SELECT restaurant_id, restaurant_name, website FROM restaurant
            WHERE restaurant_name IN
                (SELECT restaurant_name FROM restaurant
                GROUP BY restaurant_name, cuisine_id, category_id
                HAVING COUNT(*) > 1);
    
    DECLARE rest_name VARCHAR(50);
    DECLARE rest_id INTEGER;
    DECLARE rest_web VARCHAR(200); 
    DECLARE DONE INT DEFAULT 0;
    DECLARE curr_chain_id INTEGER;

    DECLARE cur CURSOR FOR
        SELECT restaurant_id, restaurant_name, website FROM chain_rests;
        
    WHILE NOT done DO
        FETCH cur INTO rest_id, rest_name, rest_web;
        FETCH id_cur
        IF NOT DONE THEN
            IF rest_name NOT IN (SELECT chain_name FROM chain) THEN
                INSERT INTO chain (chain_name, chain_website) VALUES
                    (rest_name, rest_web);
            END IF 
            
            IF rest_id NOT IN (SELECT restaurant_id FROM belongs_in_chain) THEN
                SELECT chain_id FROM chain 
                    WHERE chain_name=rest_name
                INTO curr_chain_id;

                INSERT INTO belongs_in_chain VALUES (curr_chain_id, rest_id);
            END IF
        END IF
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
    avg_rating           NUMERIC(2, 1)   NOT NULL,
    PRIMARY KEY (cuisine_name, restuarant_name),
    FOREIGN KEY (cuisine_id)
        REFERENCES cuisine(cuisine_id),
    FOREIGN KEY (restaurant_id)
        REFERENCES restaurant(restaurant_id)
);

INSERT INTO mv_top_restaurants_by_cuisine (cuisine_id,
                                           restaurant_id,
                                           avg_rating)
SELECT cuisine_id,
       restaurant_id,
       AVG(rating) AS avg_rating
FROM rating LEFT JOIN user_rating LEFT JOIN in_cuisine
GROUP BY cuisine_id, restaurant_id
HAVING avg_rating >= 8.0
ORDER BY cuisine_id ASC, avg_rating DESC;


DELIMITER !

CREATE PROCEDURE sp_cuisinetoprest_newrating(
    new_restaurant_id INTEGER,
    new_rating NUMERIC(2, 1)
)
BEGIN 
    CREATE TABLE new_mv (
        cuisine_id 	         INTEGER         NOT NULL,
        restaurant_id        INTEGER         NOT NULL,
        avg_rating           NUMERIC(2, 1)   NOT NULL,
        PRIMARY KEY (cuisine_name, restuarant_name),
        FOREIGN KEY (cuisine_id)
            REFERENCES cuisine(cuisine_id),
        FOREIGN KEY (restaurant_id)
            REFERENCES restaurant(restaurant_id)
    );

    INSERT INTO new_mv (cuisine_id,
                        restaurant_id,
                        avg_rating)
    SELECT cuisine_id,
        restaurant_id,
        AVG(rating) AS avg_rating
    FROM rating LEFT JOIN user_rating LEFT JOIN in_cuisine
    GROUP BY cuisine_id, restaurant_id
    HAVING avg_rating >= 8.0
    ORDER BY cuisine_id ASC, avg_rating DESC;

    DROP TABLE mv_top_restaurants_by_cuisine;

    RENAME TABLE new_mv TO mv_top_restaurants_by_cuisine;

END !

-- Handles new rows added to rating table, updates MV accordingly
CREATE TRIGGER trg_new_rating AFTER INSERT
       ON rating FOR EACH ROW
BEGIN
    CALL sp_highest_(OLD.branch_name, OLD.balance);
END !
DELIMITER ;
