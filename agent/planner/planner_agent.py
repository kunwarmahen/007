import json
from typing import Dict
import util.utils as utils
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class PlannerAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        """Initialize Agent with a base url and model name."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_system_prompt)
        self.client = ChatClient(self.llamaclient)
    

    def identify_agent(self, user_query: str) -> Dict:
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
            
   
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
       
        try:

            # Identify which agent to invoke
            print(f"{PlannerAgent.__name__} : calling LLM to identify which agent to use...")
            reponse = self.identify_agent(user_query)

            if "thought" in reponse:
                print("My  plan of action is: ", reponse["thought"])

            if "requires_agents" in reponse and reponse["requires_agents"] and "selected_agents" in reponse:
                selected_agent = reponse["selected_agents"][0]
                
                if "sequence" in selected_agent and selected_agent["sequence"] and "sequence_order" in selected_agent:

                    agent_name = selected_agent["agent"]
                    agent_args = selected_agent["sequence_order"]
                    
                    # Execute the agent with its arguments
                    return utils.invoke_agent(str(agent_name), "execute", user_query, agent_args)

                elif "agent" in selected_agent:
                    agent_name = selected_agent["agent"]
                    
                    # Execute the agent with its arguments
                    return utils.invoke_agent(str(agent_name), "execute", user_query)                    
            
        except Exception as e:
            print(f'Exception in {PlannerAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"
            

    def create_system_prompt(self) -> str:
        """Create the system prompt for the planner agent to determine and delegate tasks to appropriate agents."""
        agents_json = {
            "role": "Planner Agent",
            "capabilities": [
                "Analyze user queries and determine the appropriate agent or sequence of agents to fulfill the query.",
                "Delegate tasks to specialized agents such as the ToolAgent, BlogAgent (BlogPlannerAgent, BlogMainBodySectionAgent, BlogIntroConclusionAgent), InteractiveAgent or GenericAgent.",
                "Plan and coordinate multi-step processes when needed, ensuring agents are called in the correct sequence."
            ],
            "instructions": [
                "Interpret the user's query and decide whether to delegate it to a specific agent or handle it using a sequence of agents.",
                "For blog-related queries, invoke the blog agent (BlogAgent) and suggest the sequence of agents to fulfill the query. blog planner agent (BlogPlannerAgent) first, followed by the main body writer (BlogMainBodySectionAgent), and conclude with the conclusion writer agent (BlogIntroConclusionAgent), in sequence.",
                "For queries requiring tools, forward the query to the tools agent (ToolAgent).",
                "For general or conversational queries, forward the query to the generic agent (GenericAgent).",
                "For questions if enough information is not provided and a clarification is needed, forward the query to the interactive agent (InteractiveAgent).",
                "Always provide a JSON response that specifies the selected agent(s) and any required arguments."
            ],
            "agents": [
                {
                    "name": "ToolAgent",
                    "description": "Handles queries requiring tools like currency conversion, weather updates, or specific calculations."
                },
                {
                    "name": "BlogAgent",
                    "description": "Handles blog writing queries in three steps: planning (BlogPlannerAgent), writing the main body (BlogMainBodySectionAgent), and concluding (BlogIntroConclusionAgent)."
                },
                {
                    "name": "GenericAgent",
                    "description": "Handles general user queries that don't require specialized tools or multi-step processes."
                },
                {
                    "name": "InteractiveAgent",
                    "description": "Handles general user queries and asks clarification questions to user ONLY when needed."
                }
            ],
            "response_format": {
                "type": "json",
                "schema": {
                    "requires_agents": {
                        "type": "boolean",
                        "description": "Whether agents are needed to fulfill the query."
                    },
                    "selected_agents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "agent": {
                                    "type": "string",
                                    "description": "Name of the agent to invoke."
                                },
                                "sequence": {
                                    "type": "boolean",
                                    "description": "Indicates if the agent is part of a sequence.",
                                    "optional": True
                                },
                                "sequence_order": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "stage": {
                                                "type": "string",
                                                "description": "Name of the sub agent to invoke."
                                            }
                                        }
                                    },
                                    "optional": True
                                },                                
                                "arguments": {
                                    "type": "object",
                                    "description": "Arguments or parameters required by the agent.",
                                    "optional": True
                                }
                            }
                        },
                        "description": "List of agents to call, optionally with sequences and arguments."
                    },
                    "thought": {
                        "type": "string",
                        "description": "Reasoning about the selection of agents or direct response.",
                        "optional": True
                    }
                },
                "examples": [
                    {
                        "user": "Write a blog on the benefits of AI.",
                        "response": {
                            "requires_agents": True,
                            "thought": "This query requires a blog to be written, so the blog agents will be invoked in sequence.",
                            "selected_agents": [
                                {"agent": "BlogAgent", "sequence": True, 
                                "sequence_order": [
                                    {"stage": "BlogPlannerAgent"},
                                    {"stage": "BlogMainBodySectionAgent"},
                                    {"stage": "BlogIntroConclusionAgent"}
                                ]
                                },                                
                            ]


                        }
                    },
                    {
                        "user": "What is 100 USD in EUR?",
                        "response": {
                            "requires_agents": True,
                            "thought": "This query requires currency conversion, so the tools agent will be invoked.",
                            "selected_agents": [
                                {"agent": "ToolsAgent", "arguments": {"task": "convert_currency", "amount": 100, "from_currency": "USD", "to_currency": "EUR"}}
                            ]
                        }
                    },
                    {
                        "user": "Tell me about the weather in Tokyo.",
                        "response": {
                            "requires_agents": True,
                            "thought": "This query requires weather information, so the tools agent will be used.",
                            "selected_agents": [
                                {"agent": "ToolsAgent", "arguments": {"task": "current_weather", "location": "Tokyo"}}
                            ]
                        }
                    },
                    {
                        "user": "What is AI?",
                        "response": {
                            "requires_agents": True,
                            "thought": "This query requires can be answered with the help of any specialed agent so will be delegated to GenericAgent.",
                            "selected_agents": [
                                {"agent": "GenericAgent", "arguments": {"query": "What is AI?"}}
                            ]
                        }
                    },
                    {
                        "user": "What is the capital?",
                        "response": {
                            "requires_agents": True,
                            "thought": "This query requires further clarification from the user  so will be delegated to InteractiveAgent.",
                            "selected_agents": [
                                {"agent": "InteractiveAgent", "arguments": {"query": "What is the capital?"}}
                            ]
                        }
                    }
                ]
            }
        }
        
        return f"""You are a planner agent responsible for analyzing user queries and delegating tasks to the appropriate agents. 
    Your goal is to ensure the user's query is fulfilled efficiently by selecting the correct agent or sequence of agents.
    Configuration, instructions, and available agents are provided in JSON format below:

    {json.dumps(agents_json, indent=2)}

    Always respond with a JSON object following the response_format schema above."""