document.addEventListener('DOMContentLoaded', function() {
    const responseContent = document.getElementById('responseContent');
    
    chrome.storage.local.get(['notification'], function(result) {
        chrome.action.setBadgeText({text: ''});
        
        if (result.notification) {
            responseContent.innerHTML = '';

            const responseItem = document.createElement('div');
            responseItem.className = 'response-item';
            
            try {
                const jsonResponse = JSON.parse(result.notification);
                
                if (typeof jsonResponse === 'object') {
                    const formattedContent = document.createElement('pre');
                    formattedContent.textContent = JSON.stringify(jsonResponse, null, 2);
                    responseItem.appendChild(formattedContent);
                } else {
                    responseItem.textContent = result.notification;
                }
            } 
            catch (e) {
                responseItem.textContent = "idk";
            }
            
            responseContent.appendChild(responseItem);
        } else {
            responseContent.innerHTML = '<p class="no-responses">No responses received yet.</p>';
        }
    });
});