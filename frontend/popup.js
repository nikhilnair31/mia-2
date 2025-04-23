document.addEventListener('DOMContentLoaded', function() {
    // Get saved username if it exists
    chrome.storage.local.get(['username'], function(result) {
        if (result.username) {
            document.getElementById('username').value = result.username;
        }
    });
    
    // Save username button click handler
    document.getElementById('saveUsername').addEventListener('click', function() {
        const username = document.getElementById('username').value;
        if (username) {
            chrome.storage.local.set({ username: username }, function() {
                const status = document.getElementById('status');
                status.textContent = 'Username saved!';
                setTimeout(() => {
                    status.textContent = '';
                }, 2000);
            });
        }
    });
});