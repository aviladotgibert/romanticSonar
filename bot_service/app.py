from flask import Flask, request, jsonify, session
from flask_cors import CORS
from romantic_bot import RomanticBot
import uuid
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sonar-secret-key-change-in-production')
CORS(app)

bot = RomanticBot()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'sonar-bot'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Mensaje no proporcionado'}), 400
        
        user_message = data['message']
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        response = bot.chat(user_id, user_message)
        
        return jsonify({
            'response': response,
            'user_id': user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id no encontrado'}), 400
        
        limit = int(request.args.get('limit', 20))
        history_data = bot.memory.get_conversation_history(user_id, limit)
        
        return jsonify({
            'user_id': user_id,
            'history': [
                {
                    'user': msg[0],
                    'bot': msg[1],
                    'timestamp': str(msg[2]),
                    'emotion': msg[3] if len(msg) > 3 else None
                }
                for msg in history_data
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
def get_profile():
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id no encontrado'}), 400
        
        profile = bot.memory.get_user_profile(user_id)
        
        if not profile:
            return jsonify({'message': 'Perfil no encontrado'}), 404
        
        return jsonify({
            'user_id': profile[0],
            'name': profile[1],
            'preferences': profile[2],
            'relationship_stage': profile[3],
            'important_dates': profile[4],
            'first_interaction': str(profile[5]),
            'last_interaction': str(profile[6]),
            'total_messages': profile[7]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id no encontrado'}), 400
        
        allowed_fields = ['name', 'relationship_stage']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            bot.memory.update_user_profile(user_id, **update_data)
            return jsonify({'message': 'Perfil actualizado', 'user_id': user_id}), 200
        else:
            return jsonify({'error': 'No hay campos válidos para actualizar'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id no encontrado'}), 400
        
        stats_data = bot.get_stats(user_id)
        
        return jsonify({
            'user_id': user_id,
            'total_messages': stats_data[0],
            'first_interaction': str(stats_data[1]) if stats_data[1] else None,
            'last_interaction': str(stats_data[2]) if stats_data[2] else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memories', methods=['GET'])
def get_memories():
    try:
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id no encontrado'}), 400
        
        limit = int(request.args.get('limit', 5))
        memories = bot.memory.get_important_memories(user_id, limit)
        
        return jsonify({
            'user_id': user_id,
            'memories': [
                {
                    'type': mem[0],
                    'content': mem[1],
                    'timestamp': str(mem[2])
                }
                for mem in memories
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Sonar Bot Service...")
    print(f"📍 Ollama URL: {os.getenv('OLLAMA_URL', 'http://ollama:11434')}")
    print(f"💾 Database: {os.getenv('DATABASE_PATH', '/app/data/romantic_bot.db')}")
    app.run(host='0.0.0.0', port=5000, debug=False)