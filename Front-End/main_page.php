<?php
// Configure session for longer duration
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

// Update last activity time
if (isset($_SESSION['authenticated'])) {
    $_SESSION['last_activity'] = time();
}

// Check if user is authenticated (either regular user or guest)
if (!isset($_SESSION['username']) && !isset($_SESSION['is_guest'])) {
    // Clear any corrupted session data
    session_destroy();
    header("Location: login.html?error=Please log in to access this page");
    exit();
}

// Handle guest users
$is_guest = isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true;
$username = $is_guest ? 'Guest User' : $_SESSION['username'];
$guest_id = $is_guest ? $_SESSION['guest_id'] : null;

// Include subscription manager for regular users (guests don't have subscriptions)
$subscription_info = null;
if (!$is_guest) {
    require_once 'db_connect.php';
    require_once 'subscription_manager.php';
    $subscription_manager = new SubscriptionManager($conn);
    $user_id = $_SESSION['user_id'];
    
    // Fix username display issue: fetch username from database if session username is 'root'
    if ($username === 'root' || empty($username)) {
        $stmt = $conn->prepare("SELECT username FROM users WHERE id = ?");
        $stmt->bind_param("i", $user_id);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($result->num_rows === 1) {
            $user_data = $result->fetch_assoc();
            $username = $user_data['username'];
            $_SESSION['username'] = $username; // Update session with correct username
        }
        $stmt->close();
    }
    
    $subscription_info = $subscription_manager->checkScanPermission($user_id);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClickSafe</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="icon" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/icons/shield-lock.svg">
    <!-- Roboto font for clean look -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <!-- jsPDF and html2canvas for PDF generation -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        :root {
            --navy: #0a2342;
            --blue: #1877f2;
            --white: #fff;
            --gray: #f8f9fa;
            --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.10);
            --text-primary: #0a2342;
            --text-secondary: #3a4a5d;
            --card-bg: #fff;
            --footer-bg: #0a2342;
            --footer-text: #fff;
        }
        html, body {
            height: 100%;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        body.dark-mode, html.dark-mode, body.dark-mode html, html body.dark-mode {
            background: var(--white) !important;
        }
        body.dark-mode, .dark-mode {
            background: var(--white) !important;
        }
        body.dark-mode, .dark-mode {
            --navy: #e0e0e0;
            --blue: #2196f3;
            --white: #121212;
            --gray: #1e1e1e;
            --shadow: none;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
            --card-bg: #1e1e1e;
            --footer-bg: #181818;
            --footer-text: #e0e0e0;
        }
        body.dark-mode, .dark-mode {
            background: var(--white) !important;
        }
        .navbar {
            background: var(--white) !important;
            box-shadow: 0 2px 8px rgba(10,35,66,0.04);
            padding-top: 0.7rem;
            padding-bottom: 0.7rem;
        }
        .navbar-brand {
            color: var(--navy) !important;
            font-weight: 700;
            font-size: 1.5rem;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
        }
        .nav-link {
            color: var(--navy) !important;
            font-weight: 500;
            margin: 0 0.5rem;
        }
        .nav-link:hover {
            color: var(--blue) !important;
        }
        .logo-icon {
            font-size: 2rem;
            color: var(--blue);
            margin-right: 0.5rem;
        }
        .dark-toggle-btn {
            background: none;
            border: none;
            color: var(--navy);
            font-size: 1.5rem;
            margin-left: 1rem;
            cursor: pointer;
            transition: color 0.2s;
        }
        .dark-mode .dark-toggle-btn {
            color: #ffd600;
        }
        .profile-dropdown .dropdown-toggle {
            background: none;
            border: none;
            color: var(--navy);
            font-size: 1.3rem;
            font-weight: 500;
            display: flex;
            align-items: center;
        }
        .profile-dropdown .dropdown-menu {
            min-width: 8rem;
        }
        
        /* Enhanced Subscription Badges */
        .subscription-badge {
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.4rem 0.8rem;
            border-radius: 0.5rem;
            display: inline-flex;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .premium-badge {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #8B4513;
            border: 2px solid #FFD700;
            animation: premium-glow 2s ease-in-out infinite alternate;
        }
        
        .free-badge {
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            color: #1976D2;
            border: 2px solid #2196F3;
        }
        
        @keyframes premium-glow {
            from { box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3); }
            to { box-shadow: 0 4px 16px rgba(255, 215, 0, 0.6); }
        }
        
        .upgrade-btn {
            margin-top: 1rem;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #8B4513;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 0.8rem;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .upgrade-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5);
            background: linear-gradient(135deg, #FFE55C, #FFB347);
        }
        .main-container {
            flex: 1 0 auto;
            max-width: 1200px;
            margin: 4rem auto 2rem auto;
            width: 90%;
        }
        
        /* Override Bootstrap container constraints */
        .container, .container-fluid, .container-lg, .container-md, .container-sm, .container-xl, .container-xxl {
            max-width: none !important;
        }
        .center-card {
            background: var(--card-bg);
            border-radius: 1.5rem;
            box-shadow: var(--shadow);
            padding: 2.5rem 4rem 2rem 4rem;
            position: relative;
            overflow: hidden;
            color: var(--text-primary);
            width: 100%;
            max-width: none;
            margin: 0;
        }
        .nav-tabs {
            border-bottom: 2px solid #e3e8ee;
        }
        .nav-tabs .nav-link {
            font-weight: 500;
            color: #7a869a;
            border: none;
            border-bottom: 2.5px solid transparent;
            font-size: 1.08rem;
            padding: 0.7rem 1.5rem;
        }
        .nav-tabs .nav-link.active {
            color: var(--blue);
            border-bottom: 2.5px solid var(--blue);
            background: none;
        }
        .tab-content {
            margin-top: 2rem;
        }
        .upload-area {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 180px;
            border-radius: 1rem;
            background: #f4f8ff;
            border: 2.5px dashed #b3c6e6;
            transition: background 0.2s, border-color 0.2s;
            cursor: pointer;
            margin-bottom: 1.2rem;
        }
        .upload-area.dragover {
            background: #e3f0ff;
            border-color: var(--blue);
        }
        body.dark-mode .upload-area {
            background: #23272b;
            border-color: #444c56;
        }
        body.dark-mode .upload-area.dragover {
            background: #2c3136;
            border-color: var(--blue);
        }
        .upload-icon {
            font-size: 3.5rem;
            color: var(--blue);
            margin-bottom: 1rem;
        }
        .choose-btn {
            background: var(--blue);
            color: var(--white);
            font-weight: 600;
            border: none;
            border-radius: 0.7rem;
            padding: 0.7rem 2.2rem;
            font-size: 1.1rem;
            margin-bottom: 0.7rem;
            box-shadow: 0 2px 8px rgba(24,119,242,0.08);
        }
        .choose-btn:hover {
            background: #1456a0;
        }
        .upload-hint {
            font-size: 0.98rem;
            color: #7a869a;
        }
        body.dark-mode .upload-hint {
            color: #b0b0b0;
        }
        .file-preview {
            margin-top: 0.7rem;
            font-size: 1.01rem;
            color: var(--blue);
            word-break: break-all;
        }
        
        /* Scan Type Selection Styles */
        .scan-type-section {
            margin: 2rem 0;
        }
        
        .scan-option {
            position: relative;
            margin-bottom: 1rem;
        }
        
        .scan-radio {
            position: absolute;
            opacity: 0;
            cursor: pointer;
        }
        
        .scan-label {
            display: block;
            background: var(--card-bg);
            border: 2px solid rgba(24, 119, 242, 0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            margin: 0;
        }
        
        .scan-label:hover {
            border-color: var(--blue);
            background: rgba(24, 119, 242, 0.05);
        }
        
        .scan-radio:checked + .scan-label {
            border-color: var(--blue);
            background: rgba(24, 119, 242, 0.1);
            box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.1);
        }
        
        .scan-option-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .scan-icon {
            font-size: 2rem;
            color: var(--blue);
            margin-bottom: 0.5rem;
        }
        
        .scan-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .scan-description {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        /* Result Display Styles */
        .results-content {
            background: var(--card-bg);
            border-radius: 0.75rem;
            padding: 2.5rem 2rem;
            font-family: 'Consolas', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            min-height: 320px;
            font-size: 1.15rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            box-shadow: 0 1px 4px rgba(10,35,66,0.04);
            display: none;
        }
        
        .results-content.show {
            display: block;
        }
        
        .main-title {
            font-size: 1.4rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1.5rem;
            color: white;
            background: rgba(24, 119, 242, 0.85);
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            border: none;
            box-shadow: 0 2px 8px rgba(24, 119, 242, 0.2);
        }
        
        .result-section {
            margin-bottom: 1.5rem;
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(24, 119, 242, 0.2);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(24, 119, 242, 0.1);
            transition: all 0.3s ease;
        }
        
        .result-section:hover {
            box-shadow: 0 4px 12px rgba(24, 119, 242, 0.15);
            border-color: rgba(24, 119, 242, 0.3);
        }
        
        .result-title {
            font-size: 1.2rem;
            font-weight: 600;
            text-align: left;
            margin-bottom: 0.75rem;
            color: var(--blue);
            border-bottom: 1px solid rgba(24, 119, 242, 0.3);
            padding-bottom: 0.5rem;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .toggle-btn {
            background: var(--blue);
            color: white;
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .toggle-btn:hover {
            background: #1456a0;
            transform: scale(1.1);
        }
        
        .section-content {
            display: block;
            transition: all 0.3s ease;
            padding: 0.5rem 0;
        }
        
        .result-text {
            margin-bottom: 0.5rem;
            padding: 0.25rem 0;
            line-height: 1.4;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin: 0.75rem 0;
        }
        
        .stats-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .stats-card.green {
            background: rgba(40, 167, 69, 0.8);
            color: white;
        }
        
        .stats-card.red {
            background: rgba(220, 53, 69, 0.8);
            color: white;
        }
        
        .stats-card.orange {
            background: rgba(255, 193, 7, 0.8);
            color: white;
        }
        
        .stats-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
        }
        
        .stats-title {
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        
        .stats-number {
            font-size: 2.5rem;
            font-weight: bold;
            line-height: 1;
        }
        .url-input-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            max-width: 800px;
            margin: 0 auto;
        }
        .url-input {
            flex: 1;
            border-radius: 1rem 0 0 1rem;
            border: 2px solid #e3e8ee;
            font-size: 1.3rem;
            padding: 1.2rem 1.5rem;
            background: var(--card-bg);
            color: var(--text-primary);
            box-shadow: 0 2px 8px rgba(24,119,242,0.08);
            height: 60px;
        }
        .scan-btn {
            border-radius: 0 1rem 1rem 0;
            height: 60px;
            font-size: 1.2rem;
            padding: 0 2rem;
        }
        .scan-btn:disabled {
            background: #b3c6e6;
            cursor: not-allowed;
        }
        body.dark-mode .scan-btn:disabled {
            background: #444c56;
            color: #8b949e;
        }
        .scan-btn:hover:not(:disabled) {
            background: #1456a0;
        }
        .search-placeholder {
            color: #7a869a;
            font-size: 1.05rem;
            text-align: center;
            margin-top: 2rem;
        }
        body.dark-mode .search-placeholder {
            color: #b0b0b0;
        }
        .footer {
            flex-shrink: 0;
            margin-top: 0 !important;
            padding-top: 2rem !important;
            background: var(--footer-bg);
            color: var(--footer-text);
            padding: 2rem 0 1rem 0;
        }
        .footer a, .footer .bi {
            color: var(--blue);
            text-decoration: none;
            margin-right: 0.5rem;
        }
        .footer a:hover {
            color: #fff;
        }
        /* Remove margin-top from .footer if present */
        .footer.mt-5 { margin-top: 0 !important; }
        .footer.pt-4 { padding-top: 2rem !important; }
        @media (max-width: 600px) {
            .main-container {
                margin: 2rem 0.5rem;
            }
            .center-card {
                padding: 1.2rem 0.5rem 1.5rem 0.5rem;
            }
        }
        
        /* Subscription System Styles */
        .subscription-info {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 0.75rem;
            padding: 1rem 1.25rem;
            margin-bottom: 1.5rem;
            border: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        /* PDF Download Button Styles */
        .pdf-download-container {
            text-align: center;
            margin: 1.5rem 0;
            padding: 0.75rem;
            background: rgba(24, 119, 242, 0.05);
            border-radius: 0.5rem;
            border: 1px solid rgba(24, 119, 242, 0.2);
        }
        
        .pdf-download-btn {
            background: var(--blue) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.375rem !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            text-decoration: none !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        .pdf-download-btn:hover {
            background: #0056b3 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
            color: white !important;
        }
        
        .pdf-download-btn:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        .pdf-download-btn:disabled {
            background: #6c757d !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
            color: white !important;
        }
        
        /* Dark mode support for PDF button */
        body.dark-mode .pdf-download-container {
            background: rgba(24, 119, 242, 0.1);
            border-color: rgba(24, 119, 242, 0.3);
        }
        
        body.dark-mode .pdf-download-btn {
            background: var(--blue) !important;
            color: white !important;
        }
        
        body.dark-mode .pdf-download-btn:hover {
            background: #0056b3 !important;
            color: white !important;
        }
        
        body.dark-mode .subscription-info {
            background: linear-gradient(135deg, #2c3136 0%, #23272b 100%);
            border-color: #444c56;
        }
        
        .subscription-badge {
            font-size: 0.875rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            display: inline-flex;
            align-items: center;
            letter-spacing: 0.5px;
        }
        
        .premium-badge {
            background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
            color: #8b4513;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
            border: 1px solid #ffa500;
        }
        
        .free-badge {
            background: #6c757d;
            color: white;
        }
        
        .scans-remaining {
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .scans-remaining.premium {
            color: #198754;
            font-weight: 500;
        }
        
        .scans-remaining.free.good {
            color: #198754;
        }
        
        .scans-remaining.free.warning {
            color: #fd7e14;
        }
        
        .scans-remaining.free.danger {
            color: #dc3545;
        }
        
        .upgrade-btn {
            background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
            border: 1px solid #ffa500;
            color: #8b4513;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
            border-radius: 50px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
        }
        
        .upgrade-btn:hover {
            background: linear-gradient(135deg, #ffb347 0%, #ffa500 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
            color: #8b4513;
        }
        
        .upgrade-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        @media (max-width: 768px) {
            .subscription-info {
                flex-direction: column;
                text-align: center;
            }
        }
        
        /* Email Search Styles */
        .email-search-container {
            max-width: 100%;
            margin: 0 auto;
        }
        
        .email-input-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .email-input {
            flex: 1;
            border-radius: 1rem 0 0 1rem;
            border: 2px solid #e3e8ee;
            font-size: 1.1rem;
            padding: 1rem 1.5rem;
            background: var(--card-bg);
            color: var(--text-primary);
            box-shadow: 0 2px 8px rgba(24,119,242,0.08);
            height: 55px;
        }
        
        .email-input:focus {
            border-color: var(--blue);
            outline: none;
            box-shadow: 0 2px 12px rgba(24,119,242,0.15);
        }
        
        body.dark-mode .email-input {
            background: #2c3136;
            border-color: #444c56;
            color: #e0e0e0;
        }
        
        body.dark-mode .email-input:focus {
            border-color: var(--blue);
        }
        
        .email-results-container {
            min-height: 100px;
        }
        
        .breach-result {
            background: var(--card-bg);
            border: 1px solid #dee2e6;
            border-radius: 0.75rem;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        body.dark-mode .breach-result {
            background: #2c3136;
            border-color: #444c56;
        }
        
        .breach-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .breach-logo {
            width: 32px;
            height: 32px;
            border-radius: 0.375rem;
            margin-right: 0.75rem;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        
        .breach-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        
        .breach-date {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-left: auto;
        }
        
        .breach-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }
        
        .breach-data-classes {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .data-class-tag {
            background: #e3f0ff;
            color: #1456a0;
            padding: 0.25rem 0.75rem;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        body.dark-mode .data-class-tag {
            background: #2c3e50;
            color: #74b9ff;
        }
        
        .clean-result {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 1px solid #c3e6cb;
            border-radius: 1rem;
            color: #155724;
        }
        
        body.dark-mode .clean-result {
            background: linear-gradient(135deg, #1e3a28 0%, #2d5a3d 100%);
            border-color: #2d5a3d;
            color: #a6d4a6;
        }
        
        .clean-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #28a745;
        }
        
        body.dark-mode .clean-icon {
            color: #a6d4a6;
        }
        
        .pwned-result {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 1px solid #f5c6cb;
            border-radius: 1rem;
            color: #721c24;
            margin-bottom: 1.5rem;
        }
        
        body.dark-mode .pwned-result {
            background: linear-gradient(135deg, #3d1a1a 0%, #5a2d2d 100%);
            border-color: #5a2d2d;
            color: #ff9999;
        }
        
        .pwned-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #dc3545;
        }
        
        body.dark-mode .pwned-icon {
            color: #ff9999;
        }
        
        .loading-message {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid var(--blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 0.5rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error-message {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 1px solid #f5c6cb;
            border-radius: 1rem;
            color: #721c24;
        }
        
        body.dark-mode .error-message {
            background: linear-gradient(135deg, #3d1a1a 0%, #5a2d2d 100%);
            border-color: #5a2d2d;
            color: #ff9999;
        }
        .scan-no-result {
            font-family: 'Roboto', Arial, sans-serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--text-primary);
            letter-spacing: 0.01em;
            margin: auto;
            display: block;
            text-align: center;
        }
        
        .result-text {
            font-weight: normal;
            line-height: 1.6;
            margin-bottom: 0.3rem;
            color: var(--text-primary);
        }
        
        .status-malicious {
            background-color: #dc3545;
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 0.3rem;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .status-suspicious {
            background-color: #fd7e14;
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 0.3rem;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        /* Stats grid for dynamic analysis summary */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .stats-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.2s ease;
        }
        
        .stats-card:hover {
            transform: translateY(-2px);
        }
        
        .stats-card.red {
            background: rgba(220, 53, 69, 0.15) !important;
            border: 1px solid rgba(220, 53, 69, 0.3);
        }
        
        .stats-card.orange {
            background: rgba(255, 193, 7, 0.15) !important;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }
        
        .stats-card.green {
            background: rgba(40, 167, 69, 0.15) !important;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }
        
        .stats-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stats-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--text-primary);
        }
    </style>
    <script>
        let selectedFile = null;
        let urlValue = '';
        function setActiveTab(tab) {
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.add('active');
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('show', 'active'));
            document.getElementById(tab).classList.add('show', 'active');
        }
        function handleFileInput(e) {
            const files = e.target.files;
            if (files.length > 0) {
                selectedFile = files[0];
                document.getElementById('filePreview').textContent = `File: ${selectedFile.name}`;
                document.getElementById('scanFileBtn').disabled = false;
                // Show scan type selection when file is selected
                document.getElementById('scanTypeSection').style.display = 'block';
            }
        }
        function handleFileDrop(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadArea').classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                selectedFile = files[0];
                document.getElementById('fileInput').value = '';
                document.getElementById('filePreview').textContent = `File: ${selectedFile.name}`;
                document.getElementById('scanFileBtn').disabled = false;
                // Show scan type selection when file is dropped
                document.getElementById('scanTypeSection').style.display = 'block';
            }
        }
        function handleFileDragOver(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadArea').classList.add('dragover');
        }
        function handleFileDragLeave(e) {
            e.preventDefault();
            e.stopPropagation();
            document.getElementById('uploadArea').classList.remove('dragover');
        }
        function chooseFile() {
            document.getElementById('fileInput').click();
        }
        
        // Subscription Management Functions
        async function checkScanPermission() {
            <?php if ($is_guest): ?>
            return { allowed: true, message: 'Guest user - no limits' };
            <?php else: ?>
            try {
                const response = await fetch('api/scan_manager.php?action=check_scan_permission', {
                    method: 'GET'
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                return await response.json();
            } catch (error) {
                console.error('Error checking scan permission:', error);
                return { allowed: false, message: 'Error checking permissions' };
            }
            <?php endif; ?>
        }
        
        async function upgradeToPremium() {
            const upgradeBtn = document.getElementById('upgradeBtn');
            upgradeBtn.disabled = true;
            upgradeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Upgrading...';
            
            try {
                const response = await fetch('api/subscription_upgrade.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'upgrade',
                        user_id: <?php echo $user_id ?? 0; ?>
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show success message
                    showUpgradeSuccess();
                    
                    // Refresh subscription info
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    alert('Upgrade failed: ' + result.message);
                }
            } catch (error) {
                console.error('Error upgrading subscription:', error);
                alert('Error upgrading subscription. Please try again.');
            } finally {
                upgradeBtn.disabled = false;
                upgradeBtn.innerHTML = '<i class="bi bi-gem me-2"></i>Upgrade to Premium';
            }
        }
        
        function showUpgradeSuccess() {
            const subscriptionInfo = document.getElementById('subscriptionInfo');
            if (subscriptionInfo) {
                subscriptionInfo.innerHTML = `
                    <div class="alert alert-success d-flex align-items-center" role="alert">
                        <i class="bi bi-check-circle-fill me-2"></i>
                        <div>
                            <strong>Congratulations!</strong> You've been upgraded to Premium!
                            <br><small>Page will refresh in 2 seconds...</small>
                        </div>
                    </div>
                `;
            }
        }
        
        async function recordScanResults(scanType, target, results) {
            <?php if (!$is_guest): ?>
            try {
                const response = await fetch('api/scan_manager.php?action=add_scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        scan_type: scanType,
                        target: target,
                        scan_results: results
                    })
                });
                
                if (!response.ok) {
                    console.warn('Failed to record scan results');
                    return false;
                }
                
                const result = await response.json();
                if (!result.success && result.error === 'scan_limit_exceeded') {
                    alert(result.message);
                    return false;
                }
                
                // Update subscription display if scan was successful
                if (result.success && result.scans_left !== undefined) {
                    updateSubscriptionDisplay(result.scans_left, result.subscription);
                }
                
                return result.success;
            } catch (error) {
                console.error('Error recording scan results:', error);
                return false;
            }
            <?php else: ?>
            return true; // Guests don't need scan tracking
            <?php endif; ?>
        }
        
        function updateSubscriptionDisplay(scansLeft, subscription) {
            const subscriptionInfo = document.getElementById('subscriptionInfo');
            if (!subscriptionInfo) return;
            
            // Find the scans remaining element and update it
            const scansElement = subscriptionInfo.querySelector('.scans-remaining');
            if (scansElement && subscription === 'free') {
                const icon = scansLeft > 1 ? 'bi-check-circle' : (scansLeft === 1 ? 'bi-exclamation-triangle' : 'bi-x-circle');
                const className = scansLeft > 1 ? 'good' : (scansLeft === 1 ? 'warning' : 'danger');
                
                scansElement.className = `scans-remaining free ${className}`;
                scansElement.innerHTML = `
                    <i class="bi ${icon} me-2"></i>
                    <strong>${scansLeft} scans remaining today</strong>
                    ${scansLeft === 0 ? '<small class="d-block">Upgrade to Premium for unlimited scans!</small>' : ''}
                `;
                
                // Show upgrade button if no scans left
                const upgradeBtn = document.getElementById('upgradeBtn');
                if (upgradeBtn && scansLeft === 0) {
                    upgradeBtn.style.display = 'inline-flex';
                }
            }
        }
        
        async function scanFile() {
            if (!selectedFile) return;
            
            // Check scan permission for regular users
            <?php if (!$is_guest): ?>
            const permission = await checkScanPermission();
            if (!permission.allowed) {
                alert(permission.message);
                return;
            }
            <?php endif; ?>
            
            // Get selected scan type
            const scanType = document.querySelector('input[name="scanType"]:checked').value;
            const resultsContent = document.getElementById('fileResults');
            
            document.getElementById('scanFileBtn').disabled = true;
            const scanTypeText = scanType === 'static' ? 'Static Scanning' : 'Full Scanning';
            document.getElementById('scanFileBtn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + scanTypeText + '...';
            
            // Show results container with loading
            resultsContent.classList.add('show');
            resultsContent.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><div class="mt-3">Analyzing file, please wait...</div></div>';
            
            let formData = new FormData();
            formData.append('file', selectedFile);
            <?php if ($is_guest): ?>
            formData.append('guest_id', '<?php echo htmlspecialchars($guest_id); ?>');
            <?php else: ?>
            formData.append('user_id', '<?php echo $user_id; ?>');
            <?php endif; ?>
            
            try {
                // Choose endpoint based on scan type
                const endpoint = scanType === 'static' ? 
                    'http://127.0.0.1:5000/scanfile_static' : 
                    'http://127.0.0.1:5000/scanfile';
                
                let response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    if (response.status === 429) {
                        alert(errorText);
                        document.getElementById('scanFileBtn').disabled = false;
                        document.getElementById('scanFileBtn').innerHTML = '<i class="bi bi-shield-check me-2"></i>Scan File';
                        return;
                    }
                    throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
                }
                
                let result = await response.text();
                
                // Record scan results for subscription tracking and wait for completion
                const recordingSuccess = await recordScanResults('file', selectedFile.name, result);
                
                // Only proceed if recording was successful (for non-guests)
                <?php if (!$is_guest): ?>
                if (!recordingSuccess) {
                    document.getElementById('scanFileBtn').disabled = false;
                    document.getElementById('scanFileBtn').innerHTML = '<i class="bi bi-shield-check me-2"></i>Scan File';
                    return;
                }
                <?php endif; ?>
                
                // Display formatted results
                displayFormattedResults(result, scanType);
                
            } catch (error) {
                // Fallback to PHP scanner
                console.log('Flask API not available, using PHP fallback');
                try {
                    let phpFormData = new FormData();
                    phpFormData.append('file', selectedFile);
                    phpFormData.append('scan_type', 'file');
                    <?php if ($is_guest): ?>
                    phpFormData.append('guest_id', '<?php echo htmlspecialchars($guest_id); ?>');
                    <?php else: ?>
                    phpFormData.append('user_id', '<?php echo $user_id; ?>');
                    <?php endif; ?>
                    
                    let phpResponse = await fetch('php_scanner.php', {
                        method: 'POST',
                        body: phpFormData
                    });
                    
                    if (!phpResponse.ok) {
                        const errorData = await phpResponse.json();
                        if (errorData.error === 'scan_limit_exceeded') {
                            alert(errorData.message);
                            document.getElementById('scanFileBtn').disabled = false;
                            document.getElementById('scanFileBtn').innerHTML = '<i class="bi bi-shield-check me-2"></i>Scan File';
                            return;
                        }
                        throw new Error(errorData.message || 'PHP scanner error');
                    }
                    
                    let phpData = await phpResponse.json();
                    // Redirect to PHP results page since we're using PHP fallback
                    window.location.href = 'scan_results_php.php';
                } catch (phpError) {
                    resultsContent.innerHTML = '<span class="scan-no-result text-danger">Error: ' + phpError.message + '<br><small>Make sure Flask server is running on localhost:5000</small></span>';
                }
            } finally {
                // Reset scan button
                document.getElementById('scanFileBtn').disabled = false;
                document.getElementById('scanFileBtn').innerHTML = '<i class="bi bi-shield-check me-2"></i>Scan File';
            }
        }
        function handleURLInput(e) {
            urlValue = e.target.value.trim();
            document.getElementById('scanUrlBtn').disabled = !urlValue.match(/^https?:\/\//i);
        }
        
        // Email search functionality
        function handleEmailInput(e) {
            const emailValue = e.target.value.trim();
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            document.getElementById('searchEmailBtn').disabled = !emailPattern.test(emailValue);
        }
        
        async function searchEmail() {
            const emailInput = document.getElementById('emailInput');
            const resultsContainer = document.getElementById('emailResultsContainer');
            const searchBtn = document.getElementById('searchEmailBtn');
            const searchBtnText = document.getElementById('search-btn-text');
            const email = emailInput.value.trim();

            if (!email) {
                resultsContainer.innerHTML = '<div class="error-message">Please enter an email address.</div>';
                return;
            }

            // Validate email format
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(email)) {
                resultsContainer.innerHTML = '<div class="error-message">Please enter a valid email address.</div>';
                return;
            }

            // Show loading message
            searchBtn.disabled = true;
            searchBtnText.innerHTML = '<span class="loading-spinner"></span>Searching...';
            resultsContainer.innerHTML = '<div class="loading-message"><div class="loading-spinner"></div>Checking for breaches...</div>';

            try {
                // For demo purposes, we'll use mock data
                // Replace this with actual HIBP API call when you have an API key
                const demoBreaches = {
                    'test@example.com': [
                        {
                            Name: 'Adobe',
                            BreachDate: '2013-10-04',
                            Description: 'In October 2013, 153 million Adobe accounts were breached with each containing an internal ID, username, email, encrypted password and a password hint in plain text.',
                            DataClasses: ['Email addresses', 'Password hints', 'Passwords', 'Usernames']
                        },
                        {
                            Name: 'LinkedIn',
                            BreachDate: '2012-05-05',
                            Description: 'In May 2012, LinkedIn was breached and the passwords of 6.5 million users were stolen.',
                            DataClasses: ['Email addresses', 'Passwords']
                        }
                    ],
                    'demo@clicksafe.com': [
                        {
                            Name: 'MySpace',
                            BreachDate: '2008-06-01',
                            Description: 'In approximately 2008, MySpace suffered a data breach that impacted over 360 million accounts.',
                            DataClasses: ['Email addresses', 'Passwords', 'Usernames']
                        }
                    ]
                };

                // Simulate API delay
                await new Promise(resolve => setTimeout(resolve, 1500));

                if (demoBreaches[email.toLowerCase()]) {
                    // Email found in breaches
                    displayBreaches(demoBreaches[email.toLowerCase()]);
                } else {
                    // Email not found in any breaches
                    displayCleanResult('Good news — no pwnage found!');
                }
            } catch (error) {
                console.error('Error searching email:', error);
                resultsContainer.innerHTML = '<div class="error-message">An error occurred while searching. Please try again.</div>';
            } finally {
                searchBtn.disabled = false;
                searchBtnText.innerHTML = 'Search';
            }
        }

        function displayCleanResult(message) {
            const resultsContainer = document.getElementById('emailResultsContainer');
            resultsContainer.innerHTML = `
                <div class="clean-result">
                    <i class="bi bi-shield-check clean-icon"></i>
                    <h4 style="margin-bottom: 0.5rem; font-weight: 600;">${message}</h4>
                    <p style="margin: 0; opacity: 0.8;">This email address was not found in any known data breaches.</p>
                </div>
            `;
        }

        function displayBreaches(breaches) {
            const resultsContainer = document.getElementById('emailResultsContainer');
            let html = `
                <div class="pwned-result">
                    <i class="bi bi-exclamation-triangle pwned-icon"></i>
                    <h4 style="margin-bottom: 0.5rem; font-weight: 600;">Oh no — pwned!</h4>
                    <p style="margin: 0; opacity: 0.8;">This email address was found in ${breaches.length} data breach${breaches.length > 1 ? 'es' : ''}:</p>
                </div>
            `;

            breaches.forEach(breach => {
                const breachDate = new Date(breach.BreachDate).toLocaleDateString();
                const dataClasses = breach.DataClasses || [];
                
                html += `
                    <div class="breach-result">
                        <div class="breach-header">
                            <div class="breach-logo">
                                <i class="bi bi-building"></i>
                            </div>
                            <h5 class="breach-name">${breach.Name}</h5>
                            <span class="breach-date">${breachDate}</span>
                        </div>
                        <div class="breach-description">${breach.Description}</div>
                        ${dataClasses.length > 0 ? `
                            <div class="breach-data-classes">
                                ${dataClasses.map(dataClass => `<span class="data-class-tag">${dataClass}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });

            resultsContainer.innerHTML = html;
        }
        async function scanURL() {
            if (!urlValue.match(/^https?:\/\//i)) return;
            
            // Check scan permission for regular users
            <?php if (!$is_guest): ?>
            const permission = await checkScanPermission();
            if (!permission.allowed) {
                alert(permission.message);
                return;
            }
            <?php endif; ?>
            
            document.getElementById('scanUrlBtn').disabled = true;
            document.getElementById('scanUrlBtn').innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Scanning...';
            
            try {
                // Record scan results for subscription tracking first
                <?php if (!$is_guest): ?>
                const recordingSuccess = await recordScanResults('url', urlValue, 'URL scan initiated');
                if (!recordingSuccess) {
                    alert('Scan limit exceeded. Please upgrade your subscription.');
                    return;
                }
                <?php endif; ?>

                // Build the URL for the results page with parameters
                let resultsUrl = `url_scan_results.html?url=${encodeURIComponent(urlValue)}`;
                
                <?php if ($is_guest): ?>
                resultsUrl += `&guest_id=${encodeURIComponent('<?php echo htmlspecialchars($guest_id); ?>')}`;
                <?php else: ?>
                resultsUrl += `&user_id=${encodeURIComponent('<?php echo $user_id; ?>')}`;
                <?php endif; ?>

                // Redirect to the results page
                window.location.href = resultsUrl;
                
            } catch (error) {
                console.error('URL scan error:', error);
                alert('Error initiating URL scan: ' + error.message);
            } finally {
                // Reset scan button
                document.getElementById('scanUrlBtn').disabled = false;
                document.getElementById('scanUrlBtn').innerHTML = 'Scan URL';
            }
        }
        // Dark mode toggle logic
        function setDarkMode(enabled) {
            if (enabled) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', '1');
                document.getElementById('darkToggleIcon').className = 'bi bi-sun';
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', '0');
                document.getElementById('darkToggleIcon').className = 'bi bi-moon';
            }
        }
        // Wait for DOM to be ready before assigning event listeners
        document.addEventListener('DOMContentLoaded', function() {
            // Session management for guests
            <?php if ($is_guest): ?>
            // Store/update guest session in localStorage
            const guestData = {
                guest_id: '<?php echo htmlspecialchars($guest_id); ?>',
                username: 'Guest User',
                is_guest: true,
                login_time: <?php echo isset($_SESSION['login_time']) ? $_SESSION['login_time'] : time(); ?>,
                last_activity: <?php echo time(); ?>
            };
            localStorage.setItem('clicksafe_guest_session', JSON.stringify(guestData));
            localStorage.setItem('clicksafe_session_active', 'true');
            
            // Periodic session heartbeat to keep session alive
            setInterval(function() {
                fetch('api/session_heartbeat.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        guest_id: '<?php echo htmlspecialchars($guest_id); ?>',
                        action: 'heartbeat'
                    })
                }).catch(error => console.log('Heartbeat failed:', error));
                
                // Update localStorage
                const currentData = JSON.parse(localStorage.getItem('clicksafe_guest_session') || '{}');
                currentData.last_activity = Math.floor(Date.now() / 1000);
                localStorage.setItem('clicksafe_guest_session', JSON.stringify(currentData));
            }, 300000); // Every 5 minutes
            <?php endif; ?>

            // Handle page visibility changes to maintain session
            document.addEventListener('visibilitychange', function() {
                if (!document.hidden && localStorage.getItem('clicksafe_session_active') === 'true') {
                    // Page became visible, check if session is still valid
                    <?php if ($is_guest): ?>
                    fetch('api/session_heartbeat.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            guest_id: '<?php echo htmlspecialchars($guest_id); ?>',
                            action: 'check'
                        })
                    }).then(response => response.json())
                    .then(data => {
                        if (!data.success) {
                            // Session expired, clear localStorage
                            localStorage.removeItem('clicksafe_guest_session');
                            localStorage.removeItem('clicksafe_session_active');
                        }
                    }).catch(error => console.log('Session check failed:', error));
                    <?php endif; ?>
                }
            });

            // Set dark mode from localStorage
            if (localStorage.getItem('darkMode') === '1') {
                setDarkMode(true);
            } else {
                setDarkMode(false);
            }
            setActiveTab('file');
            // File drag and drop
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.addEventListener('dragover', handleFileDragOver);
            uploadArea.addEventListener('dragleave', handleFileDragLeave);
            uploadArea.addEventListener('drop', handleFileDrop);
            uploadArea.addEventListener('click', chooseFile);
            document.getElementById('fileInput').addEventListener('change', handleFileInput);
            document.getElementById('scanFileBtn').addEventListener('click', scanFile);
            document.getElementById('urlInput').addEventListener('input', handleURLInput);
            document.getElementById('scanUrlBtn').addEventListener('click', scanURL);
            document.getElementById('emailInput').addEventListener('input', handleEmailInput);
            document.getElementById('searchEmailBtn').addEventListener('click', searchEmail);
            document.getElementById('darkToggle').onclick = function() {
                setDarkMode(!document.body.classList.contains('dark-mode'));
            };
            // On page load, check if URL input is valid and enable Scan URL button if so
            const urlInput = document.getElementById('urlInput');
            urlValue = urlInput.value.trim();
            document.getElementById('scanUrlBtn').disabled = !urlValue.match(/^https?:\/\//i);
        });
        
        // Enhanced result display functions from File-Result.php
        function displayFormattedResults(result, scanType = 'full') {
            const resultsContent = document.getElementById('fileResults');
            
            // First split by the dynamic analysis separator
            const mainSections = result.split('====================');
            
            let formattedHTML = '';
            let sectionCount = 0;
            
            // Static Analysis Section (always shown)
            if (mainSections.length >= 1 && mainSections[0].trim()) {
                // Add Static Analysis title
                formattedHTML += '<div class="main-title">Static Analysis</div>';
                
                const staticSections = mainSections[0].split('-------------------------------');
                
                // File Behaviour Card (was previously String Analysis - now displayed first as a card)
                if (staticSections.length >= 4 && staticSections[3].trim()) {
                    const behaviourSection = staticSections[3].trim();
                    
                    // Extract summary text to determine background color
                    let behaviourClass = 'green'; // default
                    const lastLine = behaviourSection.trim().split('\n').pop().toLowerCase();
                    
                    if (lastLine.includes('malicious')) {
                        behaviourClass = 'red';
                    } else if (lastLine.includes('suspicious')) {
                        behaviourClass = 'orange';
                    }
                    
                    // Create the behaviour card
                    formattedHTML += '<div style="margin: 1.5rem 0;">';
                    formattedHTML += `<div class="stats-card ${behaviourClass}" style="max-width: 850px; margin: 0 auto; background: rgba(${behaviourClass === 'red' ? '220, 53, 69' : behaviourClass === 'orange' ? '255, 193, 7' : '40, 167, 69'}, 0.12) !important; border: 1px solid rgba(${behaviourClass === 'red' ? '220, 53, 69' : behaviourClass === 'orange' ? '255, 193, 7' : '40, 167, 69'}, 0.25); border-radius: 12px; padding: 1rem;">`;
                    formattedHTML += '<div class="stats-title" style="font-size: 1.1rem; margin-bottom: 0.75rem; color: var(--text-primary) !important; font-weight: 600;">File Behaviour</div>';
                    
                    // Split the entire behaviour section into all lines first to find the last line
                    const allLines = behaviourSection.split('\n').filter(line => line.trim());
                    let lineIndex = 0;
                    
                    const paragraphs = behaviourSection.split('\n\n');
                    paragraphs.forEach((paragraph, paragraphIndex) => {
                        if (paragraph.trim()) {
                            if (paragraph.trim().startsWith('Summary:')) {
                                const summaryText = paragraph.replace('Summary:', '<strong>Summary:</strong>');
                                const isVeryLastLine = lineIndex === allLines.length - 1;
                                const style = isVeryLastLine ? 
                                    "text-align: left; margin-bottom: 0.4rem; line-height: 1.3; color: var(--text-primary); font-size: 0.95rem; font-weight: bold;" :
                                    "text-align: left; margin-bottom: 0.4rem; line-height: 1.3; color: var(--text-primary); font-size: 0.95rem;";
                                formattedHTML += `<div style="${style}">${summaryText}</div>`;
                                lineIndex++;
                            } else {
                                // Split paragraph into lines
                                const lines = paragraph.split('\n');
                                lines.forEach((line, localLineIndex) => {
                                    if (line.trim()) {
                                        const isVeryLastLine = lineIndex === allLines.length - 1;
                                        const style = isVeryLastLine ? 
                                            "text-align: left; margin-bottom: 0.4rem; line-height: 1.3; color: var(--text-primary); font-size: 0.95rem; font-weight: bold;" :
                                            "text-align: left; margin-bottom: 0.4rem; line-height: 1.3; color: var(--text-primary); font-size: 0.95rem;";
                                        formattedHTML += `<div style="${style}">${line}</div>`;
                                        lineIndex++;
                                    }
                                });
                            }
                        }
                    });
                    
                    formattedHTML += '</div>';
                    formattedHTML += '</div>';
                }
                
                if (staticSections.length >= 1 && staticSections[0].trim()) {
                    // First section - Third-Party Analysis
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">Third-Party Analysis</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const firstSection = staticSections[0].trim();
                    const lines = firstSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Add emoji indicators for Third-Party Analysis
                            if (line.toLowerCase().includes('safe')) {
                                formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">✅</span>';
                            } else if (line.toLowerCase().includes('verdict:') || line.toLowerCase().includes('analysis')) {
                                formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">❌</span>';
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (staticSections.length >= 2 && staticSections[1].trim()) {
                    // Second section - Is It Packed?
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">Is It Packed?</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const secondSection = staticSections[1].trim();
                    const lines = secondSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Add emoji indicators only for lines that contain '!'
                            if (line.includes('!')) {
                                if (line.toLowerCase().includes('is likely packed')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">❌</span>';
                                } else {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">✅</span>';
                                }
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (staticSections.length >= 3 && staticSections[2].trim()) {
                    // New third section - String Analysis (between Is It Packed and File Behaviour)
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">String Analysis</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const stringsSection = staticSections[2].trim();
                    const lines = stringsSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Format strings with blue background for String Analysis
                            if (line.includes(' -> ')) {
                                const parts = line.split(' -> ');
                                if (parts.length === 2) {
                                    const stringPart = parts[0].trim();
                                    const definition = parts[1].trim();
                                    formattedLine = `<span style="background: rgba(24, 119, 242, 0.2); padding: 2px 6px; border-radius: 4px; font-weight: 500;">${stringPart}</span> → ${definition}`;
                                }
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (staticSections.length >= 5 && staticSections[4].trim()) {
                    // Fourth section - File XML Analysis
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">File XML Analysis</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const xmlSection = staticSections[4].trim();
                    const lines = xmlSection.split('\n');
                    
                    lines.forEach((line, index) => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // For the first line, check for Non-Legitimate (red) or Legitimate (green)
                            if (index === 0) {
                                if (line.toLowerCase().includes('non-legitimate')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">❌</span>';
                                } else if (line.toLowerCase().includes('legitimate')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">✅</span>';
                                }
                            } else {
                                // For other lines, use existing logic
                                if (line.toLowerCase().includes('legitimate')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">✅</span>';
                                } else if (line.toLowerCase().includes('non-legitimate')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">❌</span>';
                                } else if (line.toLowerCase().includes('request administration')) {
                                    formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">⚠️</span>';
                                } else if (line.includes('->') || line.toLowerCase().includes('privileges')) {
                                    // For lines that don't match the specific conditions
                                    if (!line.toLowerCase().includes('legitimate') && !line.toLowerCase().includes('request administration')) {
                                        if (line.toLowerCase().includes('privileges')) {
                                            formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">✅</span>';
                                        } else {
                                            formattedLine = line + ' <span style="margin-left: 5px; font-size: 1.1rem;">❌</span>';
                                        }
                                    }
                                }
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
            }
            
            // Dynamic Analysis Section (only for full scans)
            if (scanType === 'full' && mainSections.length >= 2 && mainSections[1].trim()) {
                // Add separator line and Dynamic Analysis title
                formattedHTML += '<div style="border-top: 2px solid var(--blue); margin: 2rem 0 1.5rem 0; padding-top: 1.5rem;">';
                formattedHTML += '<div class="main-title">Dynamic Analysis</div>';
                
                const dynamicSections = mainSections[1].split('-------------------------------');
                
                if (dynamicSections.length >= 1 && dynamicSections[0].trim()) {
                    // First dynamic section - Dynamic Analysis Summary
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">Dynamic Analysis Summary</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const firstDynamicSection = dynamicSections[0].trim();
                    
                    // Check if this contains the stats format
                    if (firstDynamicSection.includes('Malicious Executables/DLLs') && 
                        firstDynamicSection.includes('Malicious IP Addresses') && 
                        firstDynamicSection.includes('Suspicious IP Addresses') && 
                        firstDynamicSection.includes('Dangerous Terms Found')) {
                        
                        // Parse the stats
                        const lines = firstDynamicSection.split('\n');
                        const stats = {};
                        
                        lines.forEach(line => {
                            if (line.includes('Malicious Executables/DLLs:')) {
                                stats.maliciousExec = parseInt(line.split(':')[1].trim()) || 0;
                            } else if (line.includes('Malicious IP Addresses:')) {
                                stats.maliciousIP = parseInt(line.split(':')[1].trim()) || 0;
                            } else if (line.includes('Suspicious IP Addresses:')) {
                                stats.suspiciousIP = parseInt(line.split(':')[1].trim()) || 0;
                            } else if (line.includes('Dangerous Terms Found:')) {
                                stats.dangerousTerms = parseInt(line.split(':')[1].trim()) || 0;
                            }
                        });
                        
                        // Create the stats grid
                        formattedHTML += '<div class="stats-grid">';
                        
                        // Malicious Executables/DLLs
                        const execClass = stats.maliciousExec > 0 ? 'red' : 'green';
                        formattedHTML += `<div class="stats-card ${execClass}">`;
                        formattedHTML += '<div class="stats-title">Malicious Executables/DLLs</div>';
                        formattedHTML += `<div class="stats-number">${stats.maliciousExec}</div>`;
                        formattedHTML += '</div>';
                        
                        // Malicious IP Addresses
                        const maliciousIPClass = stats.maliciousIP > 0 ? 'red' : 'green';
                        formattedHTML += `<div class="stats-card ${maliciousIPClass}">`;
                        formattedHTML += '<div class="stats-title">Malicious IP Addresses</div>';
                        formattedHTML += `<div class="stats-number">${stats.maliciousIP}</div>`;
                        formattedHTML += '</div>';
                        
                        // Suspicious IP Addresses
                        const suspiciousIPClass = stats.suspiciousIP > 0 ? 'orange' : 'green';
                        formattedHTML += `<div class="stats-card ${suspiciousIPClass}">`;
                        formattedHTML += '<div class="stats-title">Suspicious IP Addresses</div>';
                        formattedHTML += `<div class="stats-number">${stats.suspiciousIP}</div>`;
                        formattedHTML += '</div>';
                        
                        // Dangerous Terms Found
                        const dangerousTermsClass = stats.dangerousTerms > 0 ? 'red' : 'green';
                        formattedHTML += `<div class="stats-card ${dangerousTermsClass}">`;
                        formattedHTML += '<div class="stats-title">Dangerous Terms Found</div>';
                        formattedHTML += `<div class="stats-number">${stats.dangerousTerms}</div>`;
                        formattedHTML += '</div>';
                        
                        formattedHTML += '</div>';
                        
                    } else {
                        // Regular text display for non-stats content
                        const lines = firstDynamicSection.split('\n');
                        lines.forEach(line => {
                            if (line.trim()) {
                                let formattedLine = line;
                                formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                            }
                        });
                    }
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (dynamicSections.length >= 2 && dynamicSections[1].trim()) {
                    // Second dynamic section - Files Dropped
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">Files Dropped</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const secondDynamicSection = dynamicSections[1].trim();
                    const lines = secondDynamicSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Transform Files Dropped format and add emoji indicators
                            if (line.includes('Votes : "Malicious"')) {
                                // Extract the vote count after "Malicious"-> 
                                const voteMatch = line.match(/Votes\s*:\s*"Malicious"\s*->\s*(\d+)/i);
                                if (voteMatch) {
                                    const voteCount = parseInt(voteMatch[1]);
                                    if (voteCount > 0) {
                                        // Replace the votes format with malicious indicator
                                        formattedLine = line.replace(/\s*->\s*Votes\s*:\s*"Malicious"\s*->\s*\d+/i, ' -> ❌ Voted ' + voteCount + ' times to be Malicious');
                                    } else {
                                        // Replace with safe indicator
                                        formattedLine = line.replace(/\s*->\s*Votes\s*:\s*"Malicious"\s*->\s*\d+/i, ' -> ✅ Safe');
                                    }
                                }
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (dynamicSections.length >= 3 && dynamicSections[2].trim()) {
                    // Third dynamic section - IP Addresses
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">IP Addresses</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const thirdDynamicSection = dynamicSections[2].trim();
                    const lines = thirdDynamicSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Format IP addresses and replace status with emojis
                            if (line.includes('[Safe]')) {
                                formattedLine = line.replace('[Safe]', '<span style="margin-left: 5px; font-size: 1.1rem;">✅</span>');
                            } else if (line.includes('[Malicious]')) {
                                formattedLine = line.replace('[Malicious]', '<span style="margin-left: 5px; font-size: 1.1rem;">❌</span>');
                            } else if (line.includes('[Suspicious]')) {
                                formattedLine = line.replace('[Suspicious]', '<span style="margin-left: 5px; font-size: 1.1rem;">⚠️</span>');
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                if (dynamicSections.length >= 4 && dynamicSections[3].trim()) {
                    // Fourth dynamic section - Dangerous Terms
                    formattedHTML += '<div class="result-section">';
                    formattedHTML += '<div class="section-header">';
                    formattedHTML += '<div class="result-title">Dangerous Terms</div>';
                    formattedHTML += '<button class="toggle-btn" onclick="toggleSection(' + sectionCount + ')">−</button>';
                    formattedHTML += '</div>';
                    formattedHTML += '<div id="section-content-' + sectionCount + '" class="section-content">';
                    
                    const fourthDynamicSection = dynamicSections[3].trim();
                    const lines = fourthDynamicSection.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim()) {
                            let formattedLine = line;
                            
                            // Add basic formatting for dangerous terms
                            if (line.trim().startsWith('-') && line.length > 1) {
                                formattedLine = line + ' ❌';
                            }
                            
                            formattedHTML += `<div class="result-text">${formattedLine}</div>`;
                        }
                    });
                    
                    formattedHTML += '</div></div>';
                    sectionCount++;
                }
                
                formattedHTML += '</div>'; // Close the dynamic analysis container
            }
            
            // If no sections found, display as is
            if (!formattedHTML) {
                formattedHTML = `<div class="result-text">${result}</div>`;
            }
            
            // Add PDF download button at the end (only if we have real scan results)
            if (formattedHTML && !result.includes('Upload a file and click scan') && !result.includes('Loading') && !result.includes('Error')) {
                formattedHTML += `
                    <div class="pdf-download-container" id="pdfDownloadContainer">
                        <button class="pdf-download-btn btn btn-primary" onclick="downloadReportPDF()">
                            <i class="bi bi-file-earmark-pdf me-2"></i>
                            Download Report PDF
                        </button>
                    </div>
                `;
            }
            
            resultsContent.innerHTML = formattedHTML;
        }
        
        function analyzeThreatLevel(result, scanType) {
            const lowerResult = result.toLowerCase();
            
            // Check for high-risk indicators
            if (lowerResult.includes('malicious') || 
                lowerResult.includes('virus') || 
                lowerResult.includes('trojan') ||
                lowerResult.includes('backdoor') ||
                lowerResult.includes('ransomware')) {
                return 'danger';
            }
            
            // Check for medium-risk indicators
            if (lowerResult.includes('suspicious') || 
                lowerResult.includes('warning') ||
                lowerResult.includes('potential threat') ||
                lowerResult.includes('anomaly')) {
                return 'warning';
            }
            
            // Default to safe
            return 'safe';
        }
        
        // Toggle section visibility
        function toggleSection(sectionId) {
            const content = document.getElementById('section-content-' + sectionId);
            const button = event.target;
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                button.textContent = '−';
            } else {
                content.style.display = 'none';
                button.textContent = '+';
            }
        }
        
        // PDF Download functionality
        function downloadReportPDF() {
            const button = document.querySelector('.pdf-download-btn');
            const originalText = button.innerHTML;
            
            // Disable button and show loading state
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Generating PDF...';
            
            try {
                // Get the file results content
                const resultsContent = document.getElementById('fileResults');
                
                // Create a temporary container for PDF content
                const tempContainer = document.createElement('div');
                tempContainer.style.cssText = `
                    position: absolute; 
                    top: -9999px; 
                    left: -9999px; 
                    width: 800px; 
                    background: white; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    padding: 40px; 
                    color: #333;
                `;
                
                // Get current date and time
                const now = new Date();
                const timestamp = now.getFullYear() + '-' + 
                                String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                                String(now.getDate()).padStart(2, '0') + '_' + 
                                String(now.getHours()).padStart(2, '0') + '-' + 
                                String(now.getMinutes()).padStart(2, '0');
                
                const filename = selectedFile ? 
                    `ClickSafe_Report_${selectedFile.name}_${timestamp}.pdf` : 
                    `ClickSafe_Report_${timestamp}.pdf`;
                
                // Create PDF header
                const header = `
                    <div style="text-align: center; border-bottom: 3px solid #1877f2; padding-bottom: 20px; margin-bottom: 30px;">
                        <h1 style="color: #1877f2; margin: 0; font-size: 2.5em;">🛡️ ClickSafe</h1>
                        <div style="color: #666; font-size: 1.2em; margin-top: 10px;">Security Analysis Report</div>
                        <div style="margin-top: 15px; color: #888; font-size: 1em;">
                            Generated on: ${now.toLocaleString()}<br>
                            ${selectedFile ? `File: ${selectedFile.name}` : ''}
                        </div>
                    </div>
                `;
                
                // Clone the results content and remove the PDF button
                const contentClone = resultsContent.cloneNode(true);
                const pdfButtonInClone = contentClone.querySelector('#pdfDownloadContainer');
                if (pdfButtonInClone) {
                    pdfButtonInClone.remove();
                }
                
                // Remove toggle buttons and ensure all sections are visible
                const toggleButtons = contentClone.querySelectorAll('.toggle-btn');
                toggleButtons.forEach(btn => btn.remove());
                
                const sections = contentClone.querySelectorAll('.section-content');
                sections.forEach(section => {
                    section.style.display = 'block';
                });
                
                // Add footer
                const footer = `
                    <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em;">
                        © 2024 ClickSafe. All rights reserved.<br>
                        This report was generated by ClickSafe security analysis system.
                    </div>
                `;
                
                // Combine all content
                tempContainer.innerHTML = header + contentClone.innerHTML + footer;
                document.body.appendChild(tempContainer);
                
                // Use html2canvas to convert to image, then jsPDF to create PDF
                html2canvas(tempContainer, {
                    scale: 2,
                    useCORS: true,
                    logging: false,
                    allowTaint: true,
                    backgroundColor: '#ffffff'
                }).then(canvas => {
                    // Remove temporary container
                    document.body.removeChild(tempContainer);
                    
                    // Create PDF
                    const { jsPDF } = window.jspdf;
                    const pdf = new jsPDF('p', 'mm', 'a4');
                    
                    const imgData = canvas.toDataURL('image/png');
                    const imgWidth = 210; // A4 width in mm
                    const pageHeight = 295; // A4 height in mm
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    let heightLeft = imgHeight;
                    
                    let position = 0;
                    
                    // Add first page
                    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                    heightLeft -= pageHeight;
                    
                    // Add additional pages if needed
                    while (heightLeft >= 0) {
                        position = heightLeft - imgHeight;
                        pdf.addPage();
                        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                        heightLeft -= pageHeight;
                    }
                    
                    // Download the PDF
                    pdf.save(filename);
                    
                    // Show success message
                    setTimeout(() => {
                        alert('PDF report generated and downloaded successfully!');
                    }, 100);
                    
                }).catch(error => {
                    console.error('Error generating PDF:', error);
                    document.body.removeChild(tempContainer);
                    
                    // Fallback: simple HTML download
                    const fallbackContent = `
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <title>ClickSafe Security Report</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                                .header { text-align: center; border-bottom: 2px solid #1877f2; padding-bottom: 20px; margin-bottom: 30px; }
                                .header h1 { color: #1877f2; margin: 0; }
                                @media print { body { margin: 0; } }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>🛡️ ClickSafe Security Report</h1>
                                <p>Generated on: ${now.toLocaleString()}</p>
                                ${selectedFile ? `<p>File: ${selectedFile.name}</p>` : ''}
                            </div>
                            ${contentClone.innerHTML}
                        </body>
                        </html>
                    `;
                    
                    const blob = new Blob([fallbackContent], { type: 'text/html' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename.replace('.pdf', '.html');
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    
                    alert('PDF generation failed. Downloaded as HTML file instead. You can print it as PDF from your browser.');
                });
                
            } catch (error) {
                console.error('Error generating PDF:', error);
                alert('Error generating PDF report. Please try again.');
            } finally {
                // Re-enable button
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = '<i class="bi bi-file-earmark-pdf me-2"></i>Download Report PDF';
                }, 2000);
            }
        }
    </script>
</head>
<body>
    <!-- User Profile Top Right -->
    <div style="position: absolute; top: 24px; right: 40px; z-index: 1050; display: flex; align-items: center; gap: 0.5rem;">
        <div class="profile-dropdown dropdown">
            <button class="dropdown-toggle d-flex align-items-center" type="button" id="profileDropdown" data-bs-toggle="dropdown" aria-expanded="false" style="background: none; border: none; color: var(--navy); font-size: 1.3rem; font-weight: 500;">
                <i class="bi bi-person-circle me-2" style="font-size:1.7rem;"></i>
                <span class="d-none d-md-inline"> <?php echo htmlspecialchars($username); ?> </span>
                <?php if (!$is_guest && $subscription_info): ?>
                <span class="profile-subscription-badge <?php echo $subscription_info['subscription'] === 'premium' ? 'premium-badge' : 'free-badge'; ?>" style="font-size: 0.7rem; margin-left: 0.5rem; padding: 0.2rem 0.5rem; border-radius: 0.3rem;">
                    <?php if ($subscription_info['subscription'] === 'premium'): ?>
                        <i class="bi bi-gem me-1"></i>PREMIUM
                    <?php else: ?>
                        <i class="bi bi-person me-1"></i>FREE
                    <?php endif; ?>
                </span>
                <?php endif; ?>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
                <?php if (!$is_guest && $subscription_info && $subscription_info['subscription'] === 'free'): ?>
                <li><a class="dropdown-item" href="#" onclick="upgradeToPremium()"><i class="bi bi-gem me-2 text-warning"></i>Upgrade to Premium</a></li>
                <li><hr class="dropdown-divider"></li>
                <?php endif; ?>
                <li><form action="logout.php" method="POST"><button class="dropdown-item text-danger" type="submit"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></form></li>
            </ul>
        </div>
    </div>
    <!-- Header/Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
        <div class="container d-flex align-items-center justify-content-between">
            <a class="navbar-brand d-flex align-items-center" href="index.html">
                <i class="bi bi-shield-lock logo-icon"></i>ClickSafe
            </a>
            <button class="dark-toggle-btn" id="darkToggle" title="Toggle dark mode">
                <i class="bi bi-moon" id="darkToggleIcon"></i>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="main_page.php">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="history.html">History</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="main-container">
        <div class="center-card">
            <?php if (!$is_guest && $subscription_info): ?>
            <!-- Subscription Information -->
            <div class="subscription-info" id="subscriptionInfo">
                <div class="d-flex align-items-center gap-3">
                    <?php echo $subscription_manager->getSubscriptionBadge($subscription_info['subscription']); ?>
                    <?php echo $subscription_manager->getScansRemainingMessage($user_id); ?>
                </div>
                <?php if ($subscription_info['subscription'] === 'free'): ?>
                <button class="upgrade-btn" id="upgradeBtn" onclick="upgradeToPremium()">
                    <i class="bi bi-gem me-2"></i>Upgrade to Premium
                </button>
                <?php endif; ?>
            </div>
            <?php endif; ?>
            
            <!-- Tabs -->
            <ul class="nav nav-tabs justify-content-center mb-3" id="scanTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="file-tab" data-bs-toggle="tab" data-bs-target="#file" type="button" role="tab" aria-controls="file" aria-selected="true" onclick="setActiveTab('file')">FILE</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="url-tab" data-bs-toggle="tab" data-bs-target="#url" type="button" role="tab" aria-controls="url" aria-selected="false" onclick="setActiveTab('url')">URL</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="search-tab" data-bs-toggle="tab" data-bs-target="#search" type="button" role="tab" aria-controls="search" aria-selected="false" onclick="setActiveTab('search')">SEARCH</button>
                </li>
            </ul>
            <div class="tab-content" id="scanTabContent">
                <!-- FILE TAB -->
                <div class="tab-pane fade show active" id="file" role="tabpanel" aria-labelledby="file-tab">
                    <div id="uploadArea" class="upload-area" tabindex="0">
                        <i class="bi bi-cloud-arrow-up upload-icon"></i>
                        <button type="button" class="choose-btn" onclick="chooseFile()">Choose file</button>
                        <input type="file" id="fileInput" class="d-none" />
                        <div class="upload-hint">Or drag and drop a file here</div>
                        <div id="filePreview" class="file-preview"></div>
                    </div>
                    
                    <!-- Scan Type Selection -->
                    <div class="scan-type-section" id="scanTypeSection" style="display: none;">
                        <h5 class="mb-3 text-center">Select Scan Type</h5>
                        <div class="row justify-content-center">
                            <div class="col-md-5">
                                <div class="scan-option">
                                    <input type="radio" class="scan-radio" id="staticScan" name="scanType" value="static" checked>
                                    <label class="scan-label" for="staticScan">
                                        <div class="scan-option-content">
                                            <i class="bi bi-lightning scan-icon"></i>
                                            <div class="scan-title">Static Scan</div>
                                            <div class="scan-description">Quick analysis without execution</div>
                                        </div>
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-5">
                                <div class="scan-option">
                                    <input type="radio" class="scan-radio" id="fullScan" name="scanType" value="full">
                                    <label class="scan-label" for="fullScan">
                                        <div class="scan-option-content">
                                            <i class="bi bi-shield-check scan-icon"></i>
                                            <div class="scan-title">Full Scan</div>
                                            <div class="scan-description">Complete analysis with execution</div>
                                        </div>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button id="scanFileBtn" class="btn btn-primary" type="button" disabled="<?php echo !isset($selectedFile) ? 'disabled' : '' ?>">Scan File</button>
                    </div>
                    
                    <!-- Results Section -->
                    <div class="results-content" id="fileResults">
                        <span class="scan-no-result">Upload a file and click scan to see results.</span>
                    </div>
                </div>
                <!-- URL TAB -->
                <div class="tab-pane fade" id="url" role="tabpanel" aria-labelledby="url-tab">
                    <div class="url-input-group mb-3 justify-content-center">
                        <input type="text" id="urlInput" class="url-input form-control form-control-lg" placeholder="Enter URL here..." autocomplete="off" />
                        <button id="scanUrlBtn" class="scan-btn btn btn-primary btn-lg" type="button" disabled>Scan URL</button>
                    </div>
                    
                    <!-- URL Results Section -->
                    <div class="results-content" id="urlResults">
                        <span class="scan-no-result">Enter a URL and click scan to see results.</span>
                    </div>
                </div>
                <!-- SEARCH TAB -->
                <div class="tab-pane fade" id="search" role="tabpanel" aria-labelledby="search-tab">
                    <div class="email-search-container">
                        <h3 class="text-center mb-4" style="color: var(--text-primary); font-weight: 600;">
                            <i class="bi bi-shield-exclamation me-2"></i>Check for Email Breaches
                        </h3>
                        <p class="text-center mb-4" style="color: var(--text-secondary); font-size: 0.95rem;">
                            Find out if your email address has been compromised in a data breach
                        </p>
                        <div class="email-input-group mb-3">
                            <input type="email" id="emailInput" class="email-input form-control form-control-lg" placeholder="Enter email address..." autocomplete="off" />
                            <button id="searchEmailBtn" class="search-btn btn btn-primary btn-lg" type="button" disabled>
                                <i class="bi bi-search me-2"></i><span id="search-btn-text">Search</span>
                            </button>
                        </div>
                        <div id="emailResultsContainer" class="email-results-container mt-4">
                            <!-- Results will be displayed here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-3 mb-md-0">
                    <div class="d-flex align-items-center mb-2">
                        <i class="bi bi-shield-lock logo-icon me-2"></i>
                        <span class="fw-bold fs-5">ClickSafe</span>
                    </div>
                    <p class="mb-0">&copy; 2024 ClickSafe. All rights reserved.</p>
                </div>
                <div class="col-md-4 mb-3 mb-md-0 text-center">
                    <div class="mb-2">Quick Links</div>
                    <a href="index.html#services">Services</a> |
                    <a href="index.html#about">About</a> |
                    <a href="safe_browsing.html">Safe Browsing</a> |
                    <a href="login.html">Login</a>
                </div>
                <div class="col-md-4 text-md-end text-center">
                    <div class="mb-2">Contact Us</div>
                    <a href="#" title="Email"><i class="bi bi-envelope"></i></a>
                    <a href="#" title="Twitter"><i class="bi bi-twitter"></i></a>
                    <a href="#" title="LinkedIn"><i class="bi bi-linkedin"></i></a>
                </div>
            </div>
        </div>
    </footer>
    <!-- Bootstrap JS and Popper.js -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.min.js"></script>
</body>
</html>
