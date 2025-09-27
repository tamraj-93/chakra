#!/bin/bash

# Script to help debug the chat interface

echo "======================"
echo " CHAT INTERFACE DEBUG "
echo "======================"

# Check if the browser is installed
if command -v google-chrome &> /dev/null; then
  BROWSER="google-chrome"
elif command -v firefox &> /dev/null; then
  BROWSER="firefox"
elif command -v chromium-browser &> /dev/null; then
  BROWSER="chromium-browser"
else
  echo "Cannot find a browser to open developer tools with."
  exit 1
fi

# Generate a simple HTML page that logs messages
cat > debug.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat Interface Debug</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    .instruction { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    pre { background: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }
    .btn { padding: 10px 15px; background: #00897B; color: white; border: none; border-radius: 5px; cursor: pointer; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Chat Interface Debug Helper</h1>
    
    <div class="instruction">
      <h3>Follow these steps:</h3>
      <ol>
        <li>Keep this window open</li>
        <li>Open your Angular app in another tab</li>
        <li>Open browser developer tools (F12)</li>
        <li>Go to the Console tab</li>
        <li>Try sending a message in your chat interface</li>
        <li>Look for console logs about the messages array</li>
      </ol>
    </div>
    
    <h3>Common Issues & Solutions:</h3>
    <pre>
1. Messages not appearing in UI:
   - Check if the messages array is being properly updated
   - Ensure change detection is triggered after updates
   - Verify that the template bindings are correct

2. Authentication Issues:
   - Check if token is stored in localStorage
   - Verify that AuthInterceptor is adding the token to requests
   - Make sure token format matches what the API expects

3. Messages sent but not displayed:
   - Ensure the messages array is being properly updated
   - Check for proper data binding and change detection
   - Look for errors in the console
    </pre>
    
    <button class="btn" onclick="window.open('http://localhost:4200/consultation', '_blank')">Open Consultation Page</button>
  </div>
</body>
</html>
EOF

# Open the debug helper
echo "Opening debug helper..."
$BROWSER debug.html &

echo "Done! Follow the instructions in the browser window."