# AI Basic Inventory Agent Loop

## Your challenge

A small local business — a coffee shop supply store with two physical locations — is losing money. Not because sales are down, but because no one on the team can answer a simple question at any given moment: "Do we have enough of this product to cover the week?"

Stock is tracked in a shared spreadsheet that no one updates consistently. The owner, Carla, has reached out to you after seeing a demo of an AI assistant at a trade fair. She doesn't want a dashboard she has to maintain manually — she wants to be able to talk to a system and get answers. She also wants the system to act as a register: it should track deliveries, log sales, and tell her when something is running low.

Your job is to build that system. It has two parts that must work together:

1. A REST API built with FastAPI that manages the inventory data. It exposes endpoints for listing products, registering new ones, updating stock levels, and retrieving low-stock alerts. Products are stored in a CSV file so the data persists between sessions.
2. An AI agent written in Python that connects to an LLM and uses your API as its set of tools. The agent runs in a loop — it receives a message from Carla, reasons about what action to take, calls the appropriate API endpoint as a tool, and responds with the result. Every step of that loop is logged to a separate `conversation_log.csv` file.

## How to start the project

This project uses a Python starter template. Fork and clone it:

https://github.com/4GeeksAcademy/python-hello

You can work either in GitHub Codespaces (open the repo and click Code -> Codespaces -> Create) or by cloning it locally. Once cloned, create your own GitHub repository and update the remote URL so your progress is tracked there.

Full instructions: how to start a coding project

Starting the system:

You need two terminal sessions running at the same time — one for the API, one for the agent.

```bash
# Terminal 1 - start the API
uvicorn api.app:app --reload

# Terminal 2 - start the agent
python agent.py
```

Stopping the system:

Press `Ctrl + C` in each terminal to stop the corresponding process. Stop the agent first, then the API. The `conversation_log.csv` file is written incrementally, so no data is lost when you stop mid-session.

Relaunching the agent:

Run `python agent.py` again in Terminal 2. The API does not need to be restarted. The agent will start a new session, but all previous conversation history will remain intact in `conversation_log.csv` — new rows are always appended, never overwritten.

Once the environment is ready:

```bash
# Create a .env file at the root with your LLM API key:
GROQ_API_KEY=your_key_here
```

IMPORTANT: Never commit your `.env` file. Add it to `.gitignore` before your first commit.

## What you need to do

### API (`api/app.py`)

- [ ] Create a FastAPI application that stores inventory data in a `products.csv` file.
- [ ] `GET /api/products` — Returns the full product list.
- [ ] `POST /api/products` — Adds a new product.
- [ ] `PATCH /api/inventory/{product_id}` — Updates the stock of an existing product.
- [ ] `GET /api/inventory/alerts` — Returns all products whose quantity is below a configurable threshold (default: 10 units).
- [ ] All endpoints must return appropriate HTTP status codes and descriptive messages on error.

### Agent (`agent.py`)

- [ ] Define your API endpoints as tools for the LLM — each tool must have a clear description and typed parameters.
- [ ] Implement the full agent loop: Observe -> Think -> Act -> Update -> Repeat.
- [ ] The agent must keep the conversation history in memory for the duration of the session.
- [ ] When the LLM selects a tool, the agent must call the corresponding API endpoint and inject the result back into the context.
- [ ] The loop must terminate cleanly when the LLM returns a final response.

### Conversation log

- [ ] Every event in the loop must be appended to `conversation_log.csv` with these four fields: `actor`, `message`, `tool_call`, `timestamp`.
- [ ] The CSV must include the four required fields: `actor`, `message`, `tool_call`, `timestamp`.
- [ ] The file must persist across sessions (append-only, never overwrite prior sessions).

### General

- [ ] The API must be running before the agent starts. Document how to launch both in the README.
- [ ] IMPORTANT: Do not use any agent framework (LangChain, LlamaIndex, AutoGen, etc.). The agent loop must be implemented manually in plain Python.

## What we will evaluate

- [ ] The FastAPI exposes all required endpoints and they return correct responses.
- [ ] The agent loop correctly implements the Observe -> Think -> Act -> Update -> Repeat cycle.
- [ ] Tools are defined with names, descriptions, and typed parameters that the LLM can reliably use.
- [ ] The agent calls the correct API endpoint when the LLM selects a tool.
- [ ] The LLM result is injected back into the conversation history before the next iteration.
- [ ] `conversation_log.csv` is created and populated with all four fields on every event.
- [ ] The log is append-only across multiple sessions.
- [ ] The agent handles at least one multi-step interaction (e.g., add a product and immediately ask for alerts).
- [ ] No agent framework is used — the loop is hand-coded in Python.

> Note: UI design and visual presentation are not evaluated. A terminal interface is sufficient.

## How to submit

Push your repository to GitHub and share the link following the instructions. Make sure to update the README as specified here.

1. Create a GitHub repo for the project.
2. Commit the code with a clear message.
3. Push the repo to GitHub.
4. Copy the repository URL and submit it in your final answer.

```bash
git init
git add .
git commit -m "Add inventory API and agent scaffold"
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```

## Project structure

```text
.
├── agent.py
├── api/
│   ├── __init__.py
│   ├── app.py
│   └── data/
│       └── products.csv
├── .gitignore
├── .env.example
├── main.py
├── requirements.txt
├── README.md
└── conversation_log.csv
```

The project is intentionally scaffolded so the inventory API and tool wiring are ready. The last missing piece for the challenge is the hand-coded agent loop itself.
