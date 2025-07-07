-- ClickSafe Database Setup Script
-- Run this script in phpMyAdmin or MySQL command line

-- Create the database
CREATE DATABASE IF NOT EXISTS ClickSafeDB;
USE ClickSafeDB;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create scan_history table
CREATE TABLE IF NOT EXISTS scan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scan_type ENUM('url', 'file') NOT NULL,
    target VARCHAR(255) NOT NULL,
    status ENUM('clean', 'malicious', 'suspicious', 'error') NOT NULL,
    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create managed_lists table
CREATE TABLE IF NOT EXISTS managed_lists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_value VARCHAR(255) NOT NULL,
    item_type ENUM('url', 'domain') NOT NULL,
    list_type ENUM('whitelist', 'blacklist', 'graylist') NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_item (user_id, item_value)
);

-- Create guest_sessions table for guest users
CREATE TABLE IF NOT EXISTS guest_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    scan_count INT DEFAULT 0
);

-- Insert a default admin user for testing (password: admin123)
INSERT IGNORE INTO users (username, password) VALUES 
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi');

-- Show all tables to confirm creation
SHOW TABLES;

-- Show table structures
DESCRIBE users;
DESCRIBE scan_history;
DESCRIBE managed_lists;
DESCRIBE guest_sessions;

SELECT 'Database setup completed successfully!' as Status;
