<?php
include 'db_connect.php';

// Configure session for longer duration
ini_set('session.gc_maxlifetime', 86400); // 24 hours
ini_set('session.cookie_lifetime', 86400); // 24 hours
session_set_cookie_params([
    'lifetime' => 86400, // 24 hours
    'path' => '/',
    'domain' => '',
    'secure' => false,
    'httponly' => true,
    'samesite' => 'Lax'
]);

session_start();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST["username"]);
    $password = $_POST["password"];
    
    // Validate input
    if (empty($username) || empty($password)) {
        $conn->close();
        header("Location: login.html?error=Please fill in all fields");
        exit();
    }
    
    // Prepare and execute query
    $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows === 1) {
        $user = $result->fetch_assoc();
        
        // Verify password
        if (password_verify($password, $user['password'])) {
            // Login successful
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['authenticated'] = true;
            $_SESSION['login_time'] = time();
            $_SESSION['last_activity'] = time();
            
            $stmt->close();
            $conn->close();
            
            // Redirect to main page
            header("Location: main_page.php");
            exit();
        }
    }
    
    // If we reach here, login failed
    $stmt->close();
    $conn->close();
    header("Location: login.html?error=Invalid username or password");
    exit();
    
} else {
    // Not a POST request, redirect to login page
    $conn->close();
    header("Location: login.html");
    exit();
}
?>
