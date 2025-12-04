import requests
import json

class SonarClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.user_id = "test_user_python"
    
    def chat(self, message):
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": message, "user_id": self.user_id}
        )
        return response.json()
    
    def get_history(self, limit=10):
        response = requests.get(
            f"{self.base_url}/history",
            params={"user_id": self.user_id, "limit": limit}
        )
        return response.json()
    
    def get_profile(self):
        response = requests.get(
            f"{self.base_url}/profile",
            params={"user_id": self.user_id}
        )
        return response.json()

# Uso
if __name__ == "__main__":
    client = SonarClient()
    
    print("Cliente de Sonar iniciado\n")
    
    while True:
        message = input("Tú: ")
        if message.lower() in ['salir', 'exit']:
            break
        
        response = client.chat(message)
        print(f"Sonar: {response['response']}\n")