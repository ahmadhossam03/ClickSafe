<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit();
}

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['email']) || empty($input['email'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Email address is required']);
    exit();
}

$email = filter_var($input['email'], FILTER_VALIDATE_EMAIL);
if (!$email) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid email address format']);
    exit();
}

// HIBP API endpoint
$url = "https://haveibeenpwned.com/api/v3/breachedaccount/" . urlencode($email);

// Set up the request headers
// IMPORTANT: Replace 'YOUR_API_KEY_HERE' with your actual HIBP API key
$headers = [
    'User-Agent: ClickSafe-App',
    'hibp-api-key: YOUR_API_KEY_HERE'
];

// Initialize cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(500);
    echo json_encode(['error' => 'Network error: ' . $error]);
    exit();
}

if ($httpCode === 200) {
    // Email found in breaches
    $breaches = json_decode($response, true);
    echo json_encode($breaches);
} elseif ($httpCode === 404) {
    // Email not found in any breaches
    echo json_encode(['message' => 'Good news — no pwnage found!']);
} elseif ($httpCode === 401) {
    http_response_code(401);
    echo json_encode(['error' => 'Invalid API key. Please check your HIBP API key configuration.']);
} elseif ($httpCode === 429) {
    http_response_code(429);
    echo json_encode(['error' => 'Rate limit exceeded. Please try again later.']);
} else {
    http_response_code($httpCode);
    echo json_encode(['error' => 'An error occurred while checking the email']);
}
?>
