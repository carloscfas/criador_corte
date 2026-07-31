#!/bin/bash

# Script para inicializar o banco de dados e rodar migrations

echo "Aguardando PostgreSQL estar pronto..."
until pg_isready -h postgres -U admin -d criador_cortes; do
  echo "PostgreSQL não está pronto ainda - aguardando..."
  sleep 2
done

echo "PostgreSQL está pronto!"

# Rodar migrations
echo "Rodando migrations do Alembic..."
alembic upgrade head

echo "Banco de dados inicializado com sucesso!"
