# Build stage
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
COPY nx.json ./
COPY packages/frontend/package.json ./packages/frontend/
RUN npm install

# Copy all files
COPY . .

# Build the frontend
RUN npx nx build stay-booker-pro --prod

# Production stage with Nginx
FROM nginx:alpine

# Copy the build output from the build stage
COPY --from=build /app/packages/frontend/build /usr/share/nginx/html

# Copy Nginx configuration
COPY packages/frontend/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]