# Modify the index.html to use local Bootstrap files instead of CDN
# This script is used during the Docker build process

# Check if file exists
if [ -f "./src/index.html" ]; then
    echo "Modifying index.html to use local Bootstrap files..."
    
    # Download Bootstrap files
    mkdir -p ./src/assets/bootstrap
    wget -q https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css -O ./src/assets/bootstrap/bootstrap.min.css
    wget -q https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js -O ./src/assets/bootstrap/bootstrap.bundle.min.js
    
    # Update the index.html file to use local files
    sed -i 's|https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css|assets/bootstrap/bootstrap.min.css|g' ./src/index.html
    sed -i 's|https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js|assets/bootstrap/bootstrap.bundle.min.js|g' ./src/index.html
    
    echo "Index.html modified to use local Bootstrap files."
else
    echo "Error: src/index.html not found!"
    exit 1
fi