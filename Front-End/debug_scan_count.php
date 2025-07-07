<?php
/**
 * Debug script for subscription scan counting issue
 */

require_once 'db_connect.php';
require_once 'subscription_manager.php';

$subscriptionManager = new SubscriptionManager($conn);

echo "<h2>Scan Count Debugging</h2>";

// Get a test user (change this to an actual user ID)
$test_user_id = 1;

echo "<h3>Step-by-step scan count debugging for User ID: $test_user_id</h3>";

// Reset user to clean state for testing
echo "<h4>1. Resetting user to clean state:</h4>";
$stmt = $conn->prepare("UPDATE users SET daily_scan_count = 0, last_scan_date = CURDATE(), subscription = 'free' WHERE id = ?");
$stmt->bind_param("i", $test_user_id);
$stmt->execute();
echo "<p>✅ User reset to 0 scans for today</p>";

// Check initial state
echo "<h4>2. Initial state check:</h4>";
$user_data = $subscriptionManager->getUserSubscription($test_user_id);
echo "<pre>User Data: " . print_r($user_data, true) . "</pre>";

$permission = $subscriptionManager->checkScanPermission($test_user_id);
echo "<pre>Permission Check: " . print_r($permission, true) . "</pre>";

echo "<h4>3. Simulating scan sequence:</h4>";

for ($i = 1; $i <= 4; $i++) {
    echo "<p><strong>--- Scan #$i ---</strong></p>";
    
    // Check permission before scan
    $permission_before = $subscriptionManager->checkScanPermission($test_user_id);
    echo "<p>BEFORE scan: {$permission_before['scans_left']} scans left, {$permission_before['message']}</p>";
    
    if ($permission_before['allowed']) {
        // Simulate successful scan by incrementing count
        $increment_result = $subscriptionManager->incrementScanCount($test_user_id);
        echo "<p>Scan count incremented: " . ($increment_result ? '✅ Yes' : '❌ No') . "</p>";
        
        // Check permission after scan
        $permission_after = $subscriptionManager->checkScanPermission($test_user_id);
        echo "<p>AFTER scan: {$permission_after['scans_left']} scans left, {$permission_after['message']}</p>";
        
        // Get current database state
        $current_data = $subscriptionManager->getUserSubscription($test_user_id);
        echo "<p>Database state: daily_scan_count = {$current_data['daily_scan_count']}</p>";
        
    } else {
        echo "<p>❌ Scan not allowed: {$permission_before['message']}</p>";
    }
    
    echo "<hr>";
}

echo "<h4>4. Expected vs Actual:</h4>";
echo "<p><strong>Expected behavior:</strong></p>";
echo "<ul>";
echo "<li>Start: 0 scans used, 3 scans left</li>";
echo "<li>After 1st scan: 1 scan used, 2 scans left</li>";
echo "<li>After 2nd scan: 2 scans used, 1 scan left</li>";
echo "<li>After 3rd scan: 3 scans used, 0 scans left</li>";
echo "</ul>";

echo "<p>🔄 <a href='debug_scan_count.php'>Run test again</a></p>";
echo "<p>🏠 <a href='main_page.php'>Back to main page</a></p>";
?>
