from dotenv import load_dotenv
load_dotenv()

import asyncio
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Words a result must contain to count as weather news
WEATHER_WORDS = (
    "rain", "weather", "monsoon", "cyclone", "storm",
    "heat", "temperature", "imd", "forecast", "flood",
)
# Words that mark unrelated pages (prices, power cuts)
SKIP_WORDS = ("price", "power cut", "shutdown")


def search_weather_news(city: str) -> str:
    """Search the web for today's weather news for a given city.

    Use this tool whenever the user asks about the current weather, forecast,
    rain, storms or temperature in a city today. Do not use it for general
    knowledge or trivia questions.

    Args:
        city: The name of the city, for example "Chennai".

    Returns:
        Recent weather news items for that city, one per line, with date and source.
    """
    results = DDGS().news(
        query=f"{city} weather rain forecast IMD",
        timelimit="w",      # last week
        max_results=10,
    )

    kept = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        text = f"{title} {body}".lower()

        # keep only results about this city, about weather, and not prices/power cuts
        if (
            city.lower() in text
            and any(w in text for w in WEATHER_WORDS)
            and not any(s in text for s in SKIP_WORDS)
        ):
            date = r.get("date", "")[:10]
            source = r.get("source", "")
            kept.append(f"{date} | {source} | {title} | {body}")

    if not kept:
        return f"No recent weather news found for {city}."
    return "\n".join(kept[:5])


city = input("Which city? ")

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

agent = AssistantAgent(
    name="weather_news",
    model_client=model_client,
    tools=[search_weather_news],
    system_message=(
        "You are a weather news assistant. Always use the search tool to find "
        "weather news for the city, then summarise it. "
        "Reply in exactly 3 short lines, each on its own row, one short sentence "
        "per line, with no introduction and no closing text. "
        "Use ONLY facts stated in the search results. Do not add advice, "
        "predictions or safety tips of your own. "
        "Only talk about the requested city, never another place. "
        "Mention the date of a report when it is not from today. "
        "If the results clearly contradict each other, use the most recent one. "
        "If the tool says no weather news was found, say so in the lines."
    ),
    reflect_on_tool_use=True,
)


async def main():
    await Console(
        agent.run_stream(
            task=(
                f"Give me today's weather news for {city}. "
                "Reply in exactly 3 short lines, each on its own row."
            )
        )
    )
    await model_client.close()


asyncio.run(main())