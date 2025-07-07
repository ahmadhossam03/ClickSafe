// filepath: [popup.js](http://_vscodecontentref_/0)
document.addEventListener('DOMContentLoaded', () => {
  const urlDiv = document.getElementById('current-url');

  // Dark mode functionality
  const darkToggle = document.getElementById('darkToggle');
  const darkToggleIcon = document.getElementById('darkToggleIcon');
  const body = document.body;

  // Load saved dark mode preference
  chrome.storage.local.get(['darkMode'], (result) => {
    if (result.darkMode) {
      body.classList.add('dark-mode');
      darkToggleIcon.className = 'bi bi-sun';
    } else {
      body.classList.remove('dark-mode');
      darkToggleIcon.className = 'bi bi-moon';
    }
  });

  // Dark mode toggle functionality
  darkToggle.addEventListener('click', () => {
    const isDarkMode = body.classList.contains('dark-mode');
    
    if (isDarkMode) {
      // Switch to light mode
      body.classList.remove('dark-mode');
      darkToggleIcon.className = 'bi bi-moon';
      chrome.storage.local.set({ darkMode: false });
    } else {
      // Switch to dark mode
      body.classList.add('dark-mode');
      darkToggleIcon.className = 'bi bi-sun';
      chrome.storage.local.set({ darkMode: true });
    }
  });

  if (chrome.tabs && chrome.tabs.query) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0] && tabs[0].url) {
        let displayUrl = tabs[0].url.split('?')[0];
        if (displayUrl.length > 50) {
          displayUrl = displayUrl.slice(0, 50) + '...';
        }
        urlDiv.textContent = displayUrl;
      } else {
        urlDiv.textContent = 'No active tab URL found.';
      }
    });
  } else {
    urlDiv.textContent = 'Cannot access tab info.';
  }

  // Show scan result and status circle
  function updateScanResult() {
    chrome.storage.local.get('lastScan', data => {
      const resultText = document.getElementById('scan-result-text');
      const circle = document.getElementById('scan-status-circle');
      if (data.lastScan) {
        const msg = data.lastScan.message || 'No result';
        resultText.textContent = msg;
        if (msg.toLowerCase().includes("is safe")) {
          circle.style.background = "#19c37d";
          circle.style.boxShadow = "0 0 16px #19c37d88";
        } else if (msg.toLowerCase().includes("not safe")) {
          circle.style.background = "#e53935";
          circle.style.boxShadow = "0 0 16px #e5393588";
        } else {
          circle.style.background = "#ccc";
          circle.style.boxShadow = "0 0 12px #888";
        }
      } else {
        resultText.textContent = 'No scan result yet.';
        circle.style.background = "#ccc";
        circle.style.boxShadow = "0 0 12px #888";
      }
    });
  }

  updateScanResult();

  // Listen for storage changes to update scan result live after clicking a link
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'local' && changes.lastScan) {
      updateScanResult();
    }
  });

  // Add scan button functionality
  const scanBtn = document.getElementById('scan-btn');
  const scanBtnText = document.getElementById('scan-btn-text');
  const scanBtnLoader = document.getElementById('scan-btn-loader');
  if (scanBtn) {
    scanBtn.addEventListener('click', () => {
      // Show loading spinner, hide text
      if (scanBtnLoader) scanBtnLoader.style.display = '';
      if (scanBtnText) scanBtnText.style.display = 'none';
      // Button press effect
      scanBtn.style.transform = 'scale(0.95)';
      scanBtn.style.boxShadow = '0 0 0 #0000';
      setTimeout(() => {
        scanBtn.style.transform = '';
        scanBtn.style.boxShadow = '';
      }, 120);
      // Get current tab and trigger scan as if a link was clicked
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url && (tabs[0].url.startsWith('http://') || tabs[0].url.startsWith('https://'))) {
          chrome.runtime.sendMessage({ action: 'scanUrl', url: tabs[0].url, fromPopup: true });
        } else {
          // Hide loader if no valid tab
          if (scanBtnLoader) scanBtnLoader.style.display = 'none';
          if (scanBtnText) scanBtnText.style.display = '';
        }
      });
    });
  }

  // Hide loading spinner when scan result updates
  function hideScanBtnLoader() {
    if (scanBtnLoader) scanBtnLoader.style.display = 'none';
    if (scanBtnText) scanBtnText.style.display = '';
  }

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'local' && changes.lastScan) {
      updateScanResult();
      hideScanBtnLoader();
    }
  });





  // Add report button functionality
  const reportBtn = document.getElementById('report-btn');
  if (reportBtn) {
    reportBtn.addEventListener('click', () => {
      // Button press effect
      reportBtn.style.transform = 'scale(0.95)';
      reportBtn.style.boxShadow = '0 0 0 #0000';
      setTimeout(() => {
        reportBtn.style.transform = '';
        reportBtn.style.boxShadow = '';
      }, 120);
      
      // Get current tab URL and redirect to scan_results.html with guest auth
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url && (tabs[0].url.startsWith('http://') || tabs[0].url.startsWith('https://'))) {
          const currentUrl = tabs[0].url;
          
          // Create guest session and trigger scan, then redirect to scan_results.html
          createGuestSessionAndScan(currentUrl);
        } else {
          // No valid URL, just open the main page with guest login
          chrome.tabs.create({ url: 'http://localhost/grad/login.html' });
        }
      });
    });
  }

  // Function to create guest session and perform scan
  async function createGuestSessionAndScan(urlToScan) {
    try {
      console.log('Starting guest session creation and scan for:', urlToScan);
      
      // Step 1: Create a unique guest ID
      const guestId = 'ext_guest_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      console.log('Generated guest ID:', guestId);
      
      // Step 2: Create guest session via dedicated API endpoint
      const guestResponse = await fetch('http://localhost/grad/api/create_guest_session.php', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guest_id: guestId
        })
      });

      if (!guestResponse.ok) {
        throw new Error(`Failed to create guest session: ${guestResponse.status}`);
      }
      
      const guestData = await guestResponse.json();
      if (!guestData.success) {
        throw new Error(`Guest session error: ${guestData.message}`);
      }
      
      console.log('Guest session created successfully:', guestData);
      
      // Step 3: Redirect to scan_results.html with auto-scan enabled
      const scanResultsUrl = `http://localhost/grad/scan_results.html?type=URL&value=${encodeURIComponent(urlToScan)}&guest=1&guest_id=${guestId}&from_extension=1&auto_scan=1`;
      
      console.log('Opening scan results page:', scanResultsUrl);
      chrome.tabs.create({ url: scanResultsUrl }, (newTab) => {
        if (chrome.runtime.lastError) {
          console.error('Error opening scan results tab:', chrome.runtime.lastError);
        } else {
          console.log('Scan results tab opened successfully:', newTab.id);
          // Close the extension popup after successful redirect
          window.close();
        }
      });

    } catch (error) {
      console.error('Error in guest scan process:', error);
      
      // Fallback: redirect directly to guest login page
      const fallbackUrl = `http://localhost/grad/guest_login.html?url=${encodeURIComponent(urlToScan)}`;
      console.log('Using fallback URL:', fallbackUrl);
      chrome.tabs.create({ url: fallbackUrl }, () => {
        if (chrome.runtime.lastError) {
          console.error('Fallback failed:', chrome.runtime.lastError);
          // Final fallback: just open the main page
          chrome.tabs.create({ url: 'http://localhost/grad/login.html' });
        }
        window.close();
      });
    }
  }
});