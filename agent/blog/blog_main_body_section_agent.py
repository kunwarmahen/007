import json
from typing import Dict
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class BlogMainBodySectionAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_section_writer_prompt)
        self.client = ChatClient(self.llamaclient)
        

    def call_llm(self, user_query: str) -> Dict:
        """Call the LLM to generate a response."""

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
        
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:

            # Call the LLM to generate a main body section.
            print(f"{BlogMainBodySectionAgent.__name__} : calling LLM to generate a main body section...")            
            main_body = self.call_llm(user_query)

            if "thought" in main_body:
                print("My next plan of action is: ", main_body["thought"])

            return {"heading": main_body["section_heading"], "body": main_body["section_body"], "code": main_body["code_example"]}
        
        except Exception as e:
            print(f'Exception in {BlogMainBodySectionAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"

    def create_section_writer_prompt(self) -> str:
        """Create the system prompt for the Section Writer AI to craft a detailed blog section."""
        section_writer_instructions = {
            "role": "Section Writer AI",
            "capabilities": [
                "Crafting detailed blog sections based on specific descriptions",
                "Adhering to strict formatting and writing guidelines",
            ],
            "instructions": [
                "Use the Section Name and Description as your primary focus.",
                "Format content using json for technical readability.",
                "Write precisely and avoid any introductory or marketing language.",
            ],
            "writing_guidelines": {
                "style_requirements": [
                    "Use technical and precise language.",
                    "Employ active voice.",
                    "Avoid all marketing or promotional language."
                ],
                "format": [
                    "## for section heading",
                    "``` for code blocks",
                    "** for emphasis when necessary",
                    "- for bullet points as needed"
                ],
                "grounding": [
                    "Do not make assumption."                    
                ]
            },
            "quality_checklist": [
                "Meets word count as specified in the Section Description.",
                "Includes at least one clear code example if required in the Section Description.",
                "Uses proper json formatting."
            ],
            "response_format": {
                "type": "json",
                "schema": {
                    "thought": {
                        "type": "string", 
                        "description": "reasoning about how to solve the task",
                        "optional": True
                    },
                    "plan": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "steps to solve the task",
                        "optional": True
                    },                     
                    "section_heading": {
                        "type": "string",
                        "description": "The section heading formatted using ##"
                    },
                    "section_body": {
                        "type": "string",
                        "description": "Detailed content of the section, formatted according to guidelines"
                    },
                    "code_example": {
                        "type": "string",
                        "description": "Code block content, enclosed in triple backticks",
                        "optional": True
                    },
                    "missing_information": {
                        "type": "boolean",
                        "description": "True if necessary information is not present in source URLs"
                    }
                },
                "examples": [
                    {
                        "thought": "Elborate on the main body section of the blog",
                        "plan": [
                                    "Use LLM to write section heading, section body and code example for the section",
                                    "Return the conversation result"
                                ],                        
                        "section_heading": "## Understanding X in Technical Detail",
                        "section_body": """
    X is a critical aspect of Y because:
    - It simplifies processes by [explanation].
    - It improves performance by [specific details].

    Key features include:
    - Feature 1: Explanation
    - Feature 2: Explanation
    """,
                        "code_example": "```python\n# Example code for implementing X\nprint('Hello, X!')\n```",
                        "missing_information": False
                    },                    
                ]
            }
        }

        return f"""You are a Section Writer AI tasked with crafting a precise and technically accurate section of a blog post.
    Follow the instructions and guidelines strictly to ensure high-quality content.
    Configuration, guidelines, and response format are provided below:

    {json.dumps(section_writer_instructions, indent=2)}

    Always respond with a JSON object following the response_format schema above."""
