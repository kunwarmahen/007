import json
from util.time_exe import time_execution
from agent.base.base_agent import BaseAgent

class GenericAgent(BaseAgent):
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent the agent."""
        super().__init__(base_url, model, temperature, stream, system_prompt_func=self.create_system_prompt)
   
    @time_execution   
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
       
        try:

            # Call the LLM to generate a response
            print(f"{GenericAgent.__name__} : calling LLM to answer user question...")
            response = self.call_llm(user_query)

            if "thought" in response:
                print("My plan of action is: ", response["thought"])

            if "direct_response" in response:
                return response["direct_response"]            
            
        except Exception as e:
            print(f'Exception in {GenericAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"
        
    def create_system_prompt(self) -> str:
            """Create the system prompt for the LLM with available tools."""
            
            info_json = {
                "role": "AI Assistant",
                "capabilities": [
                    "Responding directly to the question asked by the user",
                ],
                "instructions": [
                    "If a query can be answered directly, respond with a detailed message",
                ],
                "response_format": {
                    "type": "json",
                    "schema": {
                        "direct_response": {
                            "type": "string",
                            "description": "response for the question asked",
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
                            "user": "What currency does Japan use?",
                            "response": {
                                "direct_response": "Japan uses the Japanese Yen (JPY) as its official currency. This is common knowledge that doesn't require using the currency conversion tool.",
                                "thought": "I need to answer directly and no further action is needed",
                                "plan": [
                                        "Use LLM to answer user question",
                                        "Return the conversation result"
                                ]
                            }
                        }
                    ]
                }
            }
            
            return f"""You are an AI assistant that helps users by providing direct answers .
    Configuration, instructions, and available tools are provided in JSON format below:

    {json.dumps(info_json, indent=2)}

    Always respond with a JSON object following the response_format schema above. 
    """        