<?php
session_start();

// Check if it's a guest session
$is_guest = isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true;

// Destroy the session
session_destroy();

// For guest sessions, show a page that clears localStorage
if ($is_guest) {
    echo "<!DOCTYPE html>
    <html>
    <head>
        <title>Logging out...</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f8f9fa; }
            .loading { color: #0a2342; font-size: 18px; margin-top: 20px; }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #1877f2; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class=\"spinner\"></div>
        <div class=\"loading\">Logging out...</div>
        <script>
            // Clear guest session data from localStorage
            localStorage.removeItem('clicksafe_guest_session');
            localStorage.removeItem('clicksafe_session_active');
            localStorage.removeItem('result');
            
            // Redirect to index page
            setTimeout(function() {
                window.location.href = 'index.html';
            }, 1500);
        </script>
    </body>
    </html>";
} else {
    // For regular users, redirect directly to index.html
    header("Location: index.html");
    exit();
}
?>
