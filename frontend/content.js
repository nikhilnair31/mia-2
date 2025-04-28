let debounceTimer;

document.addEventListener('input', handleInput, true);

function handleInput(event) {
    console.log(`handleInput`);
    
    const target = event.target;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || event.target.getAttribute('contenteditable') === 'true' || target.isContentEditable) {
        clearTimeout(debounceTimer);
        
        debounceTimer = setTimeout(() => {
            let inputText = (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') ? target.value : target.textContent;
            console.log(`inputText: ${inputText}`);
            
            chrome.runtime.sendMessage({
                type: 'SEARCH_REQUEST',
                query: inputText,
                search: false
            });
        }, 1000);
    }
}