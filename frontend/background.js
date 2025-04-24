const LAMBDA_URL = 'https://rxirv3zxmn4woy6hztdqrmfigy0lsurc.lambda-url.ap-south-1.on.aws/';

let notificationTimer;

// Add listener for when the extension icon is clicked
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
// Process text and send to Lambda
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log(`message: ${JSON.stringify(message)}`);
    
    if (message.type === 'INPUT_CHANGE') {
        sendToLambda(message.text);
    }
});

function parseResponseText(responseText) {
    // console.log(`parseResponseText`);
    // console.log(`responseText: ${responseText}`);
    
    try {
        const responseObj = JSON.parse(responseText);
        
        if (responseObj.results && responseObj.results.length > 0) {
            let formattedResponse = '';
            for (let i = 0; i < responseObj.results.length; i++) {
                formattedResponse += `\n\n${i + 1}. ${responseObj.results[i].analysis_raw_text}`;
            }
            return formattedResponse;
        } 
        else {
            return "No results found in the response";
        }
    } 
    catch (error) {
        return `Error parsing response: ${error.message}`;
    }
}

// Send text to Lambda function
async function sendToLambda(text) {
    // console.log(`sendToLambda`);
    // console.log(`text: ${text}`);

    try {
        // Get the username from storage
        chrome.storage.local.get(['username'], async function(result) {
            // console.log(`result: ${JSON.stringify(result)}`);
            if (!result.username) {
                console.warn('Username not set. Cannot send data to Lambda.');
                return;
            }
            
            const username = result.username;
            // console.log(`username: ${username}`);
            
            // Prepare data for Lambda
            const data = {
                username: username,
                content: text
            };
            console.log(`data: ${JSON.stringify(data)}`);
            
            // Send to Lambda
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
                
                // Get existing notifications or create new array
                chrome.storage.local.get(['notification'], function(result) {
                    let notification = result.notification || '';
                    console.log(`notification: ${notification}`);
                    
                    chrome.storage.local.set({notification: notification});
                    
                    showNotificationBadge();
                });
            }
        });
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
    
    // Set a new timer to clear the badge after 5 seconds
    notificationTimer = setTimeout(clearNotificationBadge, 5000);
}
function clearNotificationBadge() {
    chrome.action.setBadgeText({text: ''});
}