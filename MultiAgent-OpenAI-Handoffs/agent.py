from dotenv import load_dotenv
load_dotenv()

from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real app, call a weather API here
    return f"The weather in {city} is sunny."

# Weather expert agent with the weather tool
weather_agent = Agent(
    name="WeatherAgent",
    instructions="You are a weather expert. Answer weather questions using the get_weather tool.",
    tools=[get_weather]
)

# Main assistant that can delegate to the weather agent
assistant_agent = Agent(
    name="AssistantAgent",
    instructions=(
        "You are a helpful assistant. "
        "If the user's question is about the weather, delegate to the WeatherAgent. "
        "Otherwise, answer the question yourself."
    ),
    handoffs=[weather_agent]
)

# Let's ask about the weather
query = "What's the weather in Paris today?"
result = Runner.run_sync(assistant_agent, query)
print(result.final_output)


