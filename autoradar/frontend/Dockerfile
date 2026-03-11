FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Build with backend URL for server-side rewrites
ENV NEXT_PUBLIC_API_URL=http://backend:8000
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
