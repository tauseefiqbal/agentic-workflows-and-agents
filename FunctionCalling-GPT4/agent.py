def get_population(country: str) -> int:
    """Return the population of the given country (as an integer)."""
    # ... imagine this calls an API or database ...
    return 67500000  # (for example, France ~67.5 million)

def get_wikipedia_summary(topic: str) -> str:
    """Return a brief summary of the Wikipedia page for the given topic."""
    # ... imagine this calls Wikipedia API ...
    return "France, officially the French Republic, is a country primarily located in Western Europe..."  # etc.


import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()  # uses OPENAI_API_KEY env variable

tools = [
    {
      "type": "function",
      "function": {
          "name": "get_population",
          "description": "Retrieve the population of a specified country.",
          "parameters": {
              "type": "object",
              "properties": {
                  "country": {"type": "string", "description": "Name of the country"}
              },
              "required": ["country"]
          }
      }
    },
    {
      "type": "function",
      "function": {
          "name": "get_wikipedia_summary",
          "description": "Fetch a short Wikipedia summary for a given topic.",
          "parameters": {
              "type": "object",
              "properties": {
                  "topic": {"type": "string", "description": "Topic to summarize (e.g., country name)"}
              },
              "required": ["topic"]
          }
      }
    }
]

# Map function names to implementations
available_functions = {
    "get_population": get_population,
    "get_wikipedia_summary": get_wikipedia_summary,
}

messages = [
    {"role": "system", "content": "You are an assistant that can use tools."},
    {"role": "user", "content": "What is the population of France, and can you give me a summary of France's Wikipedia page?"}
]

# Loop: let the model call tools until it produces a final text answer
while True:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # If the model wants to call one or more tools
    if message.tool_calls:
        # Append the assistant message (with tool_calls) to the conversation
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            print(f"Calling {func_name}({func_args})")

            # Execute the function
            func = available_functions.get(func_name)
            if func:
                result = func(**func_args)
            else:
                result = f"Error: unknown function {func_name}"

            # Append the tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
    else:
        # No tool calls — this is the final answer
        print(message.content)
        break

# User query (asking for two things)
# --> [get_population: Country -> Number] 
# --> (intermediate result: population as Number) 
# --> [get_wikipedia_summary: Topic -> Text] 
# --> (intermediate result: summary Text)
# --> (final answer composed using both Number and Text)

def translate(text: str, language: str) -> str:
    """Translate the given text into the target language."""
    # ... (calls some translation API) ...
    return "Buenos días"  # for example, "Good morning" -> "Buenos días"


def multiply(x: float, y: float) -> float:
    """Return the product of x and y."""
    return x * y