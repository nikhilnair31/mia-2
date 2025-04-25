// const searchInput = document.getElementById('searchInput');

// let allItems = []; 

// searchInput.addEventListener('input', function(e) {
//     const searchTerm = e.target.value;
//     console.log('Search term:', searchTerm);
    
//     chrome.runtime.sendMessage({
//         type: 'INPUT_CHANGE',
//         text: searchTerm
//     });
    
//     filterItems(searchTerm);
// });

// function filterItems(searchTerm) {
//     if (!allItems.length) return;
    
//     const gridItems = document.querySelectorAll('.grid-item');
//     gridItems.forEach(item => {
//         item.style.display = 'none';
//     });
    
//     if (!searchTerm) {
//         gridItems.forEach(item => {
//             item.style.display = 'block';
//         });
//         return;
//     }
    
//     allItems.forEach((item, index) => {
//         const analysisText = item.analysis || item.analysis_raw_text || '';
//         const timestamp = item.timestamp || '';
        
//         if (analysisText.toLowerCase().includes(searchTerm) || 
//             timestamp.toLowerCase().includes(searchTerm)) {
//             gridItems[index].style.display = 'block';
//         }
//     });
// }

document.addEventListener('DOMContentLoaded', function() {
    const responseContent = document.getElementById('responseContent');
    
    chrome.storage.local.get(['notification'], function(result) {
        console.log(`result: ${JSON.stringify(result)}`);

        chrome.action.setBadgeText({text: ''});
        
        if (result.notification) {
            responseContent.innerHTML = '';

            try {
                console.log(`result.notification type : ${typeof result.notification}`);

                const jsonResponse = result.notification;
                console.log(`jsonResponse: ${JSON.stringify(jsonResponse)}`);
                
                if (Array.isArray(jsonResponse)) {
                    // Handle array of messages
                    jsonResponse.forEach(item => {
                        const gridItem = document.createElement('div');
                        gridItem.className = 'grid-item';
                        
                        if (item.image_url) {
                            // Create image element
                            const img = document.createElement('img');
                            img.src = item.image_url;
                            img.onerror = function() {
                                // Replace with broken image placeholder
                                this.outerHTML = `<div class="broken-image">Image not available</div>`;
                            };
                            gridItem.appendChild(img);
                        } 
                        else {
                            // Fallback if no image
                            const brokenImage = document.createElement('div');
                            brokenImage.className = 'broken-image';
                            brokenImage.textContent = 'No image available';
                            gridItem.appendChild(brokenImage);
                        }
                            
                        // Add timestamp
                        if (item.timestamp) {
                            const timestamp = document.createElement('div');
                            timestamp.className = 'timestamp';
                            timestamp.textContent = item.timestamp;
                            gridItem.appendChild(timestamp);
                        }
                            
                        // Show analysis if available
                        if (item.image_text) {
                            const analysisText = document.createElement('div');
                            analysisText.className = 'analysis-text';
                            analysisText.textContent = item.image_text;
                            gridItem.appendChild(analysisText);
                        }
                        
                        responseContent.appendChild(gridItem);
                    });
                } 
                else if (typeof jsonResponse === 'object') {
                    // Single object - handle similarly
                    const item = jsonResponse;
                    const gridItem = document.createElement('div');
                    gridItem.className = 'grid-item';
                    
                    if (item.image_url) {
                        const img = document.createElement('img');
                        img.src = item.image_url;
                        img.onerror = function() {
                            this.outerHTML = `<div class="broken-image">Image not available</div>`;
                        };
                        gridItem.appendChild(img);
                        
                        if (item.timestamp) {
                            const timestamp = document.createElement('div');
                            timestamp.className = 'timestamp';
                            timestamp.textContent = item.timestamp;
                            gridItem.appendChild(timestamp);
                        }
                        
                        if (item.analysis) {
                            const analysisText = document.createElement('div');
                            analysisText.className = 'analysis-text';
                            analysisText.textContent = item.analysis;
                            gridItem.appendChild(analysisText);
                        }
                        // For backward compatibility with analysis_raw_text
                        else if (item.analysis_raw_text) {
                            const analysisText = document.createElement('div');
                            analysisText.className = 'analysis-text';
                            analysisText.textContent = item.analysis_raw_text;
                            gridItem.appendChild(analysisText);
                        }
                    } else {
                        const brokenImage = document.createElement('div');
                        brokenImage.className = 'broken-image';
                        brokenImage.textContent = 'No image available';
                        gridItem.appendChild(brokenImage);
                        
                        if (item.analysis) {
                            const analysisText = document.createElement('div');
                            analysisText.className = 'analysis-text';
                            analysisText.textContent = item.analysis;
                            gridItem.appendChild(analysisText);
                        }
                        // For backward compatibility with analysis_raw_text
                        else if (item.analysis_raw_text) {
                            const analysisText = document.createElement('div');
                            analysisText.className = 'analysis-text';
                            analysisText.textContent = item.analysis_raw_text;
                            gridItem.appendChild(analysisText);
                        }
                    }
                    
                    responseContent.appendChild(gridItem);
                } 
                else {
                    // Simple string - show error message
                    responseContent.innerHTML = '<p class="no-responses">Invalid data format received.</p>';
                }
            } 
            catch (e) {
                responseContent.innerHTML = `<p class="no-responses">Error parsing response: ${e.message}</p>`;
            }
        } 
        else {
            responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
        }
    });
});