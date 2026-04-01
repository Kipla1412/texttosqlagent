def build_conversation_text(messages):

    conversation = []

    for msg in messages:

        role = msg.get("role")
        content = msg.get("content")

        if not content:
            continue

        if role == "user":
            conversation.append(f"Patient: {content}")

        elif role == "assistant":
            conversation.append(f"Assistant: {content}")

    return "\n".join(conversation)