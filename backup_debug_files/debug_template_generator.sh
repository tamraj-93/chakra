#!/bin/bash

# Set colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}     CHAKRA TEMPLATE GENERATOR DEBUG             ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Step 1: Create HTML file to simulate the template generator
DEBUG_FILE="debug_template_generator.html"

cat > "$DEBUG_FILE" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Template Generator Debug</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
      color: #333;
    }
    
    .container {
      max-width: 800px;
      margin: 0 auto;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      padding: 20px;
    }
    
    h1 {
      color: #00897B;
      border-bottom: 2px solid #00897B;
      padding-bottom: 10px;
    }
    
    .form-group {
      margin-bottom: 15px;
    }
    
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: bold;
    }
    
    input, select, textarea {
      width: 100%;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      box-sizing: border-box;
    }
    
    button {
      background-color: #00897B;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 10px 15px;
      cursor: pointer;
      font-size: 16px;
    }
    
    button:hover {
      background-color: #00796B;
    }
    
    .checkbox-group {
      margin-top: 10px;
    }
    
    .checkbox-item {
      margin-bottom: 5px;
    }
    
    .checkbox-item label {
      font-weight: normal;
      display: flex;
      align-items: center;
    }
    
    .checkbox-item input {
      width: auto;
      margin-right: 10px;
    }
    
    .alert {
      padding: 15px;
      margin-bottom: 20px;
      border-radius: 4px;
    }
    
    .alert-success {
      background-color: #d4edda;
      border: 1px solid #c3e6cb;
      color: #155724;
    }
    
    .alert-danger {
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      color: #721c24;
    }
    
    .json-display {
      background-color: #f8f9fa;
      padding: 15px;
      border-radius: 4px;
      overflow-x: auto;
      font-family: monospace;
      margin-top: 20px;
    }
    
    pre {
      margin: 0;
      white-space: pre-wrap;
    }
    
    .tabs {
      display: flex;
      margin-bottom: 15px;
      border-bottom: 1px solid #ddd;
    }
    
    .tab {
      padding: 10px 15px;
      cursor: pointer;
    }
    
    .tab.active {
      border-bottom: 2px solid #00897B;
      color: #00897B;
    }
    
    .tab-content {
      display: none;
    }
    
    .tab-content.active {
      display: block;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Template Generator Debug Tool</h1>
    
    <div class="tabs">
      <div class="tab active" onclick="showTab('formTab')">Form</div>
      <div class="tab" onclick="showTab('apiTab')">API Debug</div>
      <div class="tab" onclick="showTab('resultsTab')">Results</div>
    </div>
    
    <div id="formTab" class="tab-content active">
      <form id="templateForm">
        <div class="form-group">
          <label for="serviceName">Service Name</label>
          <input type="text" id="serviceName" value="Healthcare Cloud Application" required>
        </div>
        
        <div class="form-group">
          <label for="serviceType">Service Type</label>
          <select id="serviceType" required>
            <option value="">Select a service type</option>
            <option value="web_application">Web Application</option>
            <option value="api">API Service</option>
            <option value="database">Database Service</option>
            <option value="infrastructure" selected>Infrastructure</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="description">Service Description</label>
          <textarea id="description" rows="3" required>Cloud-based healthcare service that provides secure patient data management, appointment scheduling, telehealth services, and electronic health record (EHR) management in compliance with HIPAA regulations.</textarea>
        </div>
        
        <div class="form-group">
          <label>Industry</label>
          <select id="industry" required>
            <option value="">Select an industry</option>
            <option value="healthcare" selected>Healthcare</option>
            <option value="finance">Finance</option>
            <option value="education">Education</option>
            <option value="retail">Retail</option>
            <option value="technology">Technology</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Required Metrics</label>
          <div class="checkbox-group">
            <div class="checkbox-item">
              <label>
                <input type="checkbox" id="availability" checked>
                Availability
              </label>
            </div>
            <div class="checkbox-item">
              <label>
                <input type="checkbox" id="responseTime" checked>
                Response Time
              </label>
            </div>
            <div class="checkbox-item">
              <label>
                <input type="checkbox" id="throughput" checked>
                Throughput
              </label>
            </div>
            <div class="checkbox-item">
              <label>
                <input type="checkbox" id="errorRate" checked>
                Error Rate
              </label>
            </div>
          </div>
        </div>
        
        <button type="button" onclick="submitForm()">Generate Template</button>
      </form>
      
      <div id="successAlert" class="alert alert-success" style="display:none;">
        <h4>Template Generated Successfully!</h4>
        <p>Your SLA template is ready to download.</p>
        <button onclick="downloadTemplate()">Download Template</button>
      </div>
      
      <div id="errorAlert" class="alert alert-danger" style="display:none;">
        <h4>Error</h4>
        <p id="errorMessage"></p>
        <button onclick="submitForm()">Try Again</button>
      </div>
    </div>
    
    <div id="apiTab" class="tab-content">
      <h3>API Debug Information</h3>
      
      <div class="form-group">
        <label for="apiUrl">API Endpoint</label>
        <input type="text" id="apiUrl" value="http://localhost:8000/api/templates/">
      </div>
      
      <div class="form-group">
        <label for="authToken">Authentication Token (optional)</label>
        <input type="text" id="authToken" placeholder="Bearer ...">
      </div>
      
      <div class="checkbox-item">
        <label>
          <input type="checkbox" id="useAuth" checked>
          Use Authentication
        </label>
      </div>
      
      <button type="button" onclick="testApi('GET')">Test GET</button>
      <button type="button" onclick="testApi('POST')">Test POST</button>
      
      <div class="json-display">
        <h4>API Request</h4>
        <pre id="apiRequest"></pre>
      </div>
      
      <div class="json-display">
        <h4>API Response</h4>
        <pre id="apiResponse"></pre>
      </div>
    </div>
    
    <div id="resultsTab" class="tab-content">
      <h3>Template Results</h3>
      
      <div class="json-display">
        <pre id="templateResult"></pre>
      </div>
    </div>
  </div>
  
  <script>
    // Tab functionality
    function showTab(tabId) {
      // Hide all tabs
      const tabContents = document.getElementsByClassName('tab-content');
      for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
      }
      
      // Remove active class from tab buttons
      const tabs = document.getElementsByClassName('tab');
      for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
      }
      
      // Show selected tab
      document.getElementById(tabId).classList.add('active');
      
      // Find and activate the tab button
      const tabButtons = document.getElementsByClassName('tab');
      for (let i = 0; i < tabButtons.length; i++) {
        if (tabButtons[i].onclick.toString().includes(tabId)) {
          tabButtons[i].classList.add('active');
        }
      }
    }
    
    // Form submission
    function submitForm() {
      const serviceName = document.getElementById('serviceName').value;
      const serviceType = document.getElementById('serviceType').value;
      const description = document.getElementById('description').value;
      const industry = document.getElementById('industry').value;
      const availability = document.getElementById('availability').checked;
      const responseTime = document.getElementById('responseTime').checked;
      const throughput = document.getElementById('throughput').checked;
      const errorRate = document.getElementById('errorRate').checked;
      
      // Hide any existing alerts
      document.getElementById('successAlert').style.display = 'none';
      document.getElementById('errorAlert').style.display = 'none';
      
      // Validate form
      if (!serviceName || !serviceType || !description || !industry) {
        document.getElementById('errorMessage').textContent = 'Please fill out all required fields.';
        document.getElementById('errorAlert').style.display = 'block';
        return;
      }
      
      // Build metrics array
      const metrics = [];
      if (availability) metrics.push('availability');
      if (responseTime) metrics.push('response_time');
      if (throughput) metrics.push('throughput');
      if (errorRate) metrics.push('error_rate');
      
      const requestData = {
        name: serviceName,
        service_type: serviceType,
        description: description,
        industry: industry,
        is_public: true,
        metrics: metrics
      };
      
      // Display the request in the API tab
      document.getElementById('apiRequest').textContent = JSON.stringify(requestData, null, 2);
      
      // Make API request
      const apiUrl = document.getElementById('apiUrl').value;
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add authentication if needed
      if (document.getElementById('useAuth').checked && document.getElementById('authToken').value) {
        headers['Authorization'] = document.getElementById('authToken').value;
      }
      
      fetch(apiUrl, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(requestData)
      })
      .then(response => {
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
          return response.json().then(data => {
            return {
              status: response.status,
              statusText: response.statusText,
              data: data
            };
          });
        } else {
          return response.text().then(text => {
            return {
              status: response.status,
              statusText: response.statusText,
              data: text
            };
          });
        }
      })
      .then(result => {
        // Display the response in the API tab
        document.getElementById('apiResponse').textContent = JSON.stringify(result, null, 2);
        
        if (result.status >= 200 && result.status < 300) {
          // Success
          document.getElementById('successAlert').style.display = 'block';
          document.getElementById('templateResult').textContent = JSON.stringify(result.data, null, 2);
          // Show results tab
          showTab('resultsTab');
        } else {
          // Error
          document.getElementById('errorMessage').textContent = \`Error (\${result.status}): \${result.statusText}\`;
          document.getElementById('errorAlert').style.display = 'block';
        }
      })
      .catch(error => {
        // Network error
        document.getElementById('errorMessage').textContent = \`Network error: \${error.message}\`;
        document.getElementById('errorAlert').style.display = 'block';
        document.getElementById('apiResponse').textContent = JSON.stringify({error: error.message}, null, 2);
      });
    }
    
    // Test API functionality
    function testApi(method) {
      const apiUrl = document.getElementById('apiUrl').value;
      const headers = {
        'Content-Type': 'application/json'
      };
      
      // Add authentication if needed
      if (document.getElementById('useAuth').checked && document.getElementById('authToken').value) {
        headers['Authorization'] = document.getElementById('authToken').value;
      }
      
      const options = {
        method: method,
        headers: headers
      };
      
      // Add body for POST request
      if (method === 'POST') {
        const requestData = {
          name: 'Test Template',
          service_type: 'web_application',
          description: 'Test description',
          industry: 'technology',
          is_public: true,
          metrics: ['availability', 'response_time']
        };
        options.body = JSON.stringify(requestData);
        document.getElementById('apiRequest').textContent = JSON.stringify(requestData, null, 2);
      } else {
        document.getElementById('apiRequest').textContent = 'No request body for GET';
      }
      
      fetch(apiUrl, options)
      .then(response => {
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.indexOf('application/json') !== -1) {
          return response.json().then(data => {
            return {
              status: response.status,
              statusText: response.statusText,
              data: data
            };
          });
        } else {
          return response.text().then(text => {
            return {
              status: response.status,
              statusText: response.statusText,
              data: text
            };
          });
        }
      })
      .then(result => {
        document.getElementById('apiResponse').textContent = JSON.stringify(result, null, 2);
      })
      .catch(error => {
        document.getElementById('apiResponse').textContent = JSON.stringify({error: error.message}, null, 2);
      });
    }
    
    function downloadTemplate() {
      // In a real application, this would download the template
      alert('In a real application, this would download the template file.');
    }
  </script>
</body>
</html>
EOF

echo -e "${GREEN}Created debug file: ${DEBUG_FILE}${NC}"
echo -e "${YELLOW}Open this file in your browser to debug the template generator.${NC}"
echo -e "This tool helps:"
echo -e "  1. Test API endpoints directly"
echo -e "  2. View the request and response data"
echo -e "  3. Simulate the template generator form"
echo ""
echo -e "${BLUE}Instructions:${NC}"
echo -e "  1. Open ${DEBUG_FILE} in your browser"
echo -e "  2. Go to the 'API Debug' tab"
echo -e "  3. Enter a valid authentication token if needed"
echo -e "  4. Click 'Test GET' to test listing templates"
echo -e "  5. Click 'Test POST' to test creating a template"
echo -e "  6. Check the request and response data for errors"
echo ""

# Also provide a login helper to get authentication token
cat > "get_auth_token.sh" << EOF
#!/bin/bash

# Helper script to get authentication token
if [ -z "\$1" ] || [ -z "\$2" ]; then
  echo "Usage: \$0 <username> <password>"
  exit 1
fi

USERNAME="\$1"
PASSWORD="\$2"

# Try to login
TOKEN=\$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "'\$USERNAME'", "password": "'\$PASSWORD'"}' | 
  grep -o '"access_token":"[^"]*' | 
  sed 's/"access_token":"//')

if [ -n "\$TOKEN" ]; then
  echo "Authentication successful!"
  echo ""
  echo "Use this token in the debug tool:"
  echo "Bearer \$TOKEN"
else
  echo "Authentication failed. Check your credentials."
fi
EOF

chmod +x get_auth_token.sh

echo -e "${BLUE}Authentication Helper:${NC}"
echo -e "  Use ./get_auth_token.sh <username> <password> to get a token"
echo -e "  Example: ./get_auth_token.sh admin@example.com password123"
echo ""
echo -e "${BLUE}=================================================${NC}"