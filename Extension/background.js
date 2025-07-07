chrome.runtime.onInstalled.addListener(() => {
  console.log("ClickSafe extension installed.");
});

// Listen for tab updates (navigation, refresh, etc.)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active && tab.url && (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
    sendUrlToApi(tab.url);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'scanUrl') {
    const urlToScan = message.url;
    if (urlToScan && (urlToScan.startsWith('http://') || urlToScan.startsWith('https://'))) {
      sendUrlToApi(urlToScan, { fromPopup: message.fromPopup });
    }
  }
});

function sendUrlToApi(url, options = {}) {
  const fromPopup = options && Object.prototype.hasOwnProperty.call(options, 'fromPopup') && options.fromPopup === true;
  
  // First try the full-featured API
  const formData = new FormData();
  formData.append('url', url);
  
  fetch('http://127.0.0.1:5001/api/scan_url_json', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      // Try to parse as JSON first (full API), fallback to text (simple API)
      return response.text().then(text => {
        try {
          const json = JSON.parse(text);
          return json.result || text;
        } catch {
          return text;
        }
      });
    })
    .then(message => {
      chrome.storage.local.set({ lastScan: { url, message } });
      if (!fromPopup) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'ClickSafe Scan Result',
          message: message
        });
      }
    })
    .catch(err => {
      console.error('URL scan error:', err);
      chrome.storage.local.set({ lastScan: { url, message: 'Scan failed.' } });
      if (!fromPopup) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon.png',
          title: 'Scan Failed',
          message: 'Could not scan the URL. Backend may be down.'
        });
      }
    });
}

// Function to download file and send to scanning endpoint
async function downloadAndScanFile(downloadUrl, filename) {
  try {
    console.log('[ClickSafe] Starting file download and scan:', downloadUrl);
    
    // Download the file
    const response = await fetch(downloadUrl);
    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.status}`);
    }
    
    const blob = await response.blob();
    const formData = new FormData();
    formData.append('file', blob, filename);
    
    // Send to scanning endpoint
    const scanResponse = await fetch('http://127.0.0.1:5000/scanfile_extentsion', {
      method: 'POST',
      body: formData
    });
    
    const scanResult = await scanResponse.text();
    
    // Show scan result notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'ClickSafe Scan',
      message: scanResult
    });
    
    console.log('[ClickSafe] File scan completed:', scanResult);
    
  } catch (error) {
    console.error('[ClickSafe] Error in downloadAndScanFile:', error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'ClickSafe Scan',
      message: 'Failed to scan file. Backend may be down.'
    });
  }
}

// Step 1 & 2: Detect downloads and show "Download Detected!" notification
chrome.downloads.onCreated.addListener(function(downloadItem) {
  if (downloadItem && downloadItem.url && (downloadItem.url.startsWith('http://') || downloadItem.url.startsWith('https://'))) {
    console.log('[ClickSafe] Download detected:', downloadItem.url);
    
    // Step 2: Show "Download Detected!" notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'ClickSafe',
      message: 'Download Detected!'
    });
    
    // Step 3 & 4: Download file and scan it
    const filename = downloadItem.filename || extractFilenameFromUrl(downloadItem.url);
    downloadAndScanFile(downloadItem.url, filename);
  }
});

// Fallback: Detect navigation to downloadable files
chrome.webNavigation.onCommitted.addListener(function(details) {
  if (details.url && /\.(zip|exe|pdf|docx?|xlsx?|pptx?|rar|7z|tar|gz|mp3|mp4|avi|mkv|jpg|jpeg|png|gif|apk|dmg|pkg|deb|rpm)$/i.test(details.url)) {
    console.log('[ClickSafe] Download detected via navigation:', details.url);
    
    // Step 2: Show "Download Detected!" notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'ClickSafe',
      message: 'Download Detected!'
    });
    
    // Step 3 & 4: Download file and scan it
    const filename = extractFilenameFromUrl(details.url);
    downloadAndScanFile(details.url, filename);
  }
});

// Helper function to extract filename from URL
function extractFilenameFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const pathname = urlObj.pathname;
    const filename = pathname.split('/').pop();
    return filename || 'downloaded_file';
  } catch (error) {
    console.error('[ClickSafe] Error extracting filename:', error);
    return 'downloaded_file';
  }
}
