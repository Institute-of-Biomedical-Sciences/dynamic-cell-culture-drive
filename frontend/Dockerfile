FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci  # Install ALL dependencies (including devDependencies for build)

COPY . .

RUN npm run build

EXPOSE 5173


RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "5173"]
