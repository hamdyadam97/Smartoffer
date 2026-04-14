FROM nginx:alpine

# Copy nginx config
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy pre-built frontend
COPY frontend/dist /var/www/html

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
