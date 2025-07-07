<?php
/**
 * Test script for subscription system
 * This script tests the subscription functionality
 */

require_once 'db_connect.php';
require_once 'subscription_manager.php';

$subscriptionManager = new SubscriptionManager($conn);

echo "<h2>Subscription System Test</h2>";

// Test user ID (you may need to change this to an actual user ID from your database)
$test_user_id = 1;

echo "<h3>Test User ID: $test_user_id</h3>";

// Get current subscription info
$subscription_info = $subscriptionManager->getUserSubscription($test_user_id);
echo "<h4>Current Subscription Info:</h4>";
echo "<pre>" . print_r($subscription_info, true) . "</pre>";

// Check scan permission
$permission = $subscriptionManager->checkScanPermission($test_user_id);
echo "<h4>Scan Permission Check:</h4>";
echo "<pre>" . print_r($permission, true) . "</pre>";

// Display subscription badge
echo "<h4>Subscription Badge:</h4>";
echo $subscriptionManager->getSubscriptionBadge($subscription_info['subscription']);

// Display scans remaining message
echo "<h4>Scans Remaining Message:</h4>";
echo $subscriptionManager->getScansRemainingMessage($test_user_id);

echo "<hr>";
echo "<h3>Test Actions:</h3>";

// Test upgrade (only if free)
if ($subscription_info['subscription'] === 'free') {
    echo "<p><strong>User is FREE - Testing upgrade...</strong></p>";
    $upgrade_result = $subscriptionManager->upgradeToPremium($test_user_id);
    if ($upgrade_result) {
        echo "<p style='color: green;'>✅ Upgrade successful!</p>";
        
        // Check subscription after upgrade
        $new_subscription = $subscriptionManager->getUserSubscription($test_user_id);
        echo "<h4>After Upgrade:</h4>";
        echo "<pre>" . print_r($new_subscription, true) . "</pre>";
        echo $subscriptionManager->getSubscriptionBadge($new_subscription['subscription']);
    } else {
        echo "<p style='color: red;'>❌ Upgrade failed!</p>";
    }
} else {
    echo "<p><strong>User is already PREMIUM</strong></p>";
    
    // Test downgrade to free for testing
    echo "<p>Testing downgrade to free for testing purposes...</p>";
    $stmt = $conn->prepare("UPDATE users SET subscription = 'free', daily_scan_count = 0 WHERE id = ?");
    $stmt->bind_param("i", $test_user_id);
    if ($stmt->execute()) {
        echo "<p style='color: green;'>✅ Downgraded to free for testing</p>";
        
        // Show updated info
        $updated_subscription = $subscriptionManager->getUserSubscription($test_user_id);
        echo "<h4>After Downgrade (for testing):</h4>";
        echo "<pre>" . print_r($updated_subscription, true) . "</pre>";
        echo $subscriptionManager->getSubscriptionBadge($updated_subscription['subscription']);
    }
}

echo "<hr>";
echo "<h3>Test Scan Limit (Free Users):</h3>";

// Ensure user is free for this test
$stmt = $conn->prepare("UPDATE users SET subscription = 'free', daily_scan_count = 0, last_scan_date = CURDATE() WHERE id = ?");
$stmt->bind_param("i", $test_user_id);
$stmt->execute();

for ($i = 1; $i <= 5; $i++) {
    echo "<p><strong>Scan attempt #$i:</strong></p>";
    
    $permission = $subscriptionManager->checkScanPermission($test_user_id);
    echo "<p>Permission: " . ($permission['allowed'] ? '✅ Allowed' : '❌ Denied') . "</p>";
    echo "<p>Message: " . $permission['message'] . "</p>";
    echo "<p>Scans left: " . $permission['scans_left'] . "</p>";
    
    if ($permission['allowed']) {
        $increment_result = $subscriptionManager->incrementScanCount($test_user_id);
        echo "<p>Scan count incremented: " . ($increment_result ? '✅ Yes' : '❌ No') . "</p>";
    }
    
    echo "<hr>";
}

echo "<h3>Summary</h3>";
echo "<p>✅ Subscription system test completed!</p>";
echo "<p>🔄 <a href='test_subscription.php'>Run test again</a></p>";
echo "<p>🏠 <a href='main_page.php'>Back to main page</a></p>";
?>
