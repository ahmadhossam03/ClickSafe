<?php
// Test database connection and show table structure
include 'db_connect.php';

echo "<h2>Database Connection Test</h2>";

// Test connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} else {
    echo "<p style='color: green;'>✅ Successfully connected to database: " . $conn->server_info . "</p>";
}

// Show current database
$result = $conn->query("SELECT DATABASE()");
$row = $result->fetch_array();
echo "<p><strong>Current Database:</strong> " . $row[0] . "</p>";

// Show all tables
echo "<h3>Tables in Database:</h3>";
$result = $conn->query("SHOW TABLES");
if ($result->num_rows > 0) {
    echo "<ul>";
    while($row = $result->fetch_array()) {
        echo "<li>" . $row[0] . "</li>";
    }
    echo "</ul>";
} else {
    echo "<p>No tables found</p>";
}

// Show users table structure
echo "<h3>Users Table Structure:</h3>";
$result = $conn->query("DESCRIBE users");
if ($result->num_rows > 0) {
    echo "<table border='1'>";
    echo "<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th><th>Default</th><th>Extra</th></tr>";
    while($row = $result->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $row["Field"] . "</td>";
        echo "<td>" . $row["Type"] . "</td>";
        echo "<td>" . $row["Null"] . "</td>";
        echo "<td>" . $row["Key"] . "</td>";
        echo "<td>" . $row["Default"] . "</td>";
        echo "<td>" . $row["Extra"] . "</td>";
        echo "</tr>";
    }
    echo "</table>";
}

// Count existing users
$result = $conn->query("SELECT COUNT(*) as count FROM users");
$row = $result->fetch_assoc();
echo "<h3>Current Users Count: " . $row['count'] . "</h3>";

// Show existing users (without passwords)
echo "<h3>Existing Users:</h3>";
$result = $conn->query("SELECT id, username, created_at, last_login, is_active FROM users");
if ($result->num_rows > 0) {
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Username</th><th>Created At</th><th>Last Login</th><th>Active</th></tr>";
    while($row = $result->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $row["id"] . "</td>";
        echo "<td>" . $row["username"] . "</td>";
        echo "<td>" . $row["created_at"] . "</td>";
        echo "<td>" . $row["last_login"] . "</td>";
        echo "<td>" . ($row["is_active"] ? "Yes" : "No") . "</td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "<p>No users found</p>";
}

$conn->close();
?>
