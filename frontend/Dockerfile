FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* ./
RUN npm install --legacy-peer-deps

COPY . .

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
