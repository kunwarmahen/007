import json
from typing import Dict, List, Any
from util.time_exe import time_execution
from agent.tool.tool_registry import Tool, global_tool_registry
from llm.base.llmclient import BaseLLMClient
from llm.base.llmclient import ChatClient

class ToolAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False, process_multi_tool = True, load_default_tools = True):
        
        """Initialize Agent with a base url and model name and tool registry."""
        self.llamaclient = BaseLLMClient(base_url=base_url, model=model, temperature=temperature, stream=stream, system_prompt_func=self.create_system_prompt)
        self.client = ChatClient(self.llamaclient)
        self.process_multi_tool = process_multi_tool
        self.tools: Dict[str, Tool] = {}

        # Automatically load tools from the global registry
        if load_default_tools:
            self._load_tools()        
        
    def _load_tools(self) -> None:
            """Load tools from the global registry."""
            for name, func in global_tool_registry.items():
                self.add_tool(func)

    def add_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent."""
        self.tools[tool.name] = tool
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool descriptions."""
        return [f"{tool.name}: {tool.description}" for tool in self.tools.values()]
    
    def use_tool(self, tool_name: str, **kwargs: Any) -> str:
        """Execute a specific tool with given arguments."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")
        
        tool = self.tools[tool_name]
        return tool.func(**kwargs)
        
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
            print(json_response['message']['content'])
            raise ValueError("Failed to parse LLM response as JSON")
        
    def subsequent_llm_call(self, messages) -> Dict:
        """Use LLM to create a plan for tool usage."""        
        # Chat with the API
        response = self.client.chat(messages)        
        # Prepare the request to Ollama        
        json_response = response.json()
        
        try:
            return json.loads(json_response['message']['content'])
        except json.JSONDecodeError:
            print(json_response['message']['content'])
            raise ValueError("Failed to parse LLM response as JSON")        
   
    @time_execution   
    def execute(self, user_query: str) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:

            # Generate a plan using the LLM
            print(f"{ToolAgent.__name__} : calling LLM to identify which tool to use...")
            plan = self.call_llm(user_query)

            while True:

                if "thought" in plan:
                    print("My next plan of action is: ", plan["thought"])

                if "direct_response" in plan or not plan.get("requires_tools", True):
                    # If no tools are required, capture the direct response and exit
                    return plan["direct_response"]
                    

                # If tools are required, execute the tool calls sequentially (as of now call only for the first tool 
                # and exist incase input of this tool response is required for the next tool call)
                for tool_call in plan["tool_calls"]:
                    tool_name = tool_call["tool"]
                    tool_args = tool_call["args"]
                    print(f"Invoking tool: {str(tool_name)} with args: {str(tool_args)}")
                    
                    # Execute the tool with its arguments
                    tool_response = self.use_tool(tool_name, **tool_args)                             
                    print(f"Tool response: {str(tool_response)}")   

                    # If multiple tool calls are required, update the query for the next tool call
                    if self.process_multi_tool:
                        # Update the query for the next tool or LLM call
                        messages = [
                            {"role": "user", "content": user_query},
                            {"role": "assistant", "content":  plan['thought']},
                            {"role": "tool", "content":  tool_response}
                        ]
            
                        # Re-plan using the updated input
                        plan = self.subsequent_llm_call(messages)
                        break;
                   
                     # If multiple tool calls are not required, return the response from tool
                    else:
                        return tool_response
            
        except Exception as e:
            print(f'Exception in {ToolAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"

    def create_system_prompt(self) -> str:
        """Create the system prompt for the LLM with available tools."""
        tools_json = {
            "role": "AI Assistant",
            "capabilities": [
                "If provided tool response, uses it to respond directly to the orginal user question.",
                "Using provided tools to help users when necessary",
                "Responding directly without tools for questions that don't require tool usage",
                "Planning efficient tool usage sequences"
            ],
            "instructions": [
                "When you receive a tool response, use it to format an answer to the orginal user question, without using tools.",
                "Use tools only when they are necessary for the task",
                "If a query can be answered directly, respond with a simple message instead of using tools",
                "When tools are needed, plan their usage efficiently to minimize tool calls"
            ],
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        name: {
                            "type": info["type"],
                            "description": info["description"]
                        }
                        for name, info in tool.arguments.items()
                    }
                }
                for tool in self.tools.values()
            ],
            "response_format": {
                "type": "json",
                "schema": {
                    "requires_tools": {
                        "type": "boolean",
                        "description": "whether tools are needed for this query"
                    },
                    "thought": {
                        "type": "string", 
                        "description": "reasoning about how to solve the task (when tools are needed)",
                        "optional": True
                    },
                    "plan": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "steps to solve the task (when tools are needed)",
                        "optional": True
                    },
                    "direct_response": {
                        "type": "string",
                        "description": "final response if no tools are needs",
                        "optional": True
                    },
                    "tool_calls": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool": {
                                    "type": "string",
                                    "description": "name of the tool"
                                },
                                "args": {
                                    "type": "object",
                                    "description": "parameters for the tool"
                                }
                            }
                        },
                        "description": "tools to call in sequence (when tools are needed)",
                        "optional": True
                    }
                },
                "examples": [
                    {
                        "user": "Convert 100 USD to EUR",
                        "response": {
                            "requires_tools": True,
                            "thought": "I need to use the currency conversion tool to convert USD to EUR",
                            "plan": [
                                "Use convert_currency tool to convert 100 USD to EUR",
                                "Return the conversion result"
                            ],
                            "tool_calls": [
                                {
                                    "tool": "convert_currency",
                                    "args": {
                                        "amount": 100,
                                        "from_currency": "USD", 
                                        "to_currency": "EUR"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "user": "What's 500 Japanese Yen in British Pounds?",
                        "response": {
                            "requires_tools": True,
                            "thought": "I need to convert JPY to GBP using the currency converter",
                            "plan": [
                                "Use convert_currency tool to convert 500 JPY to GBP",
                                "Return the conversion result"
                            ],
                            "tool_calls": [
                                {
                                    "tool": "convert_currency",
                                    "args": {
                                        "amount": 500,
                                        "from_currency": "JPY",
                                        "to_currency": "GBP"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "user": "What's the current weather of New Delhi?",
                        "assitant": "I have determined that the city of New Delhi is located in the IN. Now, I need to use the current_weather tool to get the weather information for New Delhi, IN.",
                        "tool" : "IN",
                        "response": {
                            "requires_tools": False,
                            "direct_response": "The current weather in Cary is clear sky with a temperature of -2.24°C, humidity at 79%, and wind speed at 1.08 m/s."
                        }
                    },                    
                    {
                        "user": "What currency does Japan use?",
                        "response": {
                            "requires_tools": False,
                            "direct_response": "Japan uses the Japanese Yen (JPY) as its official currency. This is common knowledge that doesn't require using the currency conversion tool."
                        }
                    }
                ]
            }
        }
        
        return f"""You are an AI assistant that helps users by providing direct response or using tools when necessary.
When you receive a tool call response, use the output to format an answer to the orginal user question and return it as a direct response.
Configuration, instructions, and available tools are provided in JSON format below:

{json.dumps(tools_json, indent=2)}

Always respond with a JSON object following the response_format schema above. 
Remember to use tools only when they are absolutely needed to get more information about the user question."""

