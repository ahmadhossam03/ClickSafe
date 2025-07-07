<?php
session_start();

// Check if user is authenticated (either regular user or guest)
if (!isset($_SESSION['username']) && !isset($_SESSION['is_guest'])) {
    header("Location: login.html");
    exit();
}

$is_guest = isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true;
$username = $is_guest ? 'Guest User' : $_SESSION['username'];

// Get scan results from session if available
$scan_result = $_SESSION['last_scan_result'] ?? null;
$scan_type = $_SESSION['last_scan_type'] ?? null;
$scan_value = $_SESSION['last_scan_value'] ?? null;

// Clear the session data after retrieving
if ($scan_result) {
    unset($_SESSION['last_scan_result']);
    unset($_SESSION['last_scan_type']);
    unset($_SESSION['last_scan_value']);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scan Results - ClickSafe</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="icon" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/icons/shield-lock.svg">
    <!-- Roboto font for clean look -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
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
        html, body {
            height: 100%;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            background: var(--white);
            color: var(--text-primary);
            font-family: 'Roboto', sans-serif;
        }
        .navbar {
            background: var(--white) !important;
            box-shadow: 0 2px 8px rgba(10,35,66,0.04);
        }
        .navbar-brand {
            color: var(--navy) !important;
            font-weight: 700;
            font-size: 1.5rem;
        }
        .logo-icon {
            font-size: 2rem;
            color: var(--blue);
            margin-right: 0.5rem;
        }
        .results-container {
            max-width: 900px;
            margin: 4rem auto 2rem auto;
        }
        .card {
            border-radius: 1rem;
            box-shadow: var(--shadow);
            border: none;
            background: var(--card-bg);
            color: var(--text-primary);
        }
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
        }
        .btn-primary {
            background: var(--blue);
            border: none;
            font-weight: 600;
        }
        .btn-primary:hover {
            background: #1456a0;
        }
        .status-badge {
            font-size: 1rem;
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            margin-bottom: 1rem;
            display: inline-block;
        }
        .status-safe {
            background: rgba(24,119,242,0.08);
            color: var(--blue);
        }
        .status-warning {
            background: rgba(255,193,7,0.15);
            color: #ffc107;
        }
        .status-danger {
            background: rgba(220,53,69,0.15);
            color: #dc3545;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-shield-lock logo-icon"></i>ClickSafe
            </a>
            <div class="ms-auto">
                <span class="me-3"><?php echo htmlspecialchars($username); ?></span>
                <a href="logout.php" class="btn btn-outline-danger btn-sm">
                    <i class="bi bi-box-arrow-right me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>

    <!-- Results Section -->
    <div class="results-container">
        <div class="card p-4">
            <div class="text-center mb-4">
                <i class="bi bi-shield-lock logo-icon mb-2"></i>
                <h3 class="fw-bold mb-2">Scan Results</h3>
                <?php if ($scan_type && $scan_value): ?>
                    <p class="text-muted">Scanned <?php echo ucfirst($scan_type); ?>: <strong><?php echo htmlspecialchars($scan_value); ?></strong></p>
                <?php endif; ?>
                <div class="status-badge status-safe" id="statusBadge">
                    <i class="bi bi-shield-check me-2"></i>Scan Complete
                </div>
            </div>
            
            <div class="results-content" id="scanResults">
                <?php if ($scan_result): ?>
                    <?php echo htmlspecialchars($scan_result); ?>
                <?php else: ?>
                    <div class="text-center text-muted">
                        <i class="bi bi-exclamation-circle mb-2" style="font-size: 2rem;"></i>
                        <div>No scan results available.</div>
                        <small>Please go back and perform a new scan.</small>
                    </div>
                <?php endif; ?>
            </div>
            
            <div class="text-center">
                <a href="main_page.php" class="btn btn-primary">
                    <i class="bi bi-house-door me-2"></i>Back to Home
                </a>
                <a href="main_page.php" class="btn btn-outline-secondary ms-2">
                    <i class="bi bi-arrow-repeat me-2"></i>New Scan
                </a>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Update status badge based on results
        document.addEventListener('DOMContentLoaded', function() {
            const resultsContent = document.getElementById('scanResults').textContent;
            const statusBadge = document.getElementById('statusBadge');
            
            if (resultsContent.toLowerCase().includes('threat') || resultsContent.toLowerCase().includes('malicious') || resultsContent.toLowerCase().includes('danger')) {
                statusBadge.className = 'status-badge status-danger';
                statusBadge.innerHTML = '<i class="bi bi-shield-x me-2"></i>Threats Detected';
            } else if (resultsContent.toLowerCase().includes('warning') || resultsContent.toLowerCase().includes('caution') || resultsContent.toLowerCase().includes('suspicious')) {
                statusBadge.className = 'status-badge status-warning';
                statusBadge.innerHTML = '<i class="bi bi-shield-exclamation me-2"></i>Warnings Found';
            } else if (resultsContent.toLowerCase().includes('safe') || resultsContent.toLowerCase().includes('clean')) {
                statusBadge.className = 'status-badge status-safe';
                statusBadge.innerHTML = '<i class="bi bi-shield-check me-2"></i>Safe';
            }
        });
    </script>
</body>
</html>
