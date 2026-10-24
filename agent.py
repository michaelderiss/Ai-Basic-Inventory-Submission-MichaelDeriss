from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LOG_PATH = Path(__file__).resolve().parent / "conversation_log.csv"

SYSTEM_PROMPT = """
You are Carla's inventory assistant. You have access to an inventory API and must use it as your toolset.

Rules:
- Keep a short memory of the conversation in the session.
- Use the API tools when the user requests a product list, stock change, or low-stock alert.
- Always respond in plain language and explain what you did and the result.
- If you need to update stock, prefer to send a small adjustment that matches the request.
- When a tool call is used, inject the tool result into the context before continuing.
""".strip()


def append_conversation_log(actor: str, message: str, tool_call: str | None = None) -> None:
    """Append one event to the conversation log CSV."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOG_PATH.exists()

    with LOG_PATH.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(["actor", "message", "tool_call", "timestamp"])
        writer.writerow([actor, message, tool_call or "", datetime.now(timezone.utc).isoformat()])


def build_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_products",
                "description": "List all inventory products in the store.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_product",
                "description": "Create a new inventory product with a name, quantity, price, and location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Product name."},
                        "quantity": {"type": "integer", "description": "Opening stock quantity."},
                        "price": {"type": "number", "description": "Unit price of the product."},
                        "location": {"type": "string", "description": "Store location such as North or South."},
                    },
                    "required": ["name", "quantity", "price", "location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_stock",
                "description": "Increase or decrease stock for a product by a delta value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "The product ID to update."},
                        "delta": {"type": "integer", "description": "Positive values add stock; negative values remove stock."},
                        "reason": {"type": "string", "description": "Reason for the adjustment."},
                    },
                    "required": ["product_id", "delta"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_low_stock_alerts",
                "description": "List products whose quantity is at or below a threshold value.",
                "parameters": {
                    "type": "object",
                    "properties": {"threshold": {"type": "integer", "default": 10, "description": "Stock threshold to compare against."}},
                    "required": ["threshold"],
                },
            },
        },
    ]


def request_llm(messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Send the current messages to the LLM provider.

    This uses Groq's OpenAI-compatible API so project owners can plug in their API key without
    extra framework setup.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to a .env file in the project root.")

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.2,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def call_tool(name: str, args: dict[str, Any]) -> Any:
    """Execute a tool call against the FastAPI inventory API."""
    if name == "list_products":
        response = requests.get(f"{API_BASE_URL}/api/products", timeout=30)
        response.raise_for_status()
        return response.json()

    if name == "create_product":
        response = requests.post(f"{API_BASE_URL}/api/products", json=args, timeout=30)
        response.raise_for_status()
        return response.json()

    if name == "update_stock":
        product_id = args["product_id"]
        payload = {"delta": args.get("delta"), "reason": args.get("reason", "tool update")}
        response = requests.patch(f"{API_BASE_URL}/api/inventory/{product_id}", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    if name == "get_low_stock_alerts":
        threshold = args.get("threshold", 10)
        response = requests.get(f"{API_BASE_URL}/api/inventory/alerts", params={"threshold": threshold}, timeout=30)
        response.raise_for_status()
        return response.json()

    raise ValueError(f"Unsupported tool call: {name}")


def print_welcome_message() -> None:
    print("Inventory agent scaffold is ready.")
    print("The final hand-coded loop is intentionally left for the next step in the challenge.")
    print(f"API base URL: {API_BASE_URL}")
    print("Set GROQ_API_KEY in a .env file before running the full loop against the LLM.")


def run_agent_loop(user_message: str = "Check the current inventory and flag low stock items.") -> str:
    """Project scaffold for the agent loop.

    The actual Observe -> Think -> Act -> Update -> Repeat loop is left intentionally as a
    hand-coded step for the challenge. This function sets up the tool definitions, log writing,
    and API integration points so the final loop can be added cleanly.
    """
    append_conversation_log("user", user_message)

    tools = build_tool_schema()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    try:
        llm_response = request_llm(messages, tools)
        first_choice = llm_response["choices"][0]
        assistant_message = first_choice["message"].get("content") or "I am ready to process the inventory task."
        append_conversation_log("agent", assistant_message)

        if "tool_calls" not in first_choice["message"]:
            return assistant_message

        for tool_call in first_choice["message"]["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"].get("arguments", {})
            if isinstance(tool_args, str):
                import json
                tool_args = json.loads(tool_args)

            append_conversation_log("tool", f"Call {tool_name} with {tool_args}", tool_call=tool_name)
            tool_result = call_tool(tool_name, tool_args)
            messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_name, "content": str(tool_result)})
            append_conversation_log("api", str(tool_result), tool_call=tool_name)

        # TODO: hand-code the final loop here.
        # The missing logic should keep the conversation context in memory, decide whether to keep calling
        # tools, inject the tool result back into the model context, and exit cleanly when the LLM gives a
        # final human response.

        
        return assistant_message

    except RuntimeError:
        return "The agent is ready, but the LLM key is missing. Add GROQ_API_KEY to a .env file and rerun the loop."


if __name__ == "__main__":
    print_welcome_message()
    print("Example run:")
    print(run_agent_loop())
