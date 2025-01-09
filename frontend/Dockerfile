# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Next.js app
RUN npm run build

# Run stage
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy built application from the builder stage
COPY --from=builder /app/out /app/out
COPY --from=builder /app/ckeditor5_build /app/ckeditor5_build

# Expose the desired port (default: 3000)
EXPOSE 3000

# Command to serve the app using npx serve@latest
CMD ["npx", "serve@latest", "out"]
