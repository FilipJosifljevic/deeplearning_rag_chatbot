FROM node:21

WORKDIR /app

COPY . .

RUN npm install && npm run build --prod

FROM alpine:latest
WORKDIR /workspace
COPY --from=build /app/dist/frontend-rag-deep-learning-chatbot /workspace/dist
