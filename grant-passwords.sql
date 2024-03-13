DROP USER 'appadmin'@'localhost';
DROP USER 'appclient'@'localhost';

CREATE USER 'appadmin'@'localhost' IDENTIFIED BY 'adminpw';
CREATE USER 'appclient'@'localhost' IDENTIFIED BY 'clientpw';
-- Can add more users or refine permissions
GRANT ALL PRIVILEGES ON belidb.* TO 'appadmin'@'localhost';
GRANT ALL PRIVILEGES ON belidb.* TO 'appclient'@'localhost';
FLUSH PRIVILEGES;
