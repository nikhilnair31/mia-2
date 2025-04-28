document.addEventListener('DOMContentLoaded', function() {
    let searchDebounceTimer;
    const searchInput = document.getElementById('searchInput');
    const responseContent = document.getElementById('responseContent');
    
    searchInput.addEventListener('input', searchDisplay);

    // Listen for messages from background.js with search results
    chrome.runtime.onMessage.addListener(function(message) {
        if (message.type === 'SEARCH_RESULTS') {
            displayResponses(message.results);
        } 
        else if (message.type === 'SEARCH_ERROR') {
            responseContent.innerHTML = `<p class="no-responses">Search error: ${message.error}</p>`;
        }
    });

    // Initially load the notifications when the page loads
    chrome.storage.local.get(['notification'], function(result) {
        // Clear the badge text when the popup is opened
        chrome.action.setBadgeText({text: ''});
        
        // Check if there's a search text stored in local storage and set it in the input field
        getSearchText().then(searchText => {
            searchInput.value = searchText ? searchText : '';
        });

        // Check if there are any notifications to display
        if (result.notification) {
            displayResponses(result.notification);
        } 
        else {
            responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
        }
    });
    
    // Load the username when the page loads
    const userIcon = document.getElementById('userIcon');
    chrome.storage.local.get(['username'], function(result) {
        if (result.username) {
            userIcon.textContent = result.username.charAt(0).toUpperCase();
        } 
        else {
            userIcon.textContent = 'U';
        }
    });
    
    async function getSearchText() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['searchText'], function(result) {
                if (result.searchText) {
                    resolve(result.searchText);
                } else {
                    resolve(null);
                }
            });
        });
    }

    function displayResponses(responses) {
        responseContent.innerHTML = ''; // Clear existing content
        if (Array.isArray(responses) && responses.length > 0) {
            responses.forEach(item => {
                const gridItem = document.createElement('div');
                gridItem.className = 'grid-item';
    
                if (item.image_presigned_url) {
                    const img = document.createElement('img');
                    img.src = item.image_presigned_url;
                    img.onerror = function() {
                        this.outerHTML = `<div class="broken-image">Image not available</div>`;
                    };
                    gridItem.appendChild(img);
                } else {
                    const brokenImage = document.createElement('div');
                    brokenImage.className = 'broken-image';
                    brokenImage.textContent = 'No image available';
                    gridItem.appendChild(brokenImage);
                }
    
                if (item.timestamp_str) {
                    const timestamp = document.createElement('div');
                    timestamp.className = 'timestamp';
                    timestamp.textContent = item.timestamp_str;
                    gridItem.appendChild(timestamp);
                }
    
                if (item.image_text) {
                    const analysisText = document.createElement('div');
                    analysisText.className = 'analysis-text';
                    analysisText.textContent = item.image_text;
                    gridItem.appendChild(analysisText);
                }
    
                if (true) {
                    const deleteButton = document.createElement('button');
                    deleteButton.className = 'delete-button';
                    deleteButton.innerHTML = '&times;'; // × symbol
                    deleteButton.title = 'Delete item';
                    deleteButton.onclick = function(e) {
                        e.stopPropagation(); // Prevent triggering other click events
                        deleteItem(item.image_key);
                    };
                    gridItem.appendChild(deleteButton);
                }
    
                responseContent.appendChild(gridItem);
            });
        } 
        else {
            responseContent.innerHTML = '<p class="no-responses">No results found.</p>';
        }
    }
    
    function searchDisplay() {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            const query = this.value.trim();
            if (query) {
                searchResponses(query);
            } 
            else {
                // If the search bar is cleared, reload the initial notifications
                chrome.storage.local.get(['notification'], function(result) {
                });
            }
        }, 300); // Debounce for 300ms
    }
    function searchResponses(query) {
        responseContent.innerHTML = '<p class="no-responses">Searching...</p>';
        chrome.runtime.sendMessage({
            type: 'SEARCH_REQUEST',
            query: query,
            search: true
        });
    }

    function deleteItem(id) {
        console.log('Can delete item with ID:', id);
        if (confirm('Are you sure you want to delete this item?')) {
            console.log('Deleting item with ID:', id);
            // Here you would normally make an API call to delete the item
            // Then refresh the display
            
            // For demo purposes, we'll filter out the deleted item
            // const updatedItems = sampleItems.filter(item => item.id !== id);
            // createGridItems(updatedItems);
        }
    }
});