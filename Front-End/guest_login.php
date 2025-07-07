<?php
// Configure session for longer duration and better persistence
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
    $guest_id = $_POST['guest_id'] ?? 'guest_' . time() . '_' . uniqid();
    
    // Set guest session variables
    $_SESSION['guest_id'] = $guest_id;
    $_SESSION['username'] = 'Guest User';
    $_SESSION['is_guest'] = true;
    $_SESSION['user_id'] = 'guest';
    $_SESSION['authenticated'] = true;
    $_SESSION['login_time'] = time();
    $_SESSION['last_activity'] = time();
    
    // Store guest session in localStorage via JavaScript
    echo "<!DOCTYPE html>
    <html>
    <head>
        <title>Setting up Guest Session...</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .loading { color: #0a3d62; font-size: 18px; }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #0a3d62; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class=\"spinner\"></div>
        <div class=\"loading\">Setting up your guest session...</div>
        <script>
            // Store guest session data in localStorage for persistence
            const guestData = {
                guest_id: '" . htmlspecialchars($guest_id) . "',
                username: 'Guest User',
                is_guest: true,
                login_time: " . time() . ",
                last_activity: " . time() . "
            };
            localStorage.setItem('clicksafe_guest_session', JSON.stringify(guestData));
            localStorage.setItem('clicksafe_session_active', 'true');
            
            // Redirect to main page
            setTimeout(function() {
                window.location.href = 'main_page.php?guest=1';
            }, 1000);
        </script>
    </body>
    </html>";
    exit();
}

// If GET request, redirect to login
if ($_SERVER["REQUEST_METHOD"] == "GET") {
    header("Location: login.html");
    exit();
}
?>
