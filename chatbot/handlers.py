"""
handlers.py — Gradio event handlers for PolicyAI Chatbot

Functions
---------
respond(message, history)  : run the RAG pipeline and append to chat history.
clear_chat()               : reset chat, input, and sources to empty state.
"""

from pipeline import rag


def respond(message: str, history: list) -> tuple[list, str]:
    """
    Called on every user message (Send button or Enter key).

    Parameters
    ----------
    message : plain-text question from the user.
    history : current Gradio chat history (list of role/content dicts).

    Returns
    -------
    updated_history : history with the new user + assistant turn appended.
    context         : retrieved source chunks — displayed in the Sources panel.
    """
    if not message.strip():
        return history, ""

    answer, context = rag(message)

    updated_history = history + [
        {"role": "user",      "content": message},
        {"role": "assistant", "content": answer},
    ]
    return updated_history, context


def clear_chat() -> tuple[list, str, str]:
    """Reset the chat, input field, and sources panel."""
    return [], "", ""
