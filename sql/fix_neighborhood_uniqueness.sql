-- Fix neighborhood uniqueness constraint
-- Allow same neighborhood names in different cities/states
-- Only require uniqueness within user + city + state combination

-- First, drop the existing unique constraint
ALTER TABLE `neighborhoods` DROP INDEX `unique_user_neighborhood`;

-- Add new unique constraint that includes city and state
ALTER TABLE `neighborhoods` ADD UNIQUE KEY `unique_user_city_state_neighborhood` (`user_id`, `city`, `state`, `name`);
