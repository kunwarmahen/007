import json
from typing import Dict
from util.time_exe import time_execution
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class BlogConclusionAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_conclusion_prompt)
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
            return json.loads( json_response['message']['content'])
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")

    @time_execution        
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:

            # Call the LLM to generate a conclusion.
            print(f"{BlogConclusionAgent.__name__} : calling LLM to generate a conclusion...")
            conclusion = self.call_llm(user_query)

            if "thought" in conclusion:
                print("My next plan of action is: ", conclusion["thought"])

            return {"heading": conclusion["section_heading"], "body": conclusion["section_body"]}
        
        except Exception as e:
            print(f'Exception in {BlogConclusionAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"
        
    def create_conclusion_prompt(self) -> str:
        """Create the system prompt for the Conclusion Writer AI to craft blog sections."""
        conclusion_instructions = {
            "role": "Conclusion Writer AI",
            "capabilities": [
                "Crafting concise and technically accurate conclusions",
                "Referencing main body sections to provide context and flow",
                "Adhering to strict formatting and writing guidelines for these sections"
            ],
            "instructions": [
                "Use the Section Name and Description to guide your writing.",
                "Reference the main body sections for context and ensure logical flow.",
                "Follow distinct formatting and content requirements for conclusions."
            ],
            "writing_guidelines": {
                "style_requirements": [
                    "Use technical and precise language.",
                    "Employ active voice.",
                    "Avoid marketing or promotional language entirely."
                ],
                "section_specific_requirements": {
                    "FOR_CONCLUSION": [
                        "Use ## Conclusion as the heading.",
                        "Summarize key points from the main body sections in a crisp and clear manner (max 150 words).",
                        "Include a clear call to action for readers."
                    ]
                },
                "grounding": [
                        "Do not make assumption."   
                ]
            },
            "quality_checklist": [
                "Meets word count as specified for conclusion (150 words).",
                "Provides an accurate summary (for conclusion).",
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
                        "description": "The section heading formatted as # for conclusion"
                    },
                    "section_body": {
                        "type": "string",
                        "description": "Detailed content of the section, formatted according to guidelines"
                    },
                    "missing_information": {
                        "type": "boolean",
                        "description": "True if necessary information is not present in source URLs"
                    }
                },
                "examples": [
                    {
                        "thought": "Elborate on the conclusion section of the blog",
                        "plan": [
                                    "Use LLM to write section heading and section body for the conclusion",
                                    "Return the conversation result"
                                ],                        
                        "section_heading": "# Exploring the Power of X",
                        "section_body": """
    In the ever-evolving landscape of technology, X stands out as a critical innovation. 
    This blog delves into the challenges it addresses, from scalability to efficiency, and explores practical applications to implement X effectively.
    """,
                        "missing_information": False
                    },
                    {
                        "section_heading": "## Conclusion",
                        "section_body": """
    X offers transformative potential in addressing Y's challenges. 
    By leveraging its capabilities, businesses can achieve greater scalability, efficiency, and precision. 
    Explore this solution further and take the first step towards innovation.
    """,
                        "missing_information": False
                    }
                ]
            }
        }

        return f"""You are an Conclusion Writer AI tasked with crafting a precise and technically accurate conclusion for a blog post.
    Follow the instructions and guidelines strictly to ensure high-quality content.
    Configuration, guidelines, and response format are provided below:

    {json.dumps(conclusion_instructions, indent=2)}

    Always respond with a JSON object following the response_format schema above."""
