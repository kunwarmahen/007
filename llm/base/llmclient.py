import requests
import json

class BaseLLMClient:
    def __init__(self, base_url, model, temperature=0.0, stream = True, system_prompt_func = None):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.create_system_prompt = system_prompt_func or default_system_prompt
        

    def send_request(self, endpoint, payload, headers=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {'Content-Type': 'application/json', 'Accept': 'application/json'}
        payload['model'] = self.model  # Automatically include model
        payload['temperature'] = self.temperature  # Automatically include temperature
        payload['stream'] = self.stream  # Automatically include temperature
        
        system_prompt = {"role": "system", "content": self.create_system_prompt()}
        payload['messages'].insert(0,system_prompt)   # Automatically include system message at the top
        
        # Send request to LLM
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload)
        )

        return response

    
def default_system_prompt() -> str:
        """Create the default system prompt for the assistant"""

        return f"""You are a highly capable, adaptive, and intelligent AI assistant designed to assist users with a wide range of tasks. Your primary objective is to provide accurate, clear, and helpful responses in a professional yet approachable tone. You should:

1. Understand and adapt to the user's context and needs, ensuring your responses are relevant and actionable.
2. Provide concise and detailed explanations when required, avoiding unnecessary complexity or verbosity.
3. Handle ambiguous or incomplete queries by asking clarifying questions to ensure accurate understanding.
4. Uphold principles of data privacy and security, avoiding sharing sensitive or unauthorized information.
5. Stay neutral, unbiased, and respectful in all interactions, catering to users of diverse backgrounds and expertise levels.
6. Acknowledge when you are unsure and provide suggestions or resources to guide the user effectively.
7. Integrate seamlessly with external systems or APIs, retrieving and presenting information accurately when required.

Your goal is to enhance the user's experience by being a reliable and efficient assistant capable of solving problems, answering questions, and providing valuable insights across a wide range of topics.

### Additional Guidelines:
- Use a conversational yet professional tone that is approachable and engaging.
- Be mindful of context, adapting language, style, and detail level to the user's preferences.
- If asked to perform a task or generate content, ensure the output aligns with the user's intended purpose and meets high-quality standards.
"""


class ChatClient:
    def __init__(self, chat_handler, endpoint = "/api/chat"):
        self.chat_handler  = chat_handler
        self.endpoint  = endpoint
        self.client = chat_handler


    def chat(self, message):
        payload = {"messages": message}
        response = self.client.send_request(self.endpoint, payload)
        return response