<?php
/**
 * Subscription Management Helper
 * Handles subscription logic, scan limits, and upgrades
 */

require_once 'db_connect.php';

class SubscriptionManager {
    private $conn;
    
    public function __construct($connection) {
        $this->conn = $connection;
    }
    
    /**
     * Get user subscription information
     * @param int $user_id
     * @return array User subscription data
     */
    public function getUserSubscription($user_id) {
        $stmt = $this->conn->prepare("SELECT subscription, daily_scan_count, last_scan_date FROM users WHERE id = ?");
        $stmt->bind_param("i", $user_id);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows === 1) {
            return $result->fetch_assoc();
        }
        
        // Default values if user not found
        return [
            'subscription' => 'free',
            'daily_scan_count' => 0,
            'last_scan_date' => null
        ];
    }
    
    /**
     * Check if user can perform a scan
     * @param int $user_id
     * @return array ['allowed' => bool, 'message' => string, 'scans_left' => int]
     */
    public function checkScanPermission($user_id) {
        $user_data = $this->getUserSubscription($user_id);
        
        // Premium users have unlimited scans
        if ($user_data['subscription'] === 'premium') {
            return [
                'allowed' => true,
                'message' => 'Premium user - unlimited scans',
                'scans_left' => -1, // -1 indicates unlimited
                'subscription' => 'premium'
            ];
        }
        
        // Free users have daily limits
        $today = date('Y-m-d');
        $daily_limit = 3;
        
        // Check if it's a new day - reset count if needed
        if ($user_data['last_scan_date'] !== $today) {
            $this->resetDailyScanCount($user_id, $today);
            $user_data['daily_scan_count'] = 0;
        }
        
        $scans_left = $daily_limit - $user_data['daily_scan_count'];
        
        if ($user_data['daily_scan_count'] >= $daily_limit) {
            return [
                'allowed' => false,
                'message' => 'Daily scan limit reached (3/3). Upgrade to Premium for unlimited scans!',
                'scans_left' => 0,
                'subscription' => 'free'
            ];
        }
        
        return [
            'allowed' => true,
            'message' => "Scan allowed. You have $scans_left scans left today.",
            'scans_left' => $scans_left,
            'subscription' => 'free'
        ];
    }
    
    /**
     * Increment user's daily scan count
     * @param int $user_id
     * @return bool Success status
     */
    public function incrementScanCount($user_id) {
        $today = date('Y-m-d');
        
        // Update scan count and last scan date
        $stmt = $this->conn->prepare("UPDATE users SET daily_scan_count = daily_scan_count + 1, last_scan_date = ? WHERE id = ?");
        $stmt->bind_param("si", $today, $user_id);
        $result = $stmt->execute();
        
        return $result;
    }
    
    /**
     * Reset daily scan count for new day
     * @param int $user_id
     * @param string $date
     * @return bool Success status
     */
    private function resetDailyScanCount($user_id, $date) {
        $stmt = $this->conn->prepare("UPDATE users SET daily_scan_count = 0, last_scan_date = ? WHERE id = ?");
        $stmt->bind_param("si", $date, $user_id);
        return $stmt->execute();
    }
    
    /**
     * Upgrade user to premium subscription
     * @param int $user_id
     * @return bool Success status
     */
    public function upgradeToPremium($user_id) {
        $stmt = $this->conn->prepare("UPDATE users SET subscription = 'premium' WHERE id = ?");
        $stmt->bind_param("i", $user_id);
        $result = $stmt->execute();
        
        if ($result) {
            // Log the upgrade
            error_log("User ID $user_id upgraded to premium subscription at " . date('Y-m-d H:i:s'));
        }
        
        return $result;
    }
    
    /**
     * Get subscription badge HTML
     * @param string $subscription_type
     * @return string HTML badge
     */
    public function getSubscriptionBadge($subscription_type) {
        if ($subscription_type === 'premium') {
            return '<span class="badge subscription-badge premium-badge">
                        <i class="bi bi-gem me-1"></i>Premium
                    </span>';
        } else {
            return '<span class="badge subscription-badge free-badge">
                        <i class="bi bi-person me-1"></i>Free
                    </span>';
        }
    }
    
    /**
     * Get scans remaining message for dashboard
     * @param int $user_id
     * @return string HTML message
     */
    public function getScansRemainingMessage($user_id) {
        $permission = $this->checkScanPermission($user_id);
        
        if ($permission['subscription'] === 'premium') {
            return '<div class="scans-remaining premium">
                        <i class="bi bi-infinity me-2"></i>
                        <strong>Unlimited scans available</strong>
                    </div>';
        } else {
            $scans_left = $permission['scans_left'];
            $icon = $scans_left > 1 ? 'bi-check-circle' : ($scans_left === 1 ? 'bi-exclamation-triangle' : 'bi-x-circle');
            $class = $scans_left > 1 ? 'good' : ($scans_left === 1 ? 'warning' : 'danger');
            
            return "<div class=\"scans-remaining free $class\">
                        <i class=\"bi $icon me-2\"></i>
                        <strong>$scans_left scans remaining today</strong>
                        " . ($scans_left === 0 ? '<small class=\"d-block\">Upgrade to Premium for unlimited scans!</small>' : '') . "
                    </div>";
        }
    }
}

// Initialize global subscription manager
$subscriptionManager = new SubscriptionManager($conn);
?>
