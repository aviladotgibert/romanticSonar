#!/bin/bash

echo "======================================"
echo "  Deteniendo y limpiando Sonar Bot"
echo "======================================"

# Parar servicios docker-compose
echo "Deteniendo contenedores Docker..."
docker-compose down

# Eliminar contenedores específicos si siguen existiendo
echo "Eliminando contenedores de Ollama y Sonar si existen..."
docker rm -f ollama_sonar 2>/dev/null
docker rm -f sonar_telegram_bot 2>/dev/null
docker rm -f sonar_api 2>/dev/null
docker rm -f sonar_bot_service 2>/dev/null

# Eliminar imagen del modelo Sonar en Ollama
echo "Eliminando modelo personalizado de Ollama..."
docker exec ollama_sonar ollama delete sonar 2>/dev/null

# Eliminar imágenes (opcional)
echo "Eliminando imágenes de Docker relacionadas..."
docker rmi sonar_telegram_bot 2>/dev/null
docker rmi sonar_api 2>/dev/null
docker rmi romantic_bot-bot-service 2>/dev/null
docker rmi romantic-bot-telegram-bot 2>/dev/null

# Limpieza de volúmenes (opcional, descomenta si quieres borrar TODO)
echo "Eliminando volúmenes..."
docker volume prune -f

echo ""
echo " Limpieza completada."
echo "======================================"
echo " Servicios detenidos y recursos eliminados."
echo ""