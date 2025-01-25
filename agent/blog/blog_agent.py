import json
from util.time_exe import time_execution
from agent.blog.blog_planner_agent import BlogPlannerAgent
from agent.blog.blog_main_body_section_agent import BlogMainBodySectionAgent
from agent.blog.blog_intro_agent import BlogIntroAgent
from agent.blog.blog_conclusion_agent import BlogConclusionAgent


class BlogAgent:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5:32b", temperature=0.0, stream=False):
        
        """Initialize Agent with a base url and model name."""
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.stream = stream    

    @time_execution        
    def execute(self, user_query: str, *args) -> str:
        """Execute the full pipeline: plan and execute tools, chaining responses."""
        try:
            
            print(f"{BlogAgent.__name__} : calling series of agents to generate blog for '{user_query}'")
                   
            # Generate a plan using the LLM
            planner_agent = BlogPlannerAgent(self.base_url, self.model, self.temperature, self.stream)
            intro_agent = BlogIntroAgent(self.base_url, self.model, self.temperature, self.stream)
            mainbody_agent = BlogMainBodySectionAgent(self.base_url, self.model, self.temperature, self.stream)
            conclusion_agent = BlogConclusionAgent(self.base_url, self.model, self.temperature, self.stream)

            sections = planner_agent.execute(user_query)
            intro_section = next((section for section in sections if section["type"] == "Introduction"), None)

            blog = ""
            intro = intro_agent.execute(json.dumps(intro_section))
            blog += f"{intro["heading"]}\n\n"
            blog += f"{intro["body"]}\n\n"

            for section in sections:
                if section["type"] == "Main Body":
                    main = mainbody_agent.execute(json.dumps(section))
                    blog += f"{main["heading"]}\n\n"
                    blog += f"{main["body"]}\n\n"
                    blog += f"{main["code"]}\n\n"


            conclusion = conclusion_agent.execute(json.dumps(blog))
            blog += f"{conclusion["heading"]}\n\n"
            blog += f"{conclusion["body"]}\n\n"
                
            return blog 
        
        except Exception as e:
            print(f'Exception in {BlogAgent.__name__}: {str(e)}')
            return f"Error executing plan: {str(e)}"

   