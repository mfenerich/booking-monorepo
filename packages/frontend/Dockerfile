# Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

# Copy workspace-level files so that Nx can initialize
COPY package.json package-lock.json nx.json ./
RUN npm install

# Copy the entire repository
COPY . .

# Set environment variable so that the development server binds to 0.0.0.0
ENV HOST=0.0.0.0

# Expose port 3000
EXPOSE 3000

# Use Nx to serve your app on port 3000 and bind to 0.0.0.0
CMD ["npx", "nx", "serve", "stay-booker-pro", "--host", "0.0.0.0", "--port", "3000"]
