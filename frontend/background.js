const LAMBDA_URL = 'https://rxirv3zxmn4woy6hztdqrmfigy0lsurc.lambda-url.ap-south-1.on.aws/';

let notificationTimer;

chrome.action.onClicked.addListener(() => {
    clearNotificationBadge();
    
    if (badgeText === '!') {
        // If there was a notification badge, open the response page
        chrome.tabs.create({ url: 'response.html' });
    } 
    else {
        // Otherwise, open the normal popup
        // Note: This won't actually do anything since the popup is defined in manifest.json
        // The popup will open automatically on click if there's no notification
    }
});
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log(`message: ${JSON.stringify(message)}`);
    
    if (message.type === 'INPUT_CHANGE') {
        sendToLambda(message.text);
    }
});

function parseResponseText(responseText) {
    try {
        const responseObj = typeof responseText === 'string' ? JSON.parse(responseText) : responseText;
        
        if (responseObj.results && responseObj.results.length > 0) {
            const formattedResults = responseObj.results.map(result => ({
                image_text: result.analysis_raw_text,
                image_url: result.image_objectkey,
                timestamp: result.timestamp_str
            }));
            
            console.log(`Found ${formattedResults.length} results`);
            return formattedResults;
        } else {
            console.log('No results found in response');
            return [];
        }
    } catch (error) {
        console.error(`Error parsing response: ${error.message}`);
        return [];
    }
}

async function sendToLambda(text) {
    try {
        // Get username from storage using a Promise wrapper
        const result = await new Promise((resolve) => {
            chrome.storage.local.get(['username'], resolve);
        });
        
        if (!result.username) {
            console.warn('Username not set. Cannot send data to Lambda.');
            return;
        }
            
        const username = result.username;
        
        const data = {
            username: username,
            content: text
        };
        console.log(`data: ${JSON.stringify(data)}`);
        
        const response = await fetch(LAMBDA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        // Check if response is 200
        if (response.status === 200) {
            // Get the response content
            const responseText = await response.text();
            console.log(`responseText: ${responseText}`);

            // Parse the response into a formatted bullet point list
            const formattedResponse = parseResponseText(responseText);
            console.log(`formattedResponse: ${formattedResponse}`);

            if (formattedResponse.length === 0) {
                console.warn('No valid response received from Lambda.');
                return;
            }
            chrome.storage.local.set({notification: formattedResponse});
            
            showNotificationBadge();
        }
    } 
    catch (error) {
        console.error('Error sending data to Lambda:', error);
    }
}

function showNotificationBadge() {
    // Set the badge
    chrome.action.setBadgeText({text: '!'});
    chrome.action.setBadgeBackgroundColor({color: '#FF0000'});
    
    // Clear the previous timer if it exists
    if (notificationTimer) {
        clearTimeout(notificationTimer);
    }
    
    // Set a new timer to clear the badge after X seconds
    notificationTimer = setTimeout(clearNotificationBadge, 15000);
}
function clearNotificationBadge() {
    chrome.action.setBadgeText({text: ''});
}