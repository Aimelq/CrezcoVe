# Stage de desarrollo
FROM node:18-alpine AS development

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Exponer puerto de Vite
EXPOSE 3000

# Comando de desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage de build
FROM node:18-alpine AS build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Stage de producción con nginx
FROM nginx:alpine AS production

# Copiar build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

