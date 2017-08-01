DROP TABLE IF EXISTS `commute_pair`;
CREATE TABLE `commute_pair` (
  `id` SERIAL
  , `origin` VARCHAR(255)
  , `destination` VARCHAR(255)
  , `arrival_time` VARCHAR(5)
);


INSERT INTO commute_pair (
  origin
  , destination
  , arrival_time
) VALUES
  ('4887 Eagle Blvd, Frederick, CO 80504, USA'
    ,'600 17th St #1000n, Denver, CO 80202, USA'
    ,'08:00')
