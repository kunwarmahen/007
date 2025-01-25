import json
from typing import Dict
from util.time_exe import time_execution
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class InteractiveAgent():
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_system_prompt)
        self.client = ChatClient(self.llamaclient)
        
    def call_llm(self, user_query: str) -> Dict:
        """Use LLM to create a plan for tool usage."""
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
            raise ValueError("Failed to parse LLM response as JSON")

    @time_execution                
    def execute(self, user_query: str) -> str:
        """
        Execute the agent's pipeline. If clarification is needed, ask the user.
        """
        try:
            # Invoke agent to answer user question
            print(f"{InteractiveAgent.__name__} : calling LLM to answer user question...")
            response = self.call_llm(user_query)

            if "thought" in response:
                print("My plan of action is: ", response["thought"])

            if "clarification_needed" in response and response["clarification_needed"]:
                question_to_user = response.get("clarification_question", "Could you provide more details?")
                print("I need more information: ", question_to_user)
                user_input = input("User: ")  # Get user input for clarification
                return self.execute(user_query + ". Response from user: " + user_input)
            else:
                # Check if the response requires user interaction
                if "direct_response" in response:
                    return response["direct_response"]

        except Exception as e:
            print(f'Exception in {InteractiveAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"

        return "Unable to process the query."

    def create_system_prompt(self) -> str:
        """
        Extend the system prompt to include the ability to handle incomplete queries.
        """
        info_json = {
            "role": "Interactive AI Assistant",
            "capabilities": [
                "Responding directly to the question asked by the user",
                "Asking for clarification only when the query is ambiguous or incomplete",
            ],
            "instructions": [
                "If a query can be answered directly, respond with a detailed message without requesting clarification.",
                "If the query is unclear or more information is required, set 'clarification_needed' to true and provide a 'clarification_question'."
            ],
            "response_format": {
                "type": "json",
                "schema": {
                    "direct_response": {
                        "type": "string",
                        "description": "response for the question asked",
                        "optional": True
                    },
                    "clarification_needed": {
                        "type": "boolean",
                        "description": "whether additional information is needed from the user",
                        "optional": True
                    },
                    "clarification_question": {
                        "type": "string",
                        "description": "specific question to ask the user for more details",
                        "optional": True
                    },
                    "thought": {
                        "type": "string", 
                        "description": "reasoning about how to solve the task if any",
                        "optional": True
                    },
                    "plan": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "steps to solve the task if any",
                        "optional": True
                    }                
                },
                "examples": [
                    {
                        "user": "What is the capital?",
                        "response": {
                            "clarification_needed": True,
                            "clarification_question": "Could you specify which country you are referring to?",                        
                            "thought": "The query is incomplete and lacks context about the country.",
                            "plan": [
                                "Ask the user for clarification."
                            ]
                        }
                    },
                    {
                        "user": "What is the capital of France?",
                        "response": {
                            "clarification_needed": False,
                            "thought": "The query is complete and I will respond to user query.",
                            "plan": [
                                "Response to user query."
                            ]
                        }
                    }           
                ]
            }
        }

        return f"""You are an AI assistant that helps users by providing direct answers or asking for clarification ONLY when needed.
Configuration, instructions, and available tools are provided in JSON format below:

{json.dumps(info_json, indent=2)}

Always respond with a JSON object following the response_format schema above. 
"""
