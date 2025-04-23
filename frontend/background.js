// Lambda function URL
const LAMBDA_URL = 'https://rxirv3zxmn4woy6hztdqrmfigy0lsurc.lambda-url.ap-south-1.on.aws/';

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Function to query Lambda
async function queryLambda(username, inputText) {
    console.log(`Querying Lambda with username: ${username} and inputText: ${inputText}`);
    
    if (inputText === '' || inputText === undefined) {
        // If input text is empty, do not query Lambda
        console.log('Input text is empty, not querying Lambda');
        return;
    }

    try {
        const response = await fetch(LAMBDA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                query_text: inputText
            })
        });
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Lambda response:', data);
        
    } catch (error) {
        console.error('Error calling Lambda:', error);
    }
}

// Debounced version of the query function
const debouncedQuery = debounce((username, inputText) => {
    queryLambda(username, inputText);
}, 500);

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'INPUT_CHANGE') {
        // Get username from storage and query Lambda
        chrome.storage.local.get(['username'], function(result) {
            if (result.username) {
                debouncedQuery(result.username, message.text);
            } else {
                console.log('No username set in extension');
            }
        });
    }
});