# ClickSafe Extension Integration with Guest Login System

## Overview
The ClickSafe browser extension has been updated to seamlessly integrate with the website's guest login system, providing users with automatic URL scanning and full scan reports directly from the extension.

## How It Works

### 1. Extension Popup (`popup.js`)
- **Current URL Display**: Shows the URL of the active tab at the top of the extension popup
- **Quick Scan Button**: Performs immediate scanning and shows results in the extension
- **Request Full Report Button**: Creates a guest session and opens the full scan results in the website

### 2. Guest Session Creation Process
When a user clicks "Request Full Report":

1. **Generate Guest ID**: Creates unique guest ID (`ext_guest_TIMESTAMP_RANDOM`)
2. **API Call**: Sends POST request to `/grad/api/create_guest_session.php`
3. **Dual Session**: Creates both PHP session and Flask API session
4. **Redirect**: Opens scan results page with auto-scan enabled

### 3. Auto-Scan Integration (`scan_results.html`)
The scan results page detects extension requests and automatically:

1. **Detects Extension Origin**: Checks for `from_extension=1` parameter
2. **Auto-Scan Mode**: Checks for `auto_scan=1` parameter
3. **Performs Scan**: Automatically scans the URL without user interaction
4. **Live Updates**: Shows loading spinner and real-time scan progress
5. **Display Results**: Shows formatted scan results with threat analysis

### 4. Session Management
- **24-Hour Sessions**: Guest sessions last 24 hours
- **Cross-Platform**: Sessions work across extension and website
- **Automatic Cleanup**: Expired sessions are cleaned up automatically

## Files Modified/Created

### Extension Files:
1. **`popup.js`** - Updated guest session creation and URL handling
   - Improved error handling
   - Better logging for debugging
   - Automatic popup closure after redirect

### Website Files:
1. **`api/create_guest_session.php`** - New dedicated endpoint for extension requests
   - CORS headers for cross-origin requests
   - JSON and form data support
   - Dual session creation (PHP + Flask)

2. **`scan_results.html`** - Enhanced auto-scan functionality
   - Extension detection
   - Automatic URL scanning
   - Real-time progress updates
   - Loading animations

3. **`guest_login.html`** - New quick access page for fallback scenarios
   - Auto-redirect functionality
   - URL display for user confirmation
   - Error handling with retry options

## User Experience Flow

### Normal Extension Usage:
1. User browses to a website
2. Extension icon shows in browser toolbar
3. User clicks extension icon to open popup
4. Current URL is displayed at the top
5. User clicks "Request Full Report"
6. New tab opens with guest session and scan results
7. Scan runs automatically and results are displayed

### Extension Features:
- **Current URL Display**: Always shows the active tab's URL
- **Quick Scan**: Fast scan with results shown in extension popup
- **Full Report**: Complete scan with detailed results on website
- **File Monitoring**: Automatic file download scanning
- **Notifications**: Desktop notifications for scan results

### Error Handling:
- **Network Issues**: Fallback to simple guest login page
- **API Unavailable**: Graceful degradation with error messages
- **Session Failures**: Multiple retry mechanisms
- **Invalid URLs**: Proper validation and user feedback

## Testing the Integration

### Test Extension Integration:
1. Install the extension in Chrome
2. Navigate to any website (e.g., `https://google.com`)
3. Click the extension icon
4. Verify the current URL is displayed at the top
5. Click "Request Full Report"
6. New tab should open with guest session
7. Scan should start automatically
8. Results should display within 10-30 seconds

### Test Session Persistence:
1. Complete the above test
2. Check that guest session is created in website
3. Navigate to other pages on the website
4. Session should remain active
5. Logout to clear session

### Test Error Handling:
1. Turn off Flask API (stop Python server)
2. Try "Request Full Report"
3. Should still work with PHP session only
4. Results should show appropriate error if scan fails

## API Endpoints Used

1. **`/grad/api/create_guest_session.php`** - Creates guest sessions for extension
2. **`/grad/api/session_heartbeat.php`** - Maintains session activity
3. **`http://127.0.0.1:5000/guest_login`** - Flask API guest session
4. **`http://127.0.0.1:5000/scanurl`** - URL scanning endpoint

## Security Features

- **CORS Protection**: Proper CORS headers for cross-origin requests
- **Session Validation**: Guest sessions are validated on each request
- **Automatic Expiration**: Sessions expire after 24 hours of inactivity
- **Secure Cookies**: HTTP-only cookies with proper security settings

The extension now provides a seamless experience where users can quickly get detailed scan reports without manual login, making the security analysis more accessible and user-friendly.
