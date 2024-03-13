-- Beli Final Project Password Management

DROP FUNCTION IF EXISTS make_salt; 
DROP PROCEDURE IF EXISTS sp_add_user;
DROP FUNCTION IF EXISTS authenticate; 
DROP PROCEDURE IF EXISTS sp_change_password;

-- (Provided) This function generates a specified number of characters for using as a
-- salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt!  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;


-- Adds a new user to the users_info table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(
                  new_username VARCHAR(50),
                  new_email VARCHAR(50),
                  password VARCHAR(50),
                  new_real_name VARCHAR(50),
                  new_user_location VARCHAR(200),
                  new_user_picture VARCHAR(200)
                )
BEGIN
  -- made temporary variables for ease
  DECLARE new_salt VARCHAR(20) DEFAULT '';
  DECLARE new_password_hash BINARY(64); 
  
  -- called helper
  SET new_salt = make_salt(8); 

  -- concatenation with salt and using SHA2
  SET new_password_hash = SHA2(CONCAT(new_salt, password), 256); 

  -- insertion into table
  INSERT INTO users_info (username, email, salt, password_hash,
                        real_name, user_location, user_picture)
    VALUES (new_username, new_email,
            new_salt, new_password_hash, new_real_name,
            new_user_location, new_user_picture);
END !
DELIMITER ;


-- Authenticates the specified username and password against the data
-- in the users_info table.  Returns 1 if the user appears in the table, and the
-- specified password hashes to the value for the user. Otherwise returns 0.
DELIMITER !
CREATE FUNCTION authenticate(username VARCHAR(20), password VARCHAR(20))
RETURNS TINYINT DETERMINISTIC
BEGIN

  -- since this is deterministically CHAR(8)
  -- used that type for this variable
  DECLARE salt_check CHAR(8);
  
  -- extracted the salt from the user table
  SELECT salt FROM users_info WHERE users_info.username=username
  INTO salt_check;

  -- if the username does not exist, we return 0
  IF username NOT IN (SELECT username FROM users_info) THEN 
    RETURN 0;
  -- otherwise, we check the concatenation with the stored salt
  ELSEIF SHA2(CONCAT(salt_check, password), 256) = 
          (SELECT password_hash FROM users_info 
            WHERE users_info.username=username)
          THEN RETURN 1; 
  ELSE RETURN 0;
  END IF;
END !
DELIMITER ;


-- Create a procedure sp_change_password to generate a new salt and 
-- change the given user's password to the given password 
-- (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_password(username VARCHAR(20), 
                                    new_password VARCHAR(20))
BEGIN
  -- same idea as the add_user function
  DECLARE new_salt VARCHAR(20) DEFAULT '';
  DECLARE new_password_hash BINARY(64); 
  
  SELECT make_salt(8) INTO new_salt; 

  SELECT SHA2(CONCAT(new_salt, new_password), 256) INTO new_password_hash;

  -- only difference is using UPDATE
  UPDATE users_info SET
    salt = new_salt, 
    password_hash = new_password_hash
  WHERE users_info.username=username;
END !
DELIMITER ;
