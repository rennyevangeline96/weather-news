# AutoGen Weather News Agent

An AutoGen agent that takes a city, searches the web with the keyless DuckDuckGo package (`ddgs`), and replies with today's weather news in exactly 3 short lines.

## How it works

- **Tool:** `search_weather_news(city: str) -> str` is a plain Python function that calls `DDGS().news(...)`. AutoGen reads its name, type hints and docstring to decide when to call it.
- **Docstring:** says what the tool does, when to use it (today's weather, forecast, rain) and when not to (general trivia).
- **Agent:** `AssistantAgent` with `tools=[search_weather_news]` and `reflect_on_tool_use=True`, so it writes an answer from the results instead of dumping raw search output.
- **Input:** the city comes from `input()`.
- **Output:** exactly 3 short lines, defined in both the system message and the task.
- **Async and cleanup:** runs inside `asyncio.run()`, and `await model_client.close()` closes the client at the end.

## Expected output

```
Which city? Chennai
---------- ToolCallRequestEvent (weather_news) ----------
search_weather_news(city='Chennai')
---------- TextMessage (weather_news) ----------
Line 1
Line 2
Line 3
```

## Project structure

```
weather-news/
├── weather_news.py
├── .gitignore
└── README.md
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -U "autogen-agentchat" "autogen-ext[openai]" python-dotenv ddgs
```

Create a `.env` file:

```
OPENAI_API_KEY=your-openai-key
```

## Run

```bash
python weather_news.py
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named ddgs` | Run `pip install -U ddgs` inside the activated venv |
| Agent answers without searching | Strengthen the docstring and the system message |
| Raw search output printed | Make sure `reflect_on_tool_use=True` |
| Search returns nothing | Try again or use another city, DuckDuckGo can rate-limit |

## Key learnings

- In AutoGen a tool is just a Python function. The name, type hints and docstring tell the agent when to use it.
- `reflect_on_tool_use=True` turns raw search output into a written answer.
- The same agent framework can talk (Day 1) and act (Day 2) once it has a tool.

## Security

The API key is read from `.env`, which is git-ignored and never committed.