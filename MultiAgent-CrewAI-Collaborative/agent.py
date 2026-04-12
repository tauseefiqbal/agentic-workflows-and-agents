import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Tools
search_tool = SerperDevTool()

# Agents
analyst = Agent(
    role='Market Analyst',
    goal='Analyze market trends for {product}',
    backstory="Expert in data-driven insights.",
    tools=[search_tool],
    llm="gpt-4o-mini",
    verbose=True
)
strategist = Agent(
    role='Strategy Consultant',
    goal='Develop go-to-market strategies based on analysis',
    backstory="Seasoned consultant with Fortune 500 experience.",
    llm="gpt-4o-mini",
    verbose=True
)

# Tasks
analyze_task = Task(
    description="Research current market size, competitors, and trends for {product}.",
    expected_output="A concise report on market landscape.",
    agent=analyst
)
strategy_task = Task(
    description="Using the analysis, outline a 3-month launch strategy.",
    expected_output="Bullet-point strategy with KPIs.",
    agent=strategist,
    context=[analyze_task]
)

# Crew
crew = Crew(
    agents=[analyst, strategist],
    tasks=[analyze_task, strategy_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={"product": "AI Agent Frameworks"})
print(result)

