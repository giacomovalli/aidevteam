from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.custom_tool import MCPAdapterTool, HumanInquiryTool
from crewai import LLM

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

llm_gemini = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.3,
)

@CrewBase
class Aidevteam():
    """Aidevteam crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def team_leader(self) -> Agent:
        # Initialize MCP tool with your server adapter
        # Replace with your actual MCPServerAdapter instance
        # Example: mcp_tool = MCPAdapterTool(your_server_adapter)
        # For now, we'll comment this out until you provide the adapter
        # mcp_tool = MCPAdapterTool(server_adapter)
        
        return Agent(
            config=self.agents_config['team_leader'], # type: ignore[index]
            verbose=True,
            model=llm_gemini
            #tools=[HumanInquiryTool()],
            #tools=[mcp_tool]  # Uncomment when you have your MCPServerAdapter
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analyst'], # type: ignore[index]
            verbose=True,
            use_system_prompt=False,
            tools=[HumanInquiryTool()],
            model=llm_gemini
        )

    @agent
    def backend_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_developer'], # type: ignore[index]
            verbose=True,
            model=llm_gemini
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task

    @task
    def new_feature_request(self) -> Task:
        return Task(
            config=self.tasks_config['new_feature_request'], # type: ignore[index]
            human_input=True
        )

    @task
    def new_feature_implementation(self) -> Task:
        return Task(
            config=self.tasks_config['new_feature_implementation'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Aidevteam crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[self.business_analyst(), self.backend_developer()], # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # Use hierarchical process for better task management https://docs.crewai.com/how-to/Hierarchical/
            verbose=True,
            manager_agent=self.team_leader(),
            model=llm_gemini
        )
