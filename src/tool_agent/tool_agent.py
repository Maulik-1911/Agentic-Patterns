##  I have to create agent that can use tool and respond to user queries

from src.utils.completions import ChatHistory,generate_response,struct_the_prompt,update_chat_history
from src.tool_agent.tool import Tool,validate_arguments
from groq import Groq
from dotenv import load_dotenv
import json
from typing import List
from colorama import Fore
from src.utils.extraction import extract_tag_content

load_dotenv()

TOOL_SYSTEM_PROMPT = """
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.
For each function call return a json object with function name and arguments within <tool_call></tool_call>
XML tags as follows:
you also check history if you already called the resuld and you have observation respond user with the observation

<tool_call>
{"name": <function-name>,"arguments": <args-dict>,  "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools:

<tools>
%s
</tools>
"""

class ToolAgent:
    def __init__(self,tools:List[Tool] | Tool,model:str = 'llama-3.3-70b-versatile')->None:
        self.client = Groq()
        self.model = model
        self.tools = tools
        self.tools_dict = {f.name : f for f in self.tools}
        
    def add_tool_signatures(self) -> str:
        """
        Collects the function signatures of all available tools.

        Returns:
            str: A concatenated string of all tool function signatures in JSON format.
        """
        return "".join([tool.fn_signature for tool in self.tools])

    
    def process_tool_calls(self, tool_calls_content: list) -> dict:
        """
        Processes each tool call, validates arguments, executes the tools, and collects results.

        Args:
            tool_calls_content (list): List of strings, each representing a tool call in JSON format.

        Returns:
            dict: A dictionary where the keys are tool call IDs and values are the results from the tools.
        """
        observations = {}
        for tool_call_str in tool_calls_content:
            tool_call = json.loads(tool_call_str)
            tool_name = tool_call["name"]
            tool = self.tools_dict[tool_name]

            print(Fore.GREEN + f"\nUsing Tool: {tool_name}")

            # Validate and execute the tool call
            validated_tool_call = validate_arguments(
                tool_call, json.loads(tool.fn_signature)
            )
            print(Fore.GREEN + f"\nTool call dict: \n{validated_tool_call}")

            result = tool.run(**validated_tool_call["arguments"])
            print(Fore.GREEN + f"\nTool result: \n{result}")

            # Store the result using the tool call ID
            observations[validated_tool_call["id"]] = result

        return observations
    
    
    def run(self,usr_msg:str)->str:
        agent_history = ChatHistory(
            [
                struct_the_prompt("system",TOOL_SYSTEM_PROMPT % self.add_tool_signatures()),
                struct_the_prompt("user" , usr_msg)
            ]
            ,max_length=3)
        
        llm_response = generate_response(self.client,agent_history,self.model)
        
        tool_calls = extract_tag_content(str(llm_response), "tool_call")

        if tool_calls.found:
            observations = self.process_tool_calls(tool_calls.content)
            update_chat_history(
                agent_history, struct_the_prompt(role="user",message=f"Observations {observations}")
            )

        return generate_response(self.client, agent_history, self.model)
        
        
        
        
        
        
            
        
        
        
    