# Build the Angular app
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --prod

# Serve the app using NGINX
FROM nginx:alpine
COPY --from=build /app/dist/frontend-rag-deep-learning-chatbot/usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the default NGINX port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
