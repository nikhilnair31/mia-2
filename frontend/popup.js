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
    
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        const url = new URL(tabs[0].url);
        const domain = url.hostname;

        chrome.storage.local.get(['excludedSites'], function(result) {
            const excludedSites = result.excludedSites || [];
            const isExcluded = excludedSites.includes(domain);

            const toggleButton = document.getElementById('toggleSite');
            toggleButton.textContent = isExcluded ? 'Enable for this site' : 'Disable for this site';

            toggleButton.addEventListener('click', function() {
                chrome.storage.local.get(['excludedSites'], function(result) {
                    let updatedSites = result.excludedSites || [];

                    if (updatedSites.includes(domain)) {
                        updatedSites = updatedSites.filter(site => site !== domain);
                    } else {
                        updatedSites.push(domain);
                    }

                    chrome.storage.local.set({ excludedSites: updatedSites }, function() {
                        toggleButton.textContent = updatedSites.includes(domain) ? 'Enable for this site' : 'Disable for this site';
                    });
                });
            });
        });
    });
});