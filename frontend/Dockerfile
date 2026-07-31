FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package.json ./

# Instalar dependências
RUN npm install

# Copiar código
COPY . .

# Expor porta
EXPOSE 5173

# Comando para rodar em desenvolvimento
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
