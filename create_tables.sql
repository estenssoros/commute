DROP TABLE IF EXISTS `commute_event`;
CREATE TABLE `commute_event` (
  `id` SERIAL
  , `commute_pair` INT
  , `origin` VARCHAR(255)
  , `destination` VARCHAR(255)
  , `arrival_time` DATETIME
);


DROP TABLE IF EXISTS `astral`;
CREATE TABLE `astral` (
  `id` SERIAL
  , `date` VARCHAR(10)
  , `dawn` INT
  , `dusk` INT
  , `moon_phase` DECIMAL(3,1)
  , `noon` INT
  , `sunrise` INT
  , `sunset` INT
);


DROP TABLE IF EXISTS `to_from`;
CREATE TABLE `to_from` (
  `id` SERIAL
  , `from` VARCHAR(255)
  , `to` VARCHAR(255)
);


DROP TABLE IF EXISTS `distance_matrix`;
CREATE TABLE `distance_matrix` (
  `id` SERIAL
  ,`to_from_id` INT
  ,`distance` INT
  ,`duration` INT
  ,`traffic` INT
);


DROP TABLE IF EXISTS `weather`;
CREATE TABLE `weather` (
  `id` SERIAL
  , `1hr_precip` DECIMAL(4,1)
  , `apparent_temperature` DECIMAL(4,1)
  , `ceiling` INT
  , `dew_point` DECIMAL(4,1)
  , `is_day_time` TINYINT
  , `past_24_hour_dep` DECIMAL(4,1)
  , `precip` DECIMAL(4,1)
  , `precip_1_hour` DECIMAL(4,1)
  , `precip_3_hour` DECIMAL(4,1)
  , `precip_6_hour` DECIMAL(4,1)
  , `precip_9_hour` DECIMAL(4,1)
  , `precip_12_hour` DECIMAL(4,1)
  , `precip_18_hour` DECIMAL(4,1)
  , `precip_24_hour` DECIMAL(4,1)
  , `pressure` DECIMAL(4,1)
  , `pressure_tendancy` VARCHAR(12)
  , `temp_6_min` DECIMAL(4,1)
  , `temp_6_max` DECIMAL(4,1)
  , `temp_12_min` DECIMAL(4,1)
  , `temp_12_max` DECIMAL(4,1)
  , `temp_24_max` DECIMAL(4,1)
  , `temperature` DECIMAL(4,1)
  , `uv_index` INT
  , `visibilty` DECIMAL(4,1)
  , `weather` VARCHAR(15)
  , `wet_bulb_temp` DECIMAL(4,1)
  , `wind_chill` DECIMAL(4,1)
  , `wind_direction` INT
  , `wind_gust` DECIMAL(4,1)
  , `wind_speed` DECIMAL(4,1)
);
