<!DOCTYPE html>
<html>
<head>
    <title>Database & Registration Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        form { margin: 10px 0; }
        input, button { margin: 5px; padding: 8px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>ClickSafe Database & Registration Test</h1>
    
    <div class="test-section">
        <h2>1. Database Connection Status</h2>
        <?php
        include 'db_connect.php';
        
        if ($conn->connect_error) {
            echo "<p class='error'>❌ Connection failed: " . $conn->connect_error . "</p>";
        } else {
            echo "<p class='success'>✅ Database connection successful!</p>";
            echo "<p>Server: " . $conn->server_info . "</p>";
            
            $result = $conn->query("SELECT DATABASE()");
            $row = $result->fetch_array();
            echo "<p>Database: " . $row[0] . "</p>";
        }
        ?>
    </div>
    
    <div class="test-section">
        <h2>2. Test User Registration</h2>
        <form action="register.php" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password (min 8 chars, 1 number, 1 special)" required>
            <button type="submit">Register Test User</button>
        </form>
        <p><small>Password requirements: At least 8 characters, 1 number, 1 special character</small></p>
    </div>
    
    <div class="test-section">
        <h2>3. Current Users in Database</h2>
        <?php
        if (!$conn->connect_error) {
            $result = $conn->query("SELECT id, username, created_at, is_active FROM users ORDER BY created_at DESC");
            
            if ($result->num_rows > 0) {
                echo "<table>";
                echo "<tr><th>ID</th><th>Username</th><th>Created At</th><th>Active</th></tr>";
                while($row = $result->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . $row["id"] . "</td>";
                    echo "<td>" . $row["username"] . "</td>";
                    echo "<td>" . $row["created_at"] . "</td>";
                    echo "<td>" . ($row["is_active"] ? "Yes" : "No") . "</td>";
                    echo "</tr>";
                }
                echo "</table>";
                echo "<p>Total users: " . $result->num_rows . "</p>";
            } else {
                echo "<p>No users found in database</p>";
            }
        }
        ?>
    </div>
    
    <div class="test-section">
        <h2>4. Quick Links</h2>
        <a href="create_account.html">Go to Create Account Page</a> | 
        <a href="login.html">Go to Login Page</a> | 
        <a href="index.html">Go to Homepage</a>
    </div>
    
    <div class="test-section">
        <h2>5. URL Parameters</h2>
        <?php
        if (isset($_GET['success'])) {
            echo "<p class='success'>✅ Registration successful!</p>";
        }
        if (isset($_GET['error'])) {
            echo "<p class='error'>❌ Error: " . htmlspecialchars($_GET['error']) . "</p>";
        }
        ?>
    </div>
</body>
</html>
