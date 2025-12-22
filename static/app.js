// Chat History Manager
class ChatHistoryManager {
    constructor() {
        this.currentChatId = null;
        this.chats = this.loadChats();
    }

    // Load chats from localStorage
    loadChats() {
        const stored = localStorage.getItem('chatHistory');
        return stored ? JSON.parse(stored) : {};
    }

    // Save chats to localStorage
    saveChats() {
        localStorage.setItem('chatHistory', JSON.stringify(this.chats));
    }

    // Create a new chat
    createNewChat() {
        const chatId = Date.now().toString();
        this.currentChatId = chatId;
        this.chats[chatId] = {
            id: chatId,
            title: 'New Chat',
            messages: [],
            model: 'gpt-5.2',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        this.saveChats();
        return chatId;
    }

    // Add message to current chat
    addMessage(role, content) {
        if (!this.currentChatId) {
            this.createNewChat();
        }

        const message = {
            role,
            content,
            timestamp: new Date().toISOString()
        };

        this.chats[this.currentChatId].messages.push(message);
        this.chats[this.currentChatId].updatedAt = new Date().toISOString();

        // Auto-generate title from first user message
        if (role === 'user' && this.chats[this.currentChatId].messages.length === 1) {
            this.chats[this.currentChatId].title = content.substring(0, 50) + (content.length > 50 ? '...' : '');
        }

        this.saveChats();
    }

    // Get current chat messages
    getCurrentMessages() {
        if (!this.currentChatId || !this.chats[this.currentChatId]) {
            return [];
        }
        return this.chats[this.currentChatId].messages;
    }

    // Get all chats (sorted by most recent)
    getAllChats() {
        return Object.values(this.chats).sort((a, b) =>
            new Date(b.updatedAt) - new Date(a.updatedAt)
        );
    }

    // Load a specific chat
    loadChat(chatId) {
        this.currentChatId = chatId;
        return this.chats[chatId];
    }

    // Delete a chat
    deleteChat(chatId) {
        delete this.chats[chatId];
        if (this.currentChatId === chatId) {
            this.currentChatId = null;
        }
        this.saveChats();
    }

    // Clear all chats
    clearAllChats() {
        this.chats = {};
        this.currentChatId = null;
        this.saveChats();
    }
}

// Initialize chat history manager
const chatHistory = new ChatHistoryManager();

// DOM Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const messagesContainer = document.getElementById('messagesContainer');
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const messageInput2 = document.getElementById('messageInput2');
const sendBtn = document.getElementById('sendBtn');
const sendBtn2 = document.getElementById('sendBtn2');
const modelSelect = document.getElementById('modelSelect');
const modelSelect2 = document.getElementById('modelSelect2');
const newChatBtn = document.getElementById('newChat');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveSettingsBtn = document.getElementById('saveSettings');

// Auth helper
function getApiKey() {
    return localStorage.getItem('gateway_api_key') || '';
}

// Configure marked.js
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
});

// Event Listeners
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput2.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
sendBtn2.addEventListener('click', sendMessage);

newChatBtn.addEventListener('click', () => {
    startNewChat();
});

// Sync model selectors
modelSelect.addEventListener('change', () => {
    modelSelect2.value = modelSelect.value;
});

modelSelect2.addEventListener('change', () => {
    modelSelect.value = modelSelect2.value;
});

// Settings Modal
settingsBtn.addEventListener('click', () => {
    apiKeyInput.value = getApiKey();
    settingsModal.style.display = 'flex';
});

saveSettingsBtn.addEventListener('click', () => {
    localStorage.setItem('gateway_api_key', apiKeyInput.value.trim());
    settingsModal.style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
});

// Functions
function startNewChat() {
    chatHistory.createNewChat();
    messagesDiv.innerHTML = '';
    welcomeScreen.style.display = 'flex';
    messagesContainer.style.display = 'none';
    messageInput.value = '';
    messageInput2.value = '';
}

function switchToMessagesView() {
    welcomeScreen.style.display = 'none';
    messagesContainer.style.display = 'flex';
}

function addMessage(role, content, isMarkdown = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;

    // Add avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = role === 'user' ? 'S' : 'AI';

    // Add content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isMarkdown && role === 'assistant') {
        contentDiv.innerHTML = marked.parse(content);
    } else {
        contentDiv.textContent = content;
    }

    if (role === 'user') {
        msgDiv.appendChild(contentDiv);
        msgDiv.appendChild(avatarDiv);
    } else {
        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);
    }

    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.textContent = 'Thinking';
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideLoading() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

async function sendMessage() {
    const input = messageInput.value.trim() || messageInput2.value.trim();
    if (!input) return;

    const model = modelSelect.value || modelSelect2.value;

    // Switch to messages view if on welcome screen
    if (welcomeScreen.style.display !== 'none') {
        switchToMessagesView();
    }

    // Add user message to UI and history
    addMessage('user', input);
    chatHistory.addMessage('user', input);

    // Clear inputs
    messageInput.value = '';
    messageInput2.value = '';

    // Disable send buttons
    sendBtn.disabled = true;
    sendBtn2.disabled = true;

    // Show loading
    showLoading();

    try {
        const response = await fetch('/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getApiKey()}`
            },
            body: JSON.stringify({
                messages: chatHistory.getCurrentMessages().map(m => ({ role: m.role, content: m.content })),
                model: model,
                max_tokens: 2048,
                temperature: 0.7
            })
        });

        hideLoading();

        if (!response.ok) {
            const error = await response.json();
            const errorMsg = `Error: ${error.detail || 'Unknown error'}`;
            addMessage('assistant', errorMsg);
            chatHistory.addMessage('assistant', errorMsg);
            return;
        }

        const data = await response.json();
        addMessage('assistant', data.response, true);
        chatHistory.addMessage('assistant', data.response);

    } catch (error) {
        hideLoading();
        const errorMsg = `Error: ${error.message}`;
        addMessage('assistant', errorMsg);
        chatHistory.addMessage('assistant', errorMsg);
    } finally {
        sendBtn.disabled = false;
        sendBtn2.disabled = false;
        messageInput.focus();
    }
}

// Load previous chat if exists
function loadPreviousChat() {
    const chats = chatHistory.getAllChats();
    if (chats.length > 0) {
        const lastChat = chats[0];
        chatHistory.loadChat(lastChat.id);

        if (lastChat.messages.length > 0) {
            switchToMessagesView();
            lastChat.messages.forEach(msg => {
                addMessage(msg.role, msg.content, msg.role === 'assistant');
            });
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Optionally load the last chat
    // loadPreviousChat();

    // Focus on input
    messageInput.focus();
});

// Export for potential use in other scripts
window.chatHistory = chatHistory;
