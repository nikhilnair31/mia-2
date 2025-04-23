document.addEventListener('DOMContentLoaded', function() {
    // Get references to DOM elements
    const usernameInput = document.getElementById('usernameInput');
    const saveBtn = document.getElementById('saveBtn');
    const statusMessage = document.getElementById('statusMessage');
    
    // Load saved options
    function loadOptions() {
      chrome.storage.local.get(['username'], function(result) {
        if (result.username) {
          usernameInput.value = result.username;
        }
      });
    }
    
    // Save options
    function saveOptions() {
      const username = usernameInput.value.trim();
      
      if (!username) {
        showStatus('Please enter a username', 'error');
        return;
      }
      
      chrome.storage.local.set({
        'username': username
      }, function() {
        // Show success message
        showStatus('Options saved successfully!', 'success');
        
        // Force an immediate check with the new username
        chrome.runtime.sendMessage({action: 'forceCheck'});
      });
    }
    
    // Function to show status messages
    function showStatus(message, type) {
      statusMessage.textContent = message;
      statusMessage.className = 'status-message ' + type;
      statusMessage.style.display = 'block';
      
      // Hide status message after 3 seconds
      setTimeout(function() {
        statusMessage.style.display = 'none';
      }, 3000);
    }
    
    // Load options when page loads
    loadOptions();
    
    // Setup save button
    saveBtn.addEventListener('click', saveOptions);
  });