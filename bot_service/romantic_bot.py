import requests
import json
import os
import re
from database import ConversationMemory

class RomanticBot:
    def __init__(self, ollama_url=None, model="sonar"):
        self.ollama_url = ollama_url or os.getenv('OLLAMA_URL', 'http://ollama:11434')
        self.memory = ConversationMemory()
        self.model = model
    
    def build_context_prompt(self, user_id):
        """Construye contexto adicional basado en memoria"""
        profile = self.memory.get_user_profile(user_id)
        history = self.memory.get_conversation_history(user_id, limit=5)
        memories = self.memory.get_important_memories(user_id, limit=3)
        
        context_parts = []
        
        # Información del perfil
        if profile and profile[1]:
            context_parts.append(f"El nombre de tu novio es {profile[1]}.")
        
        if profile and profile[3]:
            stages = {
                'getting_to_know': 'Están conociéndose, mantén un tono dulce pero algo reservado',
                'dating': 'Ya son pareja, puedes ser más cariñoso y cercano',
                'committed': 'Tienen una relación establecida, sé íntimo y profundo'
            }
            stage_text = stages.get(profile[3], '')
            if stage_text:
                context_parts.append(stage_text)
        
        # Recuerdos importantes
        if memories:
            context_parts.append("Cosas importantes que recuerdas:")
            for mem_type, content, timestamp in memories:
                context_parts.append(f"- {content}")
        
        # Historial reciente
        if history and len(history) > 0:
            context_parts.append("\nÚltimas conversaciones:")
            for user_msg, bot_msg, timestamp, emotion in history[-3:]:
                context_parts.append(f"Él dijo: {user_msg}")
                context_parts.append(f"Tú respondiste: {bot_msg}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def extract_user_info(self, user_message):
        """Extrae información del usuario"""
        info = {}
        message_lower = user_message.lower()
        
        # Detectar nombre
        name_patterns = [
            r'me llamo (\w+)',
            r'mi nombre es (\w+)',
            r'soy (\w+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                info['name'] = match.group(1).capitalize()
                break
        
        # Detectar momentos importantes
        if any(word in message_lower for word in ['cumpleaños', 'aniversario', 'graduación']):
            self.memory.add_memory(
                user_id='temp',
                memory_type='important_date',
                content=user_message,
                importance=8
            )
        
        return info
    
    def chat(self, user_id, user_message):
        """Envía mensaje y obtiene respuesta con contexto"""
        context = self.build_context_prompt(user_id)
        
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"CONTEXTO DE LA RELACIÓN:\n{context}\n\nUsa esta información para personalizar tu respuesta."
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            
            bot_response = response.json()['message']['content']
            
            # Extraer y guardar información
            user_info = self.extract_user_info(user_message)
            if user_info:
                self.memory.update_user_profile(user_id, **user_info)
            
            self.memory.save_interaction(
                user_id=user_id,
                user_message=user_message,
                bot_response=bot_response,
                context={'has_context': bool(context)}
            )
            
            return bot_response
            
        except requests.exceptions.RequestException as e:
            return f"❌ No pude conectarme con Sonar: {str(e)}"
        except Exception as e:
            return f"❌ Error inesperado: {str(e)}"
    
    def get_stats(self, user_id):
        return self.memory.get_stats(user_id)
    
    def update_relationship_stage(self, user_id, stage):
        valid_stages = ['getting_to_know', 'dating', 'committed']
        if stage in valid_stages:
            self.memory.update_user_profile(user_id, relationship_stage=stage)