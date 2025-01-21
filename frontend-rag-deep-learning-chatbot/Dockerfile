<<<<<<< HEAD
FROM node:21

WORKDIR /workspace

COPY . .

RUN npm install -g @angular/cli

CMD ng serve --host 0.0.0.0 --port 4200

EXPOSE 4200
=======
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
>>>>>>> 75c5e994b7317639cee2a4a86ff511554d89a42b
