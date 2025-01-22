import time
from agent.tool.tool_agent import ToolAgent
from agent.planner.planner_agent import PlannerAgent
from agent.generic.generic_agent import GenericAgent
from agent.interactive.interactive_agent import InteractiveAgent
from agent.blog.blog_agent import BlogAgent
from tool.tools import convert_currency, current_weather, country_for_city, get_current_location

def main(test_agent=None):
    
    if test_agent == "blog":

        agent = BlogAgent(model="qwen2.5:32b")
        query_list = ["Write a blog about advent of AI"]    
        
        for query in query_list:
            print(f"\nUser Query: {query}")
            start_time = time.time()
            response = agent.execute(query)
            end_time = time.time()            
            print(f"Response from the Agent after {end_time - start_time} secs: \n\n{response}")

    elif test_agent == "tool":
        
        agent = ToolAgent(model="qwen2.5:32b", load_default_tools=False)
        agent.add_tool(convert_currency)
        agent.add_tool(current_weather)
        agent.add_tool(country_for_city)
        agent.add_tool(get_current_location)        
        
        query_list = ["I am traveling to Japan from India, I have 1500 of local currency, how much of Japaese currency will I be able to get?", "How is the current weather?",
                      "How is the current weather at Boca Raton, Florida?","Tell me a joke?"]
        
        for query in query_list:
            print(f"\nUser Query: {query}")
            start_time = time.time()
            response = agent.execute(query)
            end_time = time.time()
            print(f"Response from the Agent after {end_time - start_time} secs: \n\n{response}")

    elif test_agent == "plan":

        agent = PlannerAgent(model="qwen2.5:32b")
        
        query_list = ["What is a capital", "Tell me a joke?", "How is the current weather at Boca Raton, Florida?", "Write a blog about advent of AI"]
        
        for query in query_list:
            print(f"\nUser Query: {query}")
            start_time = time.time()
            response = agent.execute(query)
            end_time = time.time()
            print(f"Response from the Agent after {end_time - start_time} secs: \n\n{response}")

    elif test_agent == "interactive":
        agent = InteractiveAgent(model="qwen2.5:32b")
        
        query_list = ["What is the capital of the United States?", "What is the capital of Florida?", "What is the capital?"]
    
        
        for query in query_list:
            print(f"\nUser Query: {query}")
            start_time = time.time()
            response = agent.execute(query)
            end_time = time.time()
            print(f"Response from the Agent after {end_time - start_time} secs: \n\n{response}")
    else:

        agent = GenericAgent(model="qwen2.5:32b")
        
        query_list = ["Tell me a sarcastic joke?"]
        
        for query in query_list:
            print(f"\nUser Query: {query}")
            start_time = time.time()
            response = agent.execute(query)
            end_time = time.time()
            print(f"Response from the Agent after {end_time - start_time} secs: \n\n{response}")

if __name__ == "__main__":
    
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1]) 
    else:
        main() 
