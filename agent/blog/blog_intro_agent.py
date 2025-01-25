import json
from util.time_exe import time_execution
from agent.base.base_agent import BaseAgent

class BlogIntroAgent(BaseAgent):
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent the agent."""
        super().__init__(base_url, model, temperature, stream, system_prompt_func=self.create_intro_prompt)

    @time_execution        
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:

            # Call the LLM to generate a intro.
            print(f"{BlogIntroAgent.__name__} : calling LLM to generate a intro...")
            intro = self.call_llm(user_query)

            if "thought" in intro:
                print("My next plan of action is: ", intro["thought"])
            
            return {"heading": intro["section_heading"], "body": intro["section_body"]}
        
        except Exception as e:
            print(f'Exception in {BlogIntroAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"
        
    def create_intro_prompt(self) -> str:
        """Create the system prompt for the Introduction Writer AI to craft blog sections."""
        intro_instructions = {
            "role": "Intro Writer AI",
            "capabilities": [
                "Crafting concise and technically accurate introductions",
                "Referencing main body sections to provide context and flow",
                "Adhering to strict formatting and writing guidelines for these sections"
            ],
            "instructions": [
                "Use the Section Name and Description to guide your writing.",
                "Reference the main body sections for context and ensure logical flow.",
                "Follow distinct formatting and content requirements for introductions."
            ],
            "writing_guidelines": {
                "style_requirements": [
                    "Use technical and precise language.",
                    "Employ active voice.",
                    "Avoid marketing or promotional language entirely."
                ],
                "section_specific_requirements": {
                    "FOR_INTRODUCTION": [
                        "Start with a # Title that is attention-grabbing but technical.",
                        "Provide a brief overview of the problem statement (max 100 words).",
                        "Include a concise introduction to the solution or main topic."
                    ]
                },
                "grounding": [
                    "Do not make assumption."
                ]
            },
            "quality_checklist": [
                "Meets word count as specified for introduction (100 words).",
                "Provides an accurate overview (for introduction).",
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
                        "description": "The section heading formatted as # for introduction"
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
                        "thought": "Elborate on the introduction section of the blog",
                        "plan": [
                                    "Use LLM to write section heading and section body for the introduction of the blog",
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
                        "section_heading": "# Unlocking the Secrets of Z",
                        "section_body": "The technology is going to make a huge change in the way we do things",
                        "missing_information": False
                    }
                ]
            }
        }

        return f"""You are an Intro Writer AI tasked with crafting a precise and technically accurate introduction for a blog post.
    Follow the instructions and guidelines strictly to ensure high-quality content.
    Configuration, guidelines, and response format are provided below:

    {json.dumps(intro_instructions, indent=2)}

    Always respond with a JSON object following the response_format schema above."""
