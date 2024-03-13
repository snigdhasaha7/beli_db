-- Beli Final Project Queries
-- The first three match relational algebras 1, 2, and 3, respectively.

-- Query 1
-- Gets, per user, the number of restaurants that they
-- have rated and the average rating they have given.
-- Only gets users with at least 1 rating.
SELECT username, COUNT(rating) AS num_ratings, AVG(rating) AS avg_rating
FROM user_rating NATURAL LEFT JOIN rating NATURAL LEFT JOIN users_info
GROUP BY username;


-- Query 2
-- Gets the average rating of all chain restaurants.
SELECT chain_name, AVG(rating) AS avg_rating
FROM (SELECT chain_name, restaurant_id
      FROM chain NATURAL LEFT JOIN belongs_in_chain) AS chain_rests
      NATURAL LEFT JOIN user_rating NATURAL LEFT JOIN rating
GROUP BY chain_name;


-- Query 3
-- Censor vulgarity in the rating descriptions.
-- You can imagine censoring harsher things than "crap."
UPDATE rating
SET rating_description = REPLACE(rating_description, "crap", "****")
WHERE rating_description LIKE '%crap%';


-- Query 4
-- Gets recommended restaurants for each user.
-- It will recommend any restaurant with an average
-- rating of at least 8.0 that is in the same city as
-- the user. Users who live in cities with no restaurants
-- rated that highly do not get recommendations.
-- That is, they will not be part of the output at all.
SELECT user_id, username, user_location, restaurant_name, avg_rating
FROM users_info LEFT JOIN
    (SELECT user_rating.restaurant_id AS restaurant_id,
            restaurant_name,
            restaurant_location,
            AVG(rating) AS avg_rating
     FROM rating NATURAL LEFT JOIN user_rating NATURAL LEFT JOIN restaurant
     GROUP BY user_rating.restaurant_id
     HAVING avg_rating >= 8.0) AS rest_ratings
     ON user_location = restaurant_location
WHERE restaurant_name IS NOT NULL
ORDER BY user_location;