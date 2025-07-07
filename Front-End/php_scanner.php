<?php
session_start();
require_once 'db_connect.php';
require_once 'subscription_manager.php';

// Check if user is authenticated (either regular user or guest)
if (!isset($_SESSION['username']) && !isset($_SESSION['is_guest'])) {
    header("Location: login.html");
    exit();
}

// Handle guest vs regular user
$is_guest = isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true;
$user_id = $is_guest ? null : $_SESSION['user_id'];

// Initialize subscription manager for regular users
$subscriptionManager = null;
if (!$is_guest) {
    $subscriptionManager = new SubscriptionManager($conn);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Check subscription limits for regular users before scanning
    if (!$is_guest && $subscriptionManager) {
        $permission = $subscriptionManager->checkScanPermission($user_id);
        if (!$permission['allowed']) {
            header('Content-Type: application/json');
            http_response_code(429); // Too Many Requests
            echo json_encode([
                'success' => false,
                'error' => 'scan_limit_exceeded',
                'message' => $permission['message'],
                'subscription' => $permission['subscription']
            ]);
            exit();
        }
    }
    
    $scan_type = $_POST['scan_type'] ?? '';
    $scan_value = '';
    $result = '';
    
    if ($scan_type == 'url') {
        $scan_value = $_POST['url'] ?? '';
        // Simple URL scanning simulation
        $result = simulateURLScan($scan_value);
    } elseif ($scan_type == 'file') {
        if (isset($_FILES['file']) && $_FILES['file']['error'] == 0) {
            $scan_value = $_FILES['file']['name'];
            // Simple file scanning simulation
            $result = simulateFileScan($_FILES['file']);
        }
    }
    
    // Increment scan count for regular users after successful scan
    if (!$is_guest && $subscriptionManager && !empty($result)) {
        $scan_recorded = $subscriptionManager->incrementScanCount($user_id);
        if (!$scan_recorded) {
            error_log("Failed to increment scan count for user $user_id");
        }
    }
    
    // Store result in session for scan_results.html
    $_SESSION['last_scan_result'] = $result;
    $_SESSION['last_scan_type'] = $scan_type;
    $_SESSION['last_scan_value'] = $scan_value;
    
    // Return JSON response
    header('Content-Type: application/json');
    echo json_encode(['result' => $result, 'success' => true]);
    exit();
}

function simulateURLScan($url) {
    // Simple URL validation and mock scanning
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return "Invalid URL format";
    }
    
    // Mock scanning result
    $safe_domains = ['google.com', 'github.com', 'stackoverflow.com', 'microsoft.com'];
    $domain = parse_url($url, PHP_URL_HOST);
    
    foreach ($safe_domains as $safe_domain) {
        if (strpos($domain, $safe_domain) !== false) {
            return "✅ SAFE - This URL appears to be legitimate and safe to visit.";
        }
    }
    
    return "⚠️ CAUTION - This URL requires further verification. Please verify before clicking.";
}

function simulateFileScan($file) {
    $filename = $file['name'];
    $size = $file['size'];
    
    // Simple file analysis
    $extension = pathinfo($filename, PATHINFO_EXTENSION);
    $safe_extensions = ['txt', 'pdf', 'jpg', 'png', 'gif', 'docx', 'xlsx'];
    
    if (in_array(strtolower($extension), $safe_extensions)) {
        return "✅ SAFE - File appears to be safe. No threats detected in '$filename' ($size bytes).";
    } else {
        return "⚠️ CAUTION - File type '$extension' requires careful review. Please verify before opening '$filename'.";
    }
}
?>
