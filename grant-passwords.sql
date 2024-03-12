CREATE USER 'appadmin'@'localhost' IDENTIFIED BY 'adminpw';
CREATE USER 'appclient'@'localhost' IDENTIFIED BY 'clientpw';
-- Can add more users or refine permissions
GRANT ALL PRIVILEGES ON belidb.* TO 'appadmin'@'localhost';
GRANT SELECT ON belidb.* TO 'appclient'@'localhost';
FLUSH PRIVILEGES;
