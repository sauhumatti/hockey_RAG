// Import the QueryProcessingStatus class if you're using it
// import QueryProcessingStatus from './components/QueryProcessingStatus.js';

document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('query-input');
    const submitButton = document.getElementById('submit-query');
    const chatHistory = document.getElementById('chat-history');
    const typingIndicator = document.getElementById('typing-indicator');
    const infoButton = document.getElementById('info-button');
    const infoText = document.getElementById('info-text');

    // Ensure typing indicator is hidden initially
    typingIndicator.style.display = 'none';

    infoButton.addEventListener('click', function() {
        infoText.style.display = infoText.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function(event) {
        if (!infoButton.contains(event.target) && !infoText.contains(event.target)) {
            infoText.style.display = 'none';
        }
    });

    submitButton.addEventListener('click', handleSubmit);
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });

    function handleSubmit() {
        const query = queryInput.value.trim();
        if (query === '') {
            return;
        }

        addMessageToChat('user', query);
        showTypingIndicator();
        queryBackend(query);
        queryInput.value = '';
    }

    function queryBackend(query) {
        console.log('Sending query:', query);

        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received response:', data);
            hideTypingIndicator();
            if (data.error) {
                throw new Error(data.error);
            }
            addMessageToChat('ai', data.natural_language_answer);
        })
        .catch((error) => {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessageToChat('ai', 'An error occurred while processing your query: ' + error.message);
        });
    }

    function addMessageToChat(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', sender + '-message');
        
        if (sender === 'ai') {
            messageDiv.innerHTML = marked.parse(message);
        } else {
            messageDiv.textContent = message;
        }

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
});