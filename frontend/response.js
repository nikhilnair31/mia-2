document.addEventListener('DOMContentLoaded', function() {
    const responseContent = document.getElementById('responseContent');
    const searchInput = document.getElementById('searchInput');
    const userIcon = document.getElementById('userIcon');

    // Function to display the responses
    function displayResponses(responses) {
        responseContent.innerHTML = ''; // Clear existing content
        if (Array.isArray(responses) && responses.length > 0) {
            responses.forEach(item => {
                const gridItem = document.createElement('div');
                gridItem.className = 'grid-item';

                if (item.image_url) {
                    const img = document.createElement('img');
                    img.src = item.image_url;
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

                if (item.timestamp) {
                    const timestamp = document.createElement('div');
                    timestamp.className = 'timestamp';
                    timestamp.textContent = item.timestamp;
                    gridItem.appendChild(timestamp);
                }

                if (item.image_text) {
                    const analysisText = document.createElement('div');
                    analysisText.className = 'analysis-text';
                    analysisText.textContent = item.image_text;
                    gridItem.appendChild(analysisText);
                }

                responseContent.appendChild(gridItem);
            });
        } else {
            responseContent.innerHTML = '<p class="no-responses">No results found.</p>';
        }
    }

    // Function to fetch and display responses based on a search query
    function searchResponses(query) {
        responseContent.innerHTML = '<p class="no-responses">Searching...</p>';
        chrome.runtime.sendMessage({
            type: 'SEARCH_REQUEST',
            query: query,
            search: true
        });
    }
    
    // Event listener for the search input
    let searchDebounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            const query = this.value.trim();
            if (query) {
                searchResponses(query);
            } 
            else {
                // If the search bar is cleared, reload the initial notifications
                chrome.storage.local.get(['notification'], function(result) {
                    if (result.notification) {
                        displayResponses(result.notification);
                    } else {
                        responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
                    }
                });
            }
        }, 300); // Debounce for 300ms
    });

    // Initially load the notifications when the page loads
    chrome.storage.local.get(['notification'], function(result) {
        chrome.action.setBadgeText({text: ''});
        if (result.notification) {
            displayResponses(result.notification);
        } else {
            responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
        }
    });

    // Load the username when the page loads
    chrome.storage.local.get(['username'], function(result) {
        if (result.username) {
            userIcon.textContent = result.username.charAt(0).toUpperCase();
        } 
        else {
            userIcon.textContent = 'U';
        }
    });

    // Listen for messages from background.js with search results
    chrome.runtime.onMessage.addListener(function(message) {
        if (message.type === 'SEARCH_RESULTS') {
            displayResponses(message.results);
        } 
        else if (message.type === 'SEARCH_ERROR') {
            responseContent.innerHTML = `<p class="no-responses">Search error: ${message.error}</p>`;
        }
    });
});