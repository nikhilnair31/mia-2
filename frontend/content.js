function handleInput(event) {
    const target = event.target;
    
    if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        event.target.getAttribute('contenteditable') === 'true' ||
        target.isContentEditable
    ) {
        // Get the text from the input element
        let inputText = '';
        
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            inputText = event.target.value;
        } 
        else {
            // For contenteditable elements
            inputText = event.target.textContent;
        }
        
        // Send the input text to the background script
        chrome.runtime.sendMessage({
            type: 'INPUT_CHANGE',
            text: inputText
        });
    }
}

document.addEventListener('input', handleInput, true);
document.addEventListener('keyup', handleInput, true);  

// Notify the user that the extension is active (optional)
console.log('MIA Assistant is active on this page');