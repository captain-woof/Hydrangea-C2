CREATE DATABASE IF NOT EXISTS hydrangea;
USE hydrangea;

-- Users table
CREATE TABLE users (
  username VARCHAR(100) PRIMARY KEY,
  password VARCHAR(255) NOT NULL,
  role ENUM('admin', 'operator', 'observer') NOT NULL
);

-- Default admin:admin user
INSERT INTO users(username, password, role) VALUES('admin', '$2b$12$2ruRCpEiwlzER3keMvVTfeQyMrUcxqViiFmTG83ENAkpT.Os04kou', 'admin');

-- Tasks table
CREATE TABLE tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  originClientId VARCHAR(255) NOT NULL,
  agentId VARCHAR(255) NOT NULL,
  task TEXT NOT NULL,
  output TEXT,
  taskedAt INT, -- unix time (secs)
  outputAt INT -- unix time (secs)
);

-- Agents table
CREATE TABLE agents (
  id VARCHAR(255) PRIMARY KEY,
  host VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL,
  lastCheckinAt INT NOT NULL
);