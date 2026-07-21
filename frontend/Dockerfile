# Estágio 1: Build do Frontend
FROM node:22-alpine AS build

WORKDIR /app

# Copia dependências (o contexto é a raiz do projeto)
COPY frontend/package*.json ./

# npm install é mais tolerante a desvios no lockfile do que o npm ci
RUN npm install

# Copia o restante e constrói
COPY frontend/ ./
RUN npm run build

# Estágio 2: Nginx
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copia configuração customizada a partir da pasta nginx/
COPY nginx/nginx.conf /etc/nginx/conf.d/

# Copia arquivos construídos
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
