#!/bin/bash

echo " Inicializando Sonar - Romantic Bot"
echo "======================================"

# Crear estructura de directorios
echo " Creando estructura de directorios..."
mkdir -p bot_service data

# Levantar servicios
echo " Levantando servicios Docker..."
docker-compose up -d

# Esperar a que Ollama esté listo
echo " Esperando a que Ollama esté listo..."
sleep 15

# Descargar modelo base si no existe
echo " Verificando modelo base..."
docker exec ollama_sonar ollama pull llama3.2:1b

# Crear modelo personalizado
echo " Creando modelo personalizado 'Sonar'..."
docker exec ollama_sonar ollama create sonar -f /tmp/Modelfile

echo ""
echo " Sonar Bot está listo!"
echo "======================================"
echo " API disponible en: http://localhost:5000"
echo " Ollama disponible en: http://localhost:11434"
echo " Base de datos en: ./data/romantic_bot.db"
echo ""
echo "Prueba el bot con:"
echo "curl -X POST http://localhost:5000/chat \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Hola amor\", \"user_id\": \"test_user\"}'"
echo ""