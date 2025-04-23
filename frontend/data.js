document.addEventListener('DOMContentLoaded', function() {
    // Get reference to DOM elements
    const dataList = document.getElementById('dataList');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Function to format timestamps
    function formatTimestamp(timestamp) {
      if (!timestamp) return 'Unknown time';
      
      const date = new Date(timestamp);
      return date.toLocaleString();
    }
    
    // Function to create a pretty display for JSON data
    function createDataDisplay(data) {
      if (!data || Object.keys(data).length === 0) {
        return `<div class="no-data">No response data available</div>`;
      }
      
      let html = '';
      
      // If data is an array, display each item
      if (Array.isArray(data)) {
        data.forEach((item, index) => {
          html += `<div class="data-item">
                    <h3>Response ${index + 1}</h3>`;
          
          // Get timestamp if available
          const timestamp = item.timestamp || item.currenttimeformattedstring;
          if (timestamp) {
            html += `<div class="timestamp">${formatTimestamp(timestamp)}</div>`;
          }
          
          // Display all properties of the item
          html += `<pre>${JSON.stringify(item, null, 2)}</pre>
                  </div>`;
        });
      } 
      // If data is an object (not array)
      else {
        html += `<div class="data-item">`;
        
        // Get timestamp if available
        const timestamp = data.timestamp || data.currenttimeformattedstring;
        if (timestamp) {
          html += `<div class="timestamp">${formatTimestamp(timestamp)}</div>`;
        }
        
        // Display all properties
        html += `<pre>${JSON.stringify(data, null, 2)}</pre>
                </div>`;
      }
      
      return html;
    }
    
    // Function to load and display data
    function loadData() {
      chrome.storage.local.get(['responseData'], function(result) {
        if (result.responseData) {
          dataList.innerHTML = createDataDisplay(result.responseData);
        } else {
          dataList.innerHTML = `<div class="no-data">No response data available</div>`;
        }
      });
      
      // Notify background script that data has been viewed
      chrome.runtime.sendMessage({action: 'dataViewed'});
    }
    
    // Load data initially
    loadData();
    
    // Setup refresh button
    refreshBtn.addEventListener('click', function() {
      refreshBtn.textContent = 'Refreshing...';
      refreshBtn.disabled = true;
      
      // Request a force check from background script
      chrome.runtime.sendMessage({action: 'forceCheck'}, function(response) {
        // Reload data after check
        loadData();
        
        // Reset button state
        refreshBtn.textContent = 'Refresh Data';
        refreshBtn.disabled = false;
      });
    });
  });