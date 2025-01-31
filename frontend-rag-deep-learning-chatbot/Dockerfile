FROM node:21

WORKDIR /workspace

COPY . .

RUN npm install -g @angular/cli

CMD ng serve --host 0.0.0.0 --port 4200

EXPOSE 4200
