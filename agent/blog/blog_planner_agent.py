import json
from typing import Dict
from util.time_exe import time_execution
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class BlogPlannerAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_blog_planner_prompt)
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

    @time_execution        
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:

            # Call the LLM to generate a plan.
            print(f"{BlogPlannerAgent.__name__} : calling LLM to generate a plan...")
            plan = self.call_llm(user_query)

            if "thought" in plan:
                print("My next plan of action is: ", plan["thought"])             

            return plan["sections"]
        
        except Exception as e:
            print(f'Exception in {BlogPlannerAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"

    def create_blog_planner_prompt(self) -> str:
        """Create the system prompt for the blog planning AI with strict structure and instructions."""

        blog_structure = {
            "Introduction": {
                "Description": "This section must start with ### Key Links, include user-provided links, provide a brief overview of the problem statement, and briefly introduce the solution or main topic. It must not exceed 100 words.",
                "Content": "Leave blank for now",
                "Type": "Introduction"
            },
            "Main Body": [
                {
                    "Name": "Section 1 - Topic Name",
                    "Description": "This section should cover a distinct aspect of the main topic. It must include at least one relevant code snippet, be 150-200 words, and avoid overlapping with other sections.",
                    "Content": "Leave blank for now",
                    "Type": "Main Body"
                },
                {
                    "Name": "Section 2 - Topic Name",
                    "Description": "This section should cover another distinct aspect of the main topic. It must include at least one relevant code snippet, be 150-200 words, and avoid overlapping with other sections.",
                    "Content": "Leave blank for now",
                    "Type": "Main Body"
                },
                {
                    "Name": "Section 3 - Topic Name",
                    "Description": "This optional section can cover a third distinct aspect of the main topic. It must include at least one relevant code snippet, be 150-200 words, and avoid overlapping with other sections.",
                    "Content": "Leave blank for now",
                    "Type": "Main Body"
                }
            ],
            "Conclusion": {
                "Description": "This section must provide a brief summary of key points, include ### Key Links, and end with a clear call to action. It must not exceed 150 words.",
                "Content": "Leave blank for now",
                "Type": "Conclusion"
            }
        }

        blog_structure_json = {
            "role": "Blog Planning AI",
            "capabilities": [
                "Organizing user-provided notes into a blog outline",
                "Following a strict three-part blog structure with clear instructions",
                "Ensuring non-overlapping, concise, and well-structured sections",
                "Including specific details such as code snippets and clear calls to action"
                "Planning efficient flow of blog creation sequences"
            ],
            "instructions": [
                "Reflect carefully on the user-provided scope notes and instructions.",
                "Organize these into sections strictly following the blog structure.",
                "Provide detailed descriptions for each section, ensuring clarity and scope without overlap.",
                "Leave 'Content' blank for now, focusing on the planning stage.",
                "Plan blog creation sequences efficiently so that it can be populated parallelly."
            ],
            "blog_structure": blog_structure,
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
                    "sections": {
                        "type": "array",
                        "items": {
                            "name": {
                                "type": "string",
                                "description": "Section name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the section's scope, topics to cover, word count, and whether it includes code examples"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the section",
                                "optional": True
                            },
                            "type": {
                                "type": "string",
                                "description": "Whether this section is an Introduction, Main Body, or Conclusion"
                            }
                        }
                    },
                    "final_check": {
                        "type": "boolean",
                        "description": "Whether the sections follow the blog structure and instructions exactly"
                    }
                },
                "examples": [
                    {
                        "user": "Write me a blog about advent of agents",
                        "response": {
                            "thought": "Write a blog about advent of agents",
                            "plan": [
                                        "Use LLM to identify all the different sections to write.",
                                        "Use Sub Agents to write a details writeup for each section.",
                                        "Return the conversation result"
                                    ],
                            "sections": [
                                {
                                    "name": "Introduction",
                                    "description": "Start with ### Key Links and provide an overview of the problem and solution (max 100 words).",
                                    "content": "",
                                    "type": "Introduction"
                                },
                                {
                                    "name": "Section 1 - Overview of X",
                                    "description": "Discuss the background and basics of X with one code snippet, 150-200 words.",
                                    "content": "",
                                    "type": "Main Body"
                                },
                                {
                                    "name": "Conclusion",
                                    "description": "Summarize the blog, include ### Key Links, and provide a call to action (max 150 words).",
                                    "content": "",
                                    "type": "Conclusion"
                                }
                            ]
                        },
                        "final_check": True
                    }
                ]
            }
        }

        return f"""You are a Blog Planning AI that helps users create a concise outline for their blog posts.
    Strictly follow the blog structure and instructions provided.
    Configuration and expected output are provided in JSON format below:

    {json.dumps(blog_structure_json, indent=2)}

    Always respond with a JSON object following the response_format schema above.
    Ensure that the outline strictly adheres to the provided blog structure."""