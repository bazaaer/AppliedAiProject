# Use the official Nginx image as the base
FROM nginx:latest

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend files to Nginx web root
COPY ./index.html /usr/share/nginx/html/index.html
COPY ./style.css /usr/share/nginx/html/style.css
COPY ./script.js /usr/share/nginx/html/script.js

# Copy Swagger UI files to a subdirectory in Nginx web root
COPY ./swagger-ui /usr/share/nginx/html/api/docs

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
