CREATE DATABASE IF NOT EXISTS hydrangea;
USE hydrangea;

-- table for c2 team server users
CREATE TABLE users (
  username VARCHAR(100) PRIMARY KEY,
  password VARCHAR(255) NOT NULL,
  role ENUM('admin', 'operator', 'observer') NOT NULL
);

-- default admin:admin user
INSERT INTO users(username, password, role) VALUES('admin', '$2b$12$2ruRCpEiwlzER3keMvVTfeQyMrUcxqViiFmTG83ENAkpT.Os04kou', 'admin');