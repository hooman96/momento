FROM node:20.9.0-alpine

WORKDIR /app

COPY package.json ./

RUN npm install --omit=dev

COPY server.js ./

RUN mkdir -p /app/data

ENV PORT = 3001

EXPOSE 3001

CMD ["node", "server.js"]
