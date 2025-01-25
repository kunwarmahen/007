import json
from typing import Dict
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class BaseAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False, system_prompt_func=None):
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=system_prompt_func)
        self.client = ChatClient(self.llamaclient)

    def call_llm(self, user_query: str) -> Dict:
        """Use LLM to generate a response."""

        messages = [
            {"role": "user", "content": user_query}
        ]
        
        # Chat with the API
        response = self.client.chat(messages)        
                
        # Prepare the request to Ollama        
        json_response = response.json()
        
        try:
            return json.loads(json_response['message']['content'])
        except json.JSONDecodeError:
            print(json_response['message']['content'])
            raise ValueError("Failed to parse LLM response as JSON")
                