<?php
include 'db_connect.php';
session_start();

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"];
    $password = $_POST["password"];

    // Server-side password validation
    if (!preg_match('/^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/', $password)) {
        header("Location: create_account.html?error=Password does not meet complexity requirements.");
        exit();
    }

    $password_hashed = password_hash($password, PASSWORD_DEFAULT);

    $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
    $stmt->bind_param("ss", $username, $password_hashed);

    if ($stmt->execute()) {
        // Registration success, redirect to login page with success message
        header("Location: login.html?success=1");
        exit();
    } else {
        header("Location: create_account.html?error=Username already taken");
        exit();
    }
}
?>
