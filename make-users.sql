-- Beli Final Project Users Setup

-- This file is intended to set up a temporary user table
-- before populating users_info with salt, password hash,
-- and personal information.

DROP TABLE IF EXISTS users_temp;

-- Similar structure to users_info but without salt and password hash.
CREATE TEMPORARY TABLE users_temp (
    user_id	            INTEGER,
    username		    VARCHAR(50)         NOT NULL    UNIQUE,
    email               VARCHAR(50),
    pwd                 VARCHAR(50),
    real_name           VARCHAR(50),
    user_location       VARCHAR(200),
    user_picture        VARCHAR(200),
    PRIMARY KEY (user_id)
);

-- Populate the temporary table from local data.
LOAD DATA LOCAL INFILE 'data/users_data.csv' INTO TABLE users_temp
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

