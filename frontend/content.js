function handleInput(event) {
    console.log(`handleInput`);
    // console.log(`event: ${JSON.stringify(event)}`);
    
    const target = event.target;
    // console.log(`target: ${JSON.stringify(target)}`);
    
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || event.target.getAttribute('contenteditable') === 'true' || target.isContentEditable) {
        // Get the text from the input element
        let inputText = '';
        
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            inputText = event.target.value;
        } 
        else {
            // For contenteditable elements
            inputText = event.target.textContent;
        }
        console.log(`inputText: ${inputText}`);
        
        // Send the input text to the background script
        chrome.runtime.sendMessage({
            type: 'INPUT_CHANGE',
            text: inputText
        });
    }
}

document.addEventListener('input', handleInput, true);