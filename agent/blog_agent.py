import json
from typing import Dict
from agent.tool.tool_registry import Tool
from llm.bak.genaiclient import GenAIClient, ChatClient

class BlogAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False, process_multi_tool = True):
        """Initialize Agent with empty tool registry."""
        self.llamaclient = GenAIClient(base_url=base_url, model=model, temperature=temperature, stream=stream)
        self.client = ChatClient(self.llamaclient)
        self.process_multi_tool = process_multi_tool
        self.tools: Dict[str, Tool] = {}
        
    def add_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent."""
        self.llamaclient.add_tool(tool)


    def first_plan(self, user_query: str) -> Dict:
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
        
    def subsequent_plan(self, messages) -> Dict:
        """Use LLM to create a plan for tool usage."""        
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

            # Generate a plan using the LLM
            print("Calling LLM with the user query: ", user_query)
            plan = self.first_plan(user_query)
            while True:

                if "thought" in plan:
                    print("My next plan of action is: ", plan["thought"])

                if "direct_response" in plan or not plan.get("requires_tools", True):
                    # If no tools are required, capture the direct response and exit
                    print("No tools required and here is the final answer: " + str(plan["direct_response"]))
                    return plan["direct_response"]
                    

                # If tools are required, execute the tool calls sequentially (as of now call only for the first tool 
                # and exist incase input of this tool response is required for the next tool call)
                for tool_call in plan["tool_calls"]:
                    tool_name = tool_call["tool"]
                    tool_args = tool_call["args"]
                    print("Calling tool: " + str(tool_name) + " with args: " + str(tool_args))
                    
                    # Execute the tool with its arguments
                    tool_response = self.llamaclient.use_tool(tool_name, **tool_args)         
                    
                    print("Response from tool call: " + str(tool_response))   

                    # If multiple tool calls are required, update the query for the next tool call
                    if self.process_multi_tool:
                        # Update the query for the next tool or LLM call
                        messages = [
                            {"role": "user", "content": user_query},
                            {"role": "assistant", "content":  plan['thought']},
                            {"role": "tool", "content":  tool_response}
                        ]
            
                        # Re-plan using the updated input
                        plan = self.subsequent_plan(messages)
                        break;
                   
                     # If multiple tool calls are not required, return the response from tool
                    else:
                        return tool_response
            
        except Exception as e:
            return f"Error executing plan: {str(e)}"


#     def execute(self, user_query: str) -> str:
#         """Execute the full pipeline: plan and execute tools."""
#         try:
#             plan = self.plan(user_query)    
#             # print(plan)        
            
#             if not plan.get("requires_tools", True):
#                 return plan["direct_response"]
            
#             # Execute each tool in sequence
#             results = []
#             for tool_call in plan["tool_calls"]:
#                 tool_name = tool_call["tool"]
#                 tool_args = tool_call["args"]
#                 result = self.llamaclient.use_tool(tool_name, **tool_args)
#                 results.append(result)
            
#             # Combine results
#             return f"""Thought: {plan['thought']}
# Plan: {'. '.join(plan['plan'])}
# Results: {'. '.join(results)}"""
            
#         except Exception as e:
#             return f"Error executing plan: {str(e)}"