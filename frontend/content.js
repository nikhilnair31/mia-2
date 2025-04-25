let debounceTimer;

function handleInput(event) {
    console.log(`handleInput`);
    
    const target = event.target;
    
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || event.target.getAttribute('contenteditable') === 'true' || target.isContentEditable) {
        // Clear any existing timer
        clearTimeout(debounceTimer);
        
        // Set a new timer
        debounceTimer = setTimeout(() => {
            let inputText = '';
            
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                inputText = target.value;
            } 
            else {
                inputText = target.textContent;
            }
            console.log(`inputText: ${inputText}`);
            
            chrome.runtime.sendMessage({
                type: 'INPUT_CHANGE',
                text: inputText
            });
        }, 500); // 500ms delay
    }
}

document.addEventListener('input', handleInput, true);