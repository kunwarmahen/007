import requests
import json

class BaseGenAIClient:
    def __init__(self, base_url, model, temperature=0.0, stream = True):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.stream = stream
        

    def send_request(self, endpoint, payload, headers=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {'Content-Type': 'application/json', 'Accept': 'application/json'}
        payload['model'] = self.model  # Automatically include model
        payload['temperature'] = self.temperature  # Automatically include temperature
        payload['stream'] = self.stream  # Automatically include temperature
        
        system_prompt = {"role": "system", "content": self.create_system_prompt()}
        # print(payload)
        payload['messages'].insert(0,system_prompt)   # Automatically include system message at the top

        # print(payload)
        # Send request to LLM
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload)
        )
        # print(response.json())
        return response

    

class ChatClient:
    def __init__(self, chat_handler, endpoint = "/api/chat"):
        self.chat_handler  = chat_handler
        self.endpoint  = endpoint
        self.client = chat_handler


    def chat(self, message):
        payload = {"messages": message}
        response = self.client.send_request(self.endpoint, payload)
        return response