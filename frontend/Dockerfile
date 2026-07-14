FROM node:20.11-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
