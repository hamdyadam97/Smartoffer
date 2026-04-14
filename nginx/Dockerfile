# Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Build frontend
COPY frontend/ ./
RUN npm run build

# Final nginx image
FROM nginx:alpine

# Copy nginx config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend build
COPY --from=frontend-builder /app/dist /var/www/html

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
