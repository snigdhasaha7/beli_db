DROP TABLE IF EXISTS users_info

CREATE TABLE users_temp (
    user_id	            INTEGER             AUTO_INCREMENT,
    username		    VARCHAR(50)         NOT NULL    UNIQUE,
    pwd                 VARCHAR(50),
    real_name           VARCHAR(50),
    user_picture        VARCHAR(200),
    user_location       VARCHAR(200),
    PRIMARY KEY (user_id)
);

LOAD DATA LOCAL INFILE 'data/users_data.csv' INTO TABLE users_temp
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;


-- TODO INSERT CURSOR FUNCTION HERE


DROP TABLE users_temp;