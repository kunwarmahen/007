import time
from agent.tool_agent import ToolAgent
from tool.tools import convert_currency, current_weather, country_for_city, get_current_location

def main():
    
    agent = ToolAgent(model="qwen2.5:32b", process_multi_tool=True)
    agent.add_tool(convert_currency)
    agent.add_tool(current_weather)
    agent.add_tool(country_for_city)
    agent.add_tool(get_current_location)
    
    # query_list = ["I am traveling to Japan from India, I have 1500 of local currency, how much of Japaese currency will I be able to get?", "How is the current weather?",
    #               "How is the current weather at Boca Raton, Florida?","Tell me a joke?"]
    query_list = ["How is the current weather?"]    
    
    for query in query_list:
        print(f"\nQuery: {query}")
        # Start the timer
        start_time = time.time()
        result = agent.execute(query)
        end_time = time.time()
        print(result)
        print(f"\nTime taken: {end_time - start_time} secs")

if __name__ == "__main__":
    main() 