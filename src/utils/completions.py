from typing import List,Optional,Any

def generate_response(client, messages: list, model: str) -> str:
    """
    Generates a response from the LLM using the specified model.

    Args:
        client: The LLM client (e.g., OpenAI API client).
        messages (list): A list of message dictionaries, each with 'role' and 'content'.
        model (str): The model name to use for generating the response.

    Returns:
        str: The content of the response message.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        # Extract and return the response content
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error in generating response"


def struct_the_prompt(role: str, message: str, tag: str = "") -> dict:
    """
    Structures a message into a dictionary for the LLM.

    Args:
        role (str): Role of the message sender (e.g., "user", "assistant", "system").
        message (str): The message content.
        tag (str, optional): An optional tag to wrap around the message. Defaults to "".

    Returns:
        dict: A dictionary with 'role' and 'content' keys formatted for LLM interaction.
    """
    try:
        # Validate inputs
        if not isinstance(role, str) or not isinstance(message, str):
            raise ValueError("Both role and message should be strings.")

        # Add tags if provided
        if tag:
            message = f"<{tag}>{message}</{tag}>"

        return {"role": role, "content": message}
    
    except Exception as e:
        print(f"Error in structuring the prompt: {e}")
        return {"role": "error", "content": "Invalid input"}

def update_chat_history(history: list, msg: dict):
    """Updates chat history with a new message.

    Args:
        history (list): List containing chat history.
        msg (dict): Message to be added.

    Raises:
        ValueError: If the input types are incorrect.
    """
    try:
        # Check for correct types
        if not isinstance(history, list) or not isinstance(msg, dict):
            raise ValueError("Expected 'history' to be a list and 'msg' to be a dictionary.")

        history.append(msg)  # Append the message
        return history  # Return updated history

    except Exception as e:
        print(f"Error in updating history: {e}")

class ChatHistory(list):
    """
    A custom list to store chat messages with an optional maximum length.

    Args:
        message (Optional[List[Any]]): Initial list of messages. Defaults to an empty list.
        max_length (int): Maximum number of messages to store. Defaults to -1 (no limit).
    """
    def __init__(self, message: Optional[List[Any]] = None, max_length: int = -1):
        self.max_length = max_length if max_length > 0 else -1
        super().__init__(message if message is not None else [])
        
    def append(self, obj: Any):
        """
        Appends a new message to the chat history while respecting max length.

        Args:
            obj (Any): The message to append.

        Returns:
            None
        """
        if not isinstance(obj, (str, dict)):
            raise TypeError("Only strings or dictionaries are allowed.")

        #print("Current Chat History:", self)

        # Enforce max length if applicable
        if self.max_length > 0 and len(self) >= self.max_length:
            self.pop(0)

        super().append(obj) # equivalent to list.append(self,object)


class FixedFirstChatHistory(ChatHistory):
    """Preserves the first message and removes the second when max_length is reached."""

    def __init__(self, message: Optional[List[Any]] = None, max_length: int = -1):
        # Properly call parent constructor
        super().__init__(message, max_length)

    def append(self, obj: Any):
        """Appends a new message, preserving the first and removing the second if needed."""
        # Check if max length constraint applies and the list is long enough
        if self.max_length != -1 and len(self) >= self.max_length:
            if len(self) > 1:  # Ensure at least 2 elements
                self.pop(1)  # Remove the second message instead of the first

        super().append(obj)
        
if __name__ == "__main__":
    chat = FixedFirstChatHistory(max_length=3)  # Limit to 3 messages
    chat.append("Hello")
    chat.append("How are you?")
    chat.append("I'm fine, thank you!")
    chat.append("New message, first one removed!")  # First message is removed
    print(chat)