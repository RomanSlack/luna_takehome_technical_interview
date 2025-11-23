-- Seed data for Luna Take Home project
-- Run this after initializing the database schema

-- Insert test users
INSERT INTO users (id, name, avatar_url, bio) VALUES
(1, 'Alice Johnson', 'https://i.pravatar.cc/150?img=1', 'Love exploring new cafes and restaurants'),
(2, 'Bob Smith', 'https://i.pravatar.cc/150?img=2', 'Foodie and music enthusiast'),
(3, 'Charlie Davis', 'https://i.pravatar.cc/150?img=3', 'Always up for an adventure'),
(4, 'Diana Martinez', 'https://i.pravatar.cc/150?img=4', 'Coffee addict and bookworm'),
(5, 'Ethan Brown', 'https://i.pravatar.cc/150?img=5', 'Live music lover');

-- Insert friendships
INSERT INTO friendships (user_id, friend_id, strength) VALUES
(1, 2, 5.0),
(1, 3, 4.0),
(1, 4, 3.5),
(2, 1, 5.0),
(2, 3, 4.5),
(2, 5, 3.0),
(3, 1, 4.0),
(3, 2, 4.5),
(3, 4, 2.5),
(4, 1, 3.5),
(4, 3, 2.5),
(4, 5, 4.0),
(5, 2, 3.0),
(5, 4, 4.0);

-- Insert venues (New York City locations)
INSERT INTO venues (id, name, category, address, latitude, longitude, description) VALUES
(1, 'Blue Bottle Coffee', 'cafe', '450 W 15th St, New York, NY 10011', 40.7425, -74.0071, 'Artisanal coffee in the heart of Chelsea'),
(2, 'Gramercy Tavern', 'restaurant', '42 E 20th St, New York, NY 10003', 40.7389, -73.9884, 'Contemporary American cuisine in an elegant setting'),
(3, 'The Met Museum', 'museum', '1000 5th Ave, New York, NY 10028', 40.7794, -73.9632, 'World-renowned art museum'),
(4, 'Brooklyn Bowl', 'entertainment', '61 Wythe Ave, Brooklyn, NY 11249', 40.7215, -73.9577, 'Bowling alley with live music and great food'),
(5, 'Levain Bakery', 'cafe', '167 W 74th St, New York, NY 10023', 40.7787, -73.9824, 'Famous for their huge cookies'),
(6, 'Le Bernardin', 'restaurant', '155 W 51st St, New York, NY 10019', 40.7614, -73.9776, 'Three Michelin star seafood restaurant'),
(7, 'Smorgasburg', 'market', 'East River State Park, Brooklyn, NY 11249', 40.7214, -73.9585, 'Open-air food market with amazing vendors'),
(8, 'Comedy Cellar', 'entertainment', '117 MacDougal St, New York, NY 10012', 40.7299, -74.0005, 'Iconic comedy club in Greenwich Village'),
(9, 'Ippudo', 'restaurant', '65 4th Ave, New York, NY 10003', 40.7302, -73.9896, 'Authentic Japanese ramen'),
(10, 'Central Park', 'park', 'Central Park, New York, NY 10022', 40.7829, -73.9654, 'Iconic urban park perfect for walks and picnics');

-- Insert some interests
INSERT INTO user_interests (user_id, venue_id, status, created_at) VALUES
(1, 1, 'INTERESTED', NOW()),
(1, 3, 'INTERESTED', NOW()),
(2, 1, 'INTERESTED', NOW()),
(2, 4, 'CONFIRMED', NOW()),
(2, 6, 'INTERESTED', NOW()),
(3, 1, 'INTERESTED', NOW()),
(3, 7, 'CONFIRMED', NOW()),
(3, 10, 'INTERESTED', NOW()),
(4, 1, 'CONFIRMED', NOW()),
(4, 3, 'INTERESTED', NOW()),
(4, 5, 'INTERESTED', NOW()),
(5, 4, 'CONFIRMED', NOW()),
(5, 8, 'INTERESTED', NOW());

-- Reset sequences to continue from max ID
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('venues_id_seq', (SELECT MAX(id) FROM venues));
SELECT setval('friendships_id_seq', (SELECT MAX(id) FROM friendships));
SELECT setval('user_interests_id_seq', (SELECT MAX(id) FROM user_interests));
