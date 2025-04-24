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
                        const responseItem = document.createElement('div');
                        responseItem.className = 'response-item';
                        
                        if (item.text) {
                            const textContent = document.createElement('p');
                            textContent.textContent = item.text;
                            responseItem.appendChild(textContent);
                            
                            if (item.timestamp) {
                                const timestamp = document.createElement('small');
                                timestamp.className = 'timestamp';
                                timestamp.textContent = item.timestamp;
                                responseItem.appendChild(timestamp);
                            }
                        } else {
                            // Fallback if the structure is different
                            const formattedContent = document.createElement('pre');
                            formattedContent.textContent = JSON.stringify(item, null, 2);
                            responseItem.appendChild(formattedContent);
                        }
                        
                        responseContent.appendChild(responseItem);
                    });
                } 
                else if (typeof jsonResponse === 'object') {
                    // Single object
                    const responseItem = document.createElement('div');
                    responseItem.className = 'response-item';
                    const formattedContent = document.createElement('pre');
                    formattedContent.textContent = JSON.stringify(jsonResponse, null, 2);
                    responseItem.appendChild(formattedContent);
                    responseContent.appendChild(responseItem);
                } 
                else {
                    // Simple string
                    const responseItem = document.createElement('div');
                    responseItem.className = 'response-item';
                    responseItem.textContent = result.notification;
                    responseContent.appendChild(responseItem);
                }
            } 
            catch (e) {
                const responseItem = document.createElement('div');
                responseItem.className = 'response-item error';
                responseItem.textContent = "Error parsing response: " + e.message;
                responseContent.appendChild(responseItem);
            }
        } else {
            responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
        }
    });
});