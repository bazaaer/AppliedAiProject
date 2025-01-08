# Use an official Node.js image to build the application
FROM node:18 AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json ./

# Install dependencies
RUN npm install

# Copy the entire application source code
COPY . ./

# Build the application
RUN npm run build --no-lint

# Use the official Nginx image as the base for serving the app
FROM nginx:latest

# Copy the exported static files to Nginx web root
COPY --from=builder /app/out /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
