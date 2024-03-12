DROP PROCEDURE sp_find_chains;

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