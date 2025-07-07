# ClickSafe Guest Session System - Updated Implementation

## Overview
The guest login functionality has been updated to provide persistent sessions that remain active until the user explicitly logs out or closes the website, addressing session timeout issues.

## How It Works

### 1. Session Creation (`guest_login.php`)
- **Extended Session Duration**: PHP sessions now last 24 hours (86400 seconds)
- **Secure Cookie Configuration**: Sessions use secure cookie parameters
- **Client-side Storage**: Guest session data is stored in browser localStorage for persistence
- **Visual Feedback**: Users see a loading screen during session setup

### 2. Session Persistence (`main_page.php`)
- **Extended PHP Session**: Same 24-hour configuration as login
- **localStorage Synchronization**: Session data is continuously synced with localStorage
- **Heartbeat System**: Every 5 minutes, the client sends a heartbeat to keep the session alive
- **Visibility Monitoring**: When the page becomes visible, it checks if the session is still valid

### 3. Session Heartbeat API (`api/session_heartbeat.php`)
- **Heartbeat Endpoint**: `/api/session_heartbeat.php` with actions: `heartbeat` and `check`
- **Session Validation**: Checks if guest sessions are still valid
- **Activity Updates**: Updates last activity timestamp
- **Flask API Integration**: Also updates the Python Flask API when available

### 4. Session Recovery (`login.html`)
- **Automatic Detection**: Checks for existing guest sessions on page load
- **Session Restoration**: Offers to continue with existing guest session
- **Expiration Handling**: Automatically cleans up expired sessions

### 5. Proper Logout (`logout.php`)
- **Complete Cleanup**: Destroys PHP session and clears localStorage
- **Visual Feedback**: Shows logout progress with loading animation
- **Clean Redirect**: Redirects to home page after cleanup

### 6. Flask API Updates (`api.py`)
- **Session Restoration**: Can restore existing guest sessions instead of always creating new ones
- **Automatic Cleanup**: Periodically removes expired sessions (every hour)
- **Better Error Handling**: Improved error handling for session operations

## Key Features

### ✅ Session Persistence
- Sessions persist across browser restarts
- 24-hour session duration
- Automatic session recovery on page load

### ✅ Session Management
- Heartbeat system keeps sessions alive
- Automatic cleanup of expired sessions
- Proper session termination on logout

### ✅ User Experience
- Visual feedback during session operations
- Option to continue existing sessions
- Seamless session restoration

### ✅ Security
- Secure cookie configuration
- Session validation
- Automatic expiration handling

## Files Modified

1. **`guest_login.php`** - Enhanced session creation with persistence
2. **`main_page.php`** - Added session monitoring and heartbeat system
3. **`api/session_heartbeat.php`** - New API for session management
4. **`logout.php`** - Improved logout with localStorage cleanup
5. **`login.html`** - Added session recovery functionality
6. **`grad/url/urlScan/api.py`** - Enhanced Flask API session handling

## Testing the System

### Test Guest Session Persistence:
1. Log in as guest
2. Close browser completely
3. Reopen browser and go to login page
4. Should see option to "Continue as Guest"
5. Click "Continue as Guest" - should redirect to main page

### Test Session Heartbeat:
1. Log in as guest
2. Leave tab open but switch to other tabs
3. Wait 10+ minutes
4. Return to the tab - session should still be active

### Test Logout:
1. Log in as guest
2. Click logout button
3. Should see loading screen and be redirected to home page
4. Going back to login should not show "Continue as Guest" option

## Session Duration
- **Default**: 24 hours from last activity
- **Heartbeat**: Every 5 minutes while page is active
- **Cleanup**: Expired sessions are cleaned up hourly

The system now provides a robust guest session experience that persists until the user decides to log out or the 24-hour session expires due to inactivity.
