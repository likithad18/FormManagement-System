FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN rm -rf node_modules package-lock.json && npm install

COPY . .

RUN npm run build

# Install a simple static server for serving the build
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"] 