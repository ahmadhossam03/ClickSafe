<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription System Test - ClickSafe</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">
                            <i class="bi bi-gem me-2 text-warning"></i>
                            Subscription System Test
                        </h5>
                    </div>
                    <div class="card-body">
                        <?php
                        session_start();
                        
                        // Check if user is logged in
                        if (!isset($_SESSION['username']) || isset($_SESSION['is_guest'])) {
                            echo '<div class="alert alert-warning">
                                    <i class="bi bi-exclamation-triangle me-2"></i>
                                    Please log in with a regular user account to test the subscription system.
                                    <br><a href="login.html" class="btn btn-primary btn-sm mt-2">Login</a>
                                  </div>';
                            exit;
                        }
                        
                        require_once 'db_connect.php';
                        require_once 'subscription_manager.php';
                        
                        $user_id = $_SESSION['user_id'];
                        $username = $_SESSION['username'];
                        $subscription_manager = new SubscriptionManager($conn);
                        
                        // Get current subscription info
                        $subscription_info = $subscription_manager->checkScanPermission($user_id);
                        $user_data = $subscription_manager->getUserSubscription($user_id);
                        
                        echo '<div class="row mb-4">
                                <div class="col-md-6">
                                    <h6>User Information:</h6>
                                    <p><strong>Username:</strong> ' . htmlspecialchars($username) . '</p>
                                    <p><strong>User ID:</strong> ' . $user_id . '</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Subscription Status:</h6>
                                    ' . $subscription_manager->getSubscriptionBadge($user_data['subscription']) . '
                                </div>
                              </div>';
                        
                        echo '<div class="row mb-4">
                                <div class="col-12">
                                    ' . $subscription_manager->getScansRemainingMessage($user_id) . '
                                </div>
                              </div>';
                        
                        // Show upgrade button if free user
                        if ($user_data['subscription'] === 'free') {
                            echo '<div class="row mb-4">
                                    <div class="col-12">
                                        <button class="btn btn-warning btn-lg" onclick="testUpgrade()">
                                            <i class="bi bi-gem me-2"></i>Test Premium Upgrade
                                        </button>
                                    </div>
                                  </div>';
                        }
                        
                        // Test scan permission
                        echo '<div class="row mb-4">
                                <div class="col-12">
                                    <h6>Test Scan Permission:</h6>
                                    <button class="btn btn-primary" onclick="testScanPermission()">
                                        <i class="bi bi-shield-check me-2"></i>Test Scan Permission
                                    </button>
                                    <div id="scanTestResult" class="mt-3"></div>
                                </div>
                              </div>';
                        
                        // Show raw data for debugging
                        echo '<div class="row">
                                <div class="col-12">
                                    <h6>Debug Information:</h6>
                                    <div class="bg-light p-3 rounded">
                                        <small>
                                            <strong>Subscription:</strong> ' . $user_data['subscription'] . '<br>
                                            <strong>Daily Scan Count:</strong> ' . $user_data['daily_scan_count'] . '<br>
                                            <strong>Last Scan Date:</strong> ' . ($user_data['last_scan_date'] ?: 'Never') . '<br>
                                            <strong>Scans Left:</strong> ' . $subscription_info['scans_left'] . '<br>
                                            <strong>Permission Allowed:</strong> ' . ($subscription_info['allowed'] ? 'Yes' : 'No') . '
                                        </small>
                                    </div>
                                </div>
                              </div>';
                        ?>
                        
                        <div class="row mt-4">
                            <div class="col-12">
                                <a href="main_page.php" class="btn btn-secondary">
                                    <i class="bi bi-arrow-left me-2"></i>Back to Main Page
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function testUpgrade() {
            try {
                const response = await fetch('api/subscription_upgrade.php', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('✅ ' + data.message);
                    location.reload(); // Reload to show updated status
                } else {
                    alert('❌ ' + data.message);
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            }
        }
        
        async function testScanPermission() {
            const resultDiv = document.getElementById('scanTestResult');
            resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>Testing...';
            
            try {
                const response = await fetch('api/check_scan_permission.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'user_id=<?php echo $user_id; ?>'
                });
                
                const data = await response.json();
                
                let alertClass = data.allowed ? 'alert-success' : 'alert-danger';
                let icon = data.allowed ? 'bi-check-circle' : 'bi-x-circle';
                
                resultDiv.innerHTML = `
                    <div class="alert ${alertClass}">
                        <i class="bi ${icon} me-2"></i>
                        <strong>Result:</strong> ${data.message}<br>
                        <small>
                            <strong>Subscription:</strong> ${data.subscription}<br>
                            <strong>Scans Left:</strong> ${data.scans_left || 'Unlimited'}
                        </small>
                    </div>
                `;
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <strong>Error:</strong> ${error.message}
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
