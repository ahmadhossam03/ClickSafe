# ClickSafe Extension - Request Full Report Feature

## What the Extension Does

When you click the **"Request full report"** button in the ClickSafe Chrome extension:

1. **Gets the current website URL** you're viewing
2. **Creates a guest session** on your ClickSafe website
3. **Scans the URL** using your Flask API
4. **Opens a new tab** with your scan results page: `http://localhost/grad/scan_results.html`
5. **Shows scan results** with guest user indicators

## The Flow

```
User clicks "Request full report" button
    ↓
Extension gets current tab URL (e.g., "https://www.google.com")
    ↓
Extension calls: http://localhost/grad/guest_login.php
    ↓
Extension calls: http://127.0.0.1:5000/scanurl (your Flask API)
    ↓
Extension opens: http://localhost/grad/scan_results.html?type=URL&value=...&guest=1
    ↓
User sees scan results on your website
```

## Files Involved

- **popup.js**: Contains the "Request full report" button logic
- **guest_login.php**: PHP script that creates guest sessions
- **api.py**: Flask API that performs URL scanning
- **scan_results.html**: Your website page that shows results

## What URLs Are Used

✅ **Correct URLs (your website):**
- `http://localhost/grad/guest_login.php` - Creates guest session
- `http://localhost/grad/scan_results.html` - Shows scan results
- `http://localhost/grad/login.html` - Login page with guest option

✅ **Correct API URL:**
- `http://127.0.0.1:5000/scanurl` - Your Flask API for scanning

❌ **No wrong/external URLs** - Everything redirects to your website

## Test the Extension

1. Load the extension in Chrome
2. Go to any website (e.g., https://www.google.com)
3. Click the ClickSafe extension icon
4. Click "Request full report"
5. New tab should open with `http://localhost/grad/scan_results.html`
6. Should show "👤 Guest User" badge and scan results

The extension is now clean and only redirects to your website at `http://localhost/grad/`.
