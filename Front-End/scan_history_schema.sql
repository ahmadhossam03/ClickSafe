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