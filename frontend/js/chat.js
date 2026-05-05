/**
 * TaxBot AI — Chatbot UI Controller
 * Handles message sending, display, suggestions, and NLP metadata
 */

document.addEventListener('DOMContentLoaded', () => {
    initChat();
});

function initChat() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('btn-chat-send');
    const resetBtn = document.getElementById('btn-chat-reset');

    sendBtn.addEventListener('click', () => sendChatMessage());
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    resetBtn.addEventListener('click', async () => {
        try { await API.resetChat(); } catch(e) {}
        const messages = document.getElementById('chat-messages');
        messages.innerHTML = `
            <div class="chat-welcome">
                <div class="welcome-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <h3>Welcome to TaxBot AI</h3>
                <p>I'm your intelligent tax filing assistant. Ask me anything about taxes!</p>
                <div class="welcome-suggestions">
                    <button class="suggestion-chip" onclick="sendSuggestion('Hello, help me file my taxes')">Start Filing</button>
                    <button class="suggestion-chip" onclick="sendSuggestion('Which tax regime should I choose?')">Compare Regimes</button>
                    <button class="suggestion-chip" onclick="sendSuggestion('What deductions can I claim?')">Explore Deductions</button>
                    <button class="suggestion-chip" onclick="sendSuggestion('Calculate my tax')">Calculate Tax</button>
                </div>
            </div>`;
        document.getElementById('chat-intent-display').textContent = 'Intent: waiting...';
        document.getElementById('chat-confidence-display').textContent = 'Confidence: —';
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Clear welcome if first message
    const welcome = document.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    // Display user message
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTyping();

    try {
        const result = await API.sendMessage(message);

        hideTyping();

        if (result.status === 'success') {
            const data = result.data;

            // Display bot response
            addMessage(data.response, 'bot', data.suggestions);

            // Update NLP metadata
            document.getElementById('chat-intent-display').textContent =
                `Intent: ${data.intent} (${data.nlp_details?.intent_method || 'rule_based'})`;
            document.getElementById('chat-confidence-display').textContent =
                `Confidence: ${data.confidence}%`;
        }
    } catch (error) {
        hideTyping();
        addMessage("I'm sorry, I couldn't connect to the server. Please ensure the backend is running on port 8000.", 'bot');
    }
}

function sendSuggestion(text) {
    document.getElementById('chat-input').value = text;
    sendChatMessage();
}

function addMessage(text, sender, suggestions = []) {
    const messages = document.getElementById('chat-messages');

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    if (sender === 'bot') {
        avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>';
    } else {
        avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
    }

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Process text: handle newlines and basic formatting
    let formattedText = text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code style="background:var(--code-bg);padding:0.1rem 0.3rem;border-radius:3px;font-family:var(--font-mono);font-size:0.8rem;">$1</code>');

    bubble.innerHTML = formattedText;

    // Add suggestions
    if (sender === 'bot' && suggestions.length > 0) {
        const sugDiv = document.createElement('div');
        sugDiv.className = 'message-suggestions';
        suggestions.forEach(sug => {
            const chip = document.createElement('button');
            chip.className = 'suggestion-chip';
            chip.textContent = sug;
            chip.onclick = () => sendSuggestion(sug);
            sugDiv.appendChild(chip);
        });
        bubble.appendChild(sugDiv);
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    messages.appendChild(msgDiv);

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
    const messages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}
