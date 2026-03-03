from typing import Dict, List, Any

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage

from agentic_platform.core.models.memory_models import Message, ToolCall, ToolResult, TextContent

class LangChainMessageConverter:

    @classmethod
    def convert_ai_message(cls, message: AIMessage) -> Message:
        # This is the easy path. langChain will return content as either a string or a list of dictionaries.
        if type(message.content) == str:
            return Message(role="assistant", text=message.content)

        # If it's a list of dictionaries, we need to iterate through them and convert them to our types.
        elif isinstance(message.content, list):
            # This is the response object that will eventually become our response.
            msg_dict: Dict[str, Any] = {'role': 'assistant'}

            for chunk in message.content:
                # Figure out what type we're dealing with.
                chunk_type: str = chunk["type"]

                # If it's text, we can just add it cleanly.
                if chunk_type == "text":
                    msg_dict["text"] = chunk["text"]

                # Tool use is a bit wonky. With pydantic models as inputs, Langchain captures the name of the class
                # as the first input and then the subsequent inputs are the arguments. There's no clean way
                # to parse this correctly so we just pass the inputs as is.
                elif chunk_type == "tool_use":
                    tool_call: ToolCall = ToolCall(name=chunk["name"], arguments=chunk["input"], id=chunk["id"])
                    msg_dict.setdefault("tool_calls", []).append(tool_call)

            return Message(**msg_dict)
    
    @classmethod
    def convert_human_message(cls, message: HumanMessage) -> Message:
        if type(message.content) == str:
            return Message(role="user", text=message.content)
        else:
            raise ValueError(f"Unexpected message type: {type(message)}")
    
    @classmethod
    def convert_tool_message(cls, message: ToolMessage) -> Message:
        # Langchain returns the output of a tool call as a string. We just have to do the best we can here.
        if type(message.content) == str:
            tool_result: ToolResult = ToolResult(
                content=[TextContent(text=message.content)], 
                id=message.tool_call_id
            )
            return Message(role="user", tool_results=[tool_result])
        else:
            raise ValueError(f"Unexpected message type: {type(message)}")
    
    @classmethod
    def convert_langchain_messages(cls, messages: List[BaseMessage]) -> List[Message]:
        my_messages: List[Message] = []
        for message in messages:
            if message.type == "human":
                my_messages.append(cls.convert_human_message(message))
            elif message.type == "ai":
                my_messages.append(cls.convert_ai_message(message))
            elif message.type == "tool":
                my_messages.append(cls.convert_tool_message(message))
        return my_messages