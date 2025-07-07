@echo off
echo Setting up ClickSafe Database...

REM Navigate to MySQL bin directory (adjust path if needed)
set MYSQL_PATH=C:\xampp\mysql\bin

REM Execute MySQL commands to create database and tables
"%MYSQL_PATH%\mysql.exe" -u root -p -e "CREATE DATABASE IF NOT EXISTS ClickSafeDB; USE ClickSafeDB; CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_login TIMESTAMP NULL); CREATE TABLE IF NOT EXISTS scan_history (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, scan_type ENUM('url', 'file') NOT NULL, target VARCHAR(255) NOT NULL, status ENUM('clean', 'malicious', 'suspicious') NOT NULL, scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS managed_lists (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, item_value VARCHAR(255) NOT NULL, item_type ENUM('url', 'domain') NOT NULL, list_type ENUM('whitelist', 'blacklist', 'graylist') NOT NULL, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, UNIQUE KEY unique_user_item (user_id, item_value)); CREATE TABLE IF NOT EXISTS guest_sessions (id INT AUTO_INCREMENT PRIMARY KEY, session_id VARCHAR(255) NOT NULL UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, scan_count INT DEFAULT 0); SHOW TABLES;"

echo Database setup completed!
pause
