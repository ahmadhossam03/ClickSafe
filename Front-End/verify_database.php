<?php
/**
 * Database Structure Verification
 * Checks if the subscription system database columns exist
 */

require_once 'db_connect.php';

echo "<h2>ClickSafe Database Structure Verification</h2>";

// Check if users table exists
$table_check = $conn->query("SHOW TABLES LIKE 'users'");
if ($table_check->num_rows === 0) {
    echo "<p style='color: red;'>❌ Users table does not exist!</p>";
    exit;
}

echo "<p style='color: green;'>✅ Users table exists</p>";

// Check users table structure
$columns = $conn->query("DESCRIBE users");
$existing_columns = [];

echo "<h3>Users Table Structure:</h3>";
echo "<table border='1' cellpadding='10'>";
echo "<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th><th>Default</th><th>Extra</th></tr>";

while ($row = $columns->fetch_assoc()) {
    $existing_columns[] = $row['Field'];
    echo "<tr>";
    echo "<td>" . $row['Field'] . "</td>";
    echo "<td>" . $row['Type'] . "</td>";
    echo "<td>" . $row['Null'] . "</td>";
    echo "<td>" . $row['Key'] . "</td>";
    echo "<td>" . $row['Default'] . "</td>";
    echo "<td>" . $row['Extra'] . "</td>";
    echo "</tr>";
}
echo "</table>";

// Check for required subscription columns
$required_columns = ['subscription', 'daily_scan_count', 'last_scan_date'];
$missing_columns = [];

echo "<h3>Subscription System Column Check:</h3>";
foreach ($required_columns as $column) {
    if (in_array($column, $existing_columns)) {
        echo "<p style='color: green;'>✅ Column '$column' exists</p>";
    } else {
        echo "<p style='color: red;'>❌ Column '$column' is missing</p>";
        $missing_columns[] = $column;
    }
}

// If columns are missing, provide SQL to add them
if (!empty($missing_columns)) {
    echo "<h3>SQL Commands to Add Missing Columns:</h3>";
    echo "<pre style='background: #f5f5f5; padding: 10px; border-radius: 5px;'>";
    
    foreach ($missing_columns as $column) {
        switch ($column) {
            case 'subscription':
                echo "ALTER TABLE users ADD COLUMN subscription ENUM('free', 'premium') DEFAULT 'free';\n";
                break;
            case 'daily_scan_count':
                echo "ALTER TABLE users ADD COLUMN daily_scan_count INT DEFAULT 0;\n";
                break;
            case 'last_scan_date':
                echo "ALTER TABLE users ADD COLUMN last_scan_date DATE;\n";
                break;
        }
    }
    echo "</pre>";
} else {
    echo "<p style='color: green; font-weight: bold;'>🎉 All subscription system columns are present!</p>";
    
    // Test data
    echo "<h3>Sample User Data:</h3>";
    $users = $conn->query("SELECT id, username, subscription, daily_scan_count, last_scan_date FROM users LIMIT 5");
    
    if ($users->num_rows > 0) {
        echo "<table border='1' cellpadding='10'>";
        echo "<tr><th>ID</th><th>Username</th><th>Subscription</th><th>Daily Scan Count</th><th>Last Scan Date</th></tr>";
        
        while ($user = $users->fetch_assoc()) {
            echo "<tr>";
            echo "<td>" . $user['id'] . "</td>";
            echo "<td>" . $user['username'] . "</td>";
            echo "<td>" . $user['subscription'] . "</td>";
            echo "<td>" . $user['daily_scan_count'] . "</td>";
            echo "<td>" . ($user['last_scan_date'] ?: 'Never') . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    } else {
        echo "<p>No users found in database.</p>";
    }
}

echo "<br><p><a href='main_page.php'>← Back to Main Page</a> | <a href='test_subscription_system.php'>Test Subscription System →</a></p>";

$conn->close();
?>
