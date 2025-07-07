<?php
$servername = "localhost";
$username = "root"; 
$password = ""; // Your MySQL password (empty for XAMPP default)
$database = "clicksafedb"; // Your database name (lowercase to match existing database)

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
