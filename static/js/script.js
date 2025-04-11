document.addEventListener("DOMContentLoaded", () => {
    const chatHistory = document.getElementById("chatHistory");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const clearChatButton = document.getElementById("clearChat");

    const API_URL = "/chat";
    let currentSessionId = null;

    sendButton.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    clearChatButton.addEventListener("click", clearChat);

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) {
            showError("Please enter a message");
            return;
        }

        addMessageToChat("user", message);
        userInput.value = "";

        const loadingElement = showLoading();

        fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                message: message,
                session_id: currentSessionId 
            }),
        })
            .then((response) => {
                if (!response.ok) throw new Error(`Server error: ${response.status}`);
                return response.json();
            })
            .then((data) => {
                loadingElement.remove();
                if (data.error) {
                    showError(data.error);
                } else if (data.response) {
                    addMessageToChat("bot", data.response);
                    currentSessionId = data.session_id;  // Update session ID
                } else {
                    showError("No valid response from server");
                }
            })
            .catch((error) => {
                loadingElement.remove();
                showError(`Failed to connect: ${error.message}`);
                console.error("Fetch error:", error);
            });
    }

    function addMessageToChat(sender, content) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        if (sender === "user") {
            messageDiv.classList.add("user-message");
            messageDiv.textContent = content;
        } else {
            messageDiv.classList.add("bot-message");
            const contentDiv = document.createElement("div");
            contentDiv.classList.add("bot-message-content");
            contentDiv.innerHTML = content;  // Render HTML directly
            messageDiv.appendChild(contentDiv);
        }

        const timeElement = document.createElement("div");
        timeElement.classList.add("timestamp");
        timeElement.textContent = timestamp;
        messageDiv.appendChild(timeElement);

        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function showLoading() {
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("loading");
        const dotsDiv = document.createElement("div");
        dotsDiv.classList.add("loading-dots");
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement("span");
            dotsDiv.appendChild(dot);
        }
        loadingDiv.appendChild(dotsDiv);
        chatHistory.appendChild(loadingDiv);
        scrollToBottom();
        return loadingDiv;
    }

    function showError(message) {
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("error-message");
        errorDiv.textContent = message;
        chatHistory.appendChild(errorDiv);
        scrollToBottom();
        setTimeout(() => errorDiv.remove(), 5000);
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function clearChat() {
        while (chatHistory.children.length > 1) {
            chatHistory.removeChild(chatHistory.lastChild);
        }
        currentSessionId = null;  // Reset session ID when clearing chat
    }
});