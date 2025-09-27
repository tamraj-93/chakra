#!/bin/bash

# Add the SLA example to the system for demonstration

# Set colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================${NC}"
echo -e "${YELLOW}   IMPORTING SLA EXAMPLE DATA      ${NC}"
echo -e "${YELLOW}====================================${NC}"

# Check if SQLite DB exists
if [ ! -f ./backend/chakra.db ]; then
    echo -e "${RED}Error: Database not found at ./backend/chakra.db${NC}"
    echo "Please run ./init_db.sh first to initialize the database."
    exit 1
fi

# Copy example file to the backend directory
cp examples/healthcare_cloud_sla_example.json backend/data/

echo -e "${GREEN}SLA example template copied to backend/data/ directory${NC}"
echo ""
echo -e "${GREEN}You can now use this SLA template in your application:${NC}"
echo -e "${YELLOW}1. Navigate to your application${NC}"
echo -e "${YELLOW}2. Login with admin credentials${NC}"
echo -e "${YELLOW}3. Go to the Template Generator section${NC}"
echo -e "${YELLOW}4. You should see the Healthcare Cloud SLA template available${NC}"

# Create a simple HTML viewer for the SLA example
cat > sla_viewer.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Healthcare SLA Example</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 0;
      padding: 20px;
      color: #333;
      max-width: 1000px;
      margin: 0 auto;
    }
    header {
      background-color: #00897B;
      color: white;
      padding: 20px;
      text-align: center;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    h1 {
      margin: 0;
    }
    .container {
      display: flex;
      gap: 20px;
    }
    .markdown {
      flex: 2;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 5px;
    }
    .json {
      flex: 1;
      background: #f5f5f5;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 5px;
      font-family: monospace;
      font-size: 12px;
      overflow: auto;
      height: 600px;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 20px;
    }
    table, th, td {
      border: 1px solid #ddd;
    }
    th, td {
      padding: 10px;
      text-align: left;
    }
    th {
      background-color: #f2f2f2;
    }
    @media (max-width: 768px) {
      .container {
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>Healthcare Cloud SLA Example</h1>
    <p>Service Level Agreement Template for Healthcare Applications</p>
  </header>
  
  <div class="container">
    <div class="markdown">
      <iframe src="examples/healthcare_cloud_sla_example.md" style="width:100%; height:600px; border:none;"></iframe>
    </div>
    <div class="json">
      <pre id="json-content">Loading...</pre>
    </div>
  </div>
  
  <script>
    // Fetch and display the JSON
    fetch('examples/healthcare_cloud_sla_example.json')
      .then(response => response.text())
      .then(text => {
        try {
          const json = JSON.parse(text);
          document.getElementById('json-content').textContent = JSON.stringify(json, null, 2);
        } catch (e) {
          document.getElementById('json-content').textContent = "Error parsing JSON: " + e;
        }
      })
      .catch(error => {
        document.getElementById('json-content').textContent = "Error loading JSON: " + error;
      });
  </script>
</body>
</html>
EOF

echo ""
echo -e "${GREEN}Created SLA viewer HTML file${NC}"
echo -e "${GREEN}You can view the example SLA by opening sla_viewer.html in your browser${NC}"