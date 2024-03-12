-- Beli db Queries

-- Query 1
-- Gets recommendations for each user
-- does 2 joins and an aggregation
SELECT user_id, restaurant_id, restaurant_name, avg_rating
FROM users_info LEFT JOIN ON user_location = restaurant_location
    (SELECT user_ratings.restaurant_id AS restaurant_id,
            restaurant_name,
            AVG(rating) AS avg_rating
     FROM user_ratings NATURAL LEFT JOIN restaurant
     GROUP BY user_ratings.restaurant_id
     HAVING rating >= 8.0) AS rest_ratings



