#!/bin/bash

# Simple chat interface styling test

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}   CHAKRA CHAT STYLING TEST        ${NC}"
echo -e "${YELLOW}====================================${NC}"

# Generate a simple HTML test file
cat > chat_test.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat UI Test</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      background-color: #f5f7fa;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    h1 {
      color: #00897B;
      margin-bottom: 20px;
      text-align: center;
    }
    .chat-container {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      height: 500px;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      background-color: #f9f9f9;
    }
    .message {
      display: flex;
      margin-bottom: 15px;
      max-width: 80%;
      width: 100%;
    }
    .message-user {
      align-self: flex-end;
      background-color: #e6f7ff;
      border-radius: 8px;
      padding: 10px;
    }
    .message-assistant {
      align-self: flex-start;
      background-color: #f5f5f5;
      border-radius: 8px;
      padding: 10px;
    }
    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background-color: #00897B;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-right: 10px;
    }
    .assistant-avatar {
      background-color: #546E7A;
    }
    .content {
      flex: 1;
    }
    .sender {
      font-weight: bold;
      margin-bottom: 4px;
    }
    .text {
      line-height: 1.5;
    }
    .buttons {
      display: flex;
      justify-content: center;
      margin-top: 20px;
      gap: 10px;
    }
    button {
      padding: 8px 15px;
      background-color: #00897B;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover {
      background-color: #00796b;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Chat UI Style Test</h1>
    <div class="chat-container" id="chatContainer">
      <!-- Messages will be added here -->
    </div>
    <div class="buttons">
      <button id="addUser">Add User Message</button>
      <button id="addAssistant">Add Assistant Message</button>
      <button id="clearChat">Clear Chat</button>
    </div>
  </div>

  <script>
    const chatContainer = document.getElementById('chatContainer');
    const addUserBtn = document.getElementById('addUser');
    const addAssistantBtn = document.getElementById('addAssistant');
    const clearChatBtn = document.getElementById('clearChat');
    
    const userMessages = [
      "Hi, I need help with creating an SLA for our cloud service",
      "We need to include uptime guarantees and response times",
      "What metrics would you recommend for a healthcare application?",
      "Can you provide examples of penalty clauses?",
      "Thank you for the information"
    ];
    
    const assistantMessages = [
      "Hello! I'd be happy to help you create an SLA for your cloud service.",
      "Great! For cloud services, I recommend including these key metrics: 1) Service availability (uptime), 2) Response time, 3) Resolution time, and 4) Error rates.",
      "For healthcare applications, I recommend including: 1) Data security compliance (HIPAA), 2) System availability (99.99% uptime), 3) Backup frequency, and 4) Recovery time objectives.",
      "Here's an example penalty clause: 'If monthly uptime falls below 99.9%, Client shall receive service credits equal to 10% of monthly fees. If uptime falls below 99%, credits shall increase to 25% of monthly fees.'",
      "You're welcome! Feel free to ask if you need any additional assistance with your SLA."
    ];
    
    let userCounter = 0;
    let assistantCounter = 0;
    
    function addUserMessage() {
      const message = document.createElement('div');
      message.className = 'message message-user';
      
      message.innerHTML = \`
        <div class="avatar">U</div>
        <div class="content">
          <div class="sender">You</div>
          <div class="text">\${userMessages[userCounter % userMessages.length]}</div>
        </div>
      \`;
      
      chatContainer.appendChild(message);
      userCounter++;
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function addAssistantMessage() {
      const message = document.createElement('div');
      message.className = 'message message-assistant';
      
      message.innerHTML = \`
        <div class="avatar assistant-avatar">A</div>
        <div class="content">
          <div class="sender">SLM Assistant</div>
          <div class="text">\${assistantMessages[assistantCounter % assistantMessages.length]}</div>
        </div>
      \`;
      
      chatContainer.appendChild(message);
      assistantCounter++;
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function clearChat() {
      chatContainer.innerHTML = '';
      userCounter = 0;
      assistantCounter = 0;
    }
    
    addUserBtn.addEventListener('click', addUserMessage);
    addAssistantBtn.addEventListener('click', addAssistantMessage);
    clearChatBtn.addEventListener('click', clearChat);
    
    // Add initial messages
    addAssistantMessage();
  </script>
</body>
</html>
EOF

echo -e "${GREEN}Created chat style test HTML file${NC}"

# Check if a browser is available
if command -v google-chrome &> /dev/null; then
    echo -e "${YELLOW}Opening test in Google Chrome...${NC}"
    google-chrome chat_test.html &
elif command -v firefox &> /dev/null; then
    echo -e "${YELLOW}Opening test in Firefox...${NC}"
    firefox chat_test.html &
elif command -v chromium-browser &> /dev/null; then
    echo -e "${YELLOW}Opening test in Chromium...${NC}"
    chromium-browser chat_test.html &
else
    echo -e "${YELLOW}No browser detected. Please open chat_test.html manually in your browser.${NC}"
fi

echo -e "${GREEN}Test complete!${NC}"
echo -e "${YELLOW}Use this test to verify that chat messages are visible and properly styled.${NC}"
echo -e "${YELLOW}Compare this to your application to check for styling issues.${NC}"