FROM node:18 AS build

# Set working directory for frontend
WORKDIR /app

# Copy package files
COPY ./frontend/package.json ./frontend/package-lock.json* ./

# Install dependencies (with legacy peer deps for compatibility)
RUN npm install --legacy-peer-deps

# Copy frontend source code
COPY ./frontend/ ./

# Copy bootstrap localization script
COPY ./docker/frontend/localize-bootstrap.sh ./localize-bootstrap.sh

# Modify angular.json to increase budget limits
RUN sed -i 's/"maximumError": "1mb"/"maximumError": "5mb"/g' angular.json && \
    sed -i 's/"maximumWarning": "500kb"/"maximumWarning": "2mb"/g' angular.json

# Update environment.ts (development) to use API proxy
RUN echo 'export const environment = { production: false, apiUrl: "/api" };' > ./src/environments/environment.ts

# Run script to localize Bootstrap files
RUN ./localize-bootstrap.sh

# Build the frontend with higher memory allocation in development mode
RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build -- --configuration=development

# Use nginx as the web server for production
FROM nginx:1.25-alpine

# Copy the built frontend from the builder stage - corrected path to copy from the chakra-frontend subdirectory
COPY --from=build /app/dist/chakra-frontend/ /usr/share/nginx/html

# Copy nginx configuration
COPY ./docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:80/ || exit 1

# Expose port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]