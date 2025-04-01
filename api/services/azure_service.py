# api/services/azure_service.py
import os
from openai import AzureOpenAI
from ..database import ChatDatabase

import dotenv
dotenv.load_dotenv()

class AzureChatService:
    def __init__(self):
        # Azure configuration
        self.endpoint = os.getenv("ENDPOINT_URL", "https://yash-baka.openai.azure.com/")  
        self.deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")  
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "FKE5wzlZratl1se3AIwdTpcwWb7Tschna8HYdQyGKce8AZM2RA1YJQQJ99BCACYeBjFXJ3w3AAABACOGRgBh")  
        self.api_version = "2024-05-01-preview"
        
        # Initialize Azure client with API key
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,  # Use API key instead
            api_version=self.api_version
        )
        
        # Database connection
        self.db = ChatDatabase()

        # System prompt for mental health support
        self.system_prompt = {
            "role": "system",
            "content": """
            You are a compassionate mental health assistant. Follow these guidelines:
            1. Use active listening techniques
            2. Avoid making diagnoses
            3. Suggest professional help when needed
            4. Keep responses concise and supportive
            5. Remember user's name and previous interactions
            """
        }

    def generate_response(self, session_id: str, user_message: str) -> str:
        # Get conversation history (last 5 messages)
        history = self.db.get_history(session_id, limit=5)
        
        # Build message list with system prompt and history
        messages = [self.system_prompt] + history + [{"role": "user", "content": user_message}]

        # Generate response from Azure OpenAI
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95
        )
        
        # Save both user and assistant messages
        assistant_response = response.choices[0].message.content
        self.db.add_message(session_id, "user", user_message)
        self.db.add_message(session_id, "assistant", assistant_response)
        
        return assistant_response
