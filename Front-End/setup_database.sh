#!/bin/bash
# Database setup script for ClickSafe

echo "Setting up ClickSafe Database..."

# Create the database and tables using MySQL command line
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS ClickSafeDB;
USE ClickSafeDB;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Create scan_history table
CREATE TABLE IF NOT EXISTS scan_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scan_type ENUM('url', 'file') NOT NULL,
    target VARCHAR(255) NOT NULL,
    status ENUM('clean', 'malicious', 'suspicious') NOT NULL,
    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

SHOW TABLES;
"

echo "Database setup completed!"
