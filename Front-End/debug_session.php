<?php
session_start();

echo "<h2>Session and User Debug</h2>";

echo "<h3>Session Data:</h3>";
echo "<pre>";
print_r($_SESSION);
echo "</pre>";

if (isset($_SESSION['user_id'])) {
    require_once 'db_connect.php';
    
    $user_id = $_SESSION['user_id'];
    $stmt = $conn->prepare("SELECT id, username, subscription, daily_scan_count, last_scan_date FROM users WHERE id = ?");
    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows === 1) {
        $user_data = $result->fetch_assoc();
        echo "<h3>Database User Data:</h3>";
        echo "<pre>";
        print_r($user_data);
        echo "</pre>";
        
        echo "<h3>Username Analysis:</h3>";
        echo "<p>Session username: '" . ($_SESSION['username'] ?? 'NOT SET') . "'</p>";
        echo "<p>Database username: '" . $user_data['username'] . "'</p>";
        echo "<p>Match: " . (($_SESSION['username'] ?? '') === $user_data['username'] ? '✅ Yes' : '❌ No') . "</p>";
        
    } else {
        echo "<p>❌ User not found in database!</p>";
    }
    
} else {
    echo "<p>❌ No user_id in session!</p>";
}

echo "<p>🏠 <a href='main_page.php'>Back to main page</a></p>";
?>
