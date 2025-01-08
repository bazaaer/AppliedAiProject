# Stage 1: Build the React application
FROM node:18 AS build

WORKDIR /app
COPY . .
ENV NEXT_DISABLE_ESLINT=1
RUN npm install
RUN npm run build

# Stage 2: Serve the app with Nginx
FROM nginx:1.25

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
