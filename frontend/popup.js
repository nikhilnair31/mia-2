document.addEventListener('DOMContentLoaded', function() {
    chrome.action.setBadgeText({text: ''});

    chrome.storage.local.get(['username'], function(result) {
        if (result.username) {
            document.getElementById('username').value = result.username;
        }
    });
    
    document.getElementById('saveUsername').addEventListener('click', function() {
        const username = document.getElementById('username').value;
        if (username) {
            chrome.storage.local.set({ username: username }, function() {
                const status = document.getElementById('status');
                status.display = 'block';
                status.textContent = 'Username saved!';
                setTimeout(() => {
                    status.textContent = '';
                }, 2000);
            });
        }
    });
    
    document.getElementById('viewResponses').addEventListener('click', function() {
        window.open('response.html', '_blank');
    });
});