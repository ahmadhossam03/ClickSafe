// Listen for clicks on download links and send the URL to the background script
document.addEventListener('click', function(e) {
  let el = e.target;
  // Traverse up in case the click is on a child element
  while (el && el.tagName !== 'A') {
    el = el.parentElement;
  }
  if (el && el.tagName === 'A') {
    const href = el.href;
    // Only send fileDownload for download links
    if (
      (el.hasAttribute('download') || /\.(zip|exe|pdf|docx?|xlsx?|pptx?|rar|7z|tar|gz|mp3|mp4|avi|mkv|jpg|jpeg|png|gif)$/i.test(href)) &&
      href.startsWith('http')
    ) {
      e.preventDefault();
      // Send to Flask first
      fetch('http://127.0.0.1:5000/X_FileScan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: href })
      })
      .then(response => response.text())
      .then(data => {
        // Show a notification via background
        chrome.runtime.sendMessage({ action: 'showFileScanNotification', message: data });
        // Now trigger the download
        window.open(href, '_blank');
      })
      .catch(err => {
        chrome.runtime.sendMessage({ action: 'showFileScanNotification', message: 'File scan failed.' });
        window.open(href, '_blank');
      });
    }
  }
}, true);
