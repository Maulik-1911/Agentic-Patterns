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

REACT_SYSTEM_PROMPT = """
You operate by running a loop with the following steps: Thought, Action, Observation.
You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don' make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.

For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools / actions:

<tools>
%s
</tools>

Example session:

<question>What's the current temperature in Madrid?</question>
<thought>I need to get the current weather in Madrid</thought>
<tool_call>{"name": "get_current_weather","arguments": {"location": "Madrid", "unit": "celsius"}, "id": 0}</tool_call>

You will be called again with this:

<observation>{0: {"temperature": 25, "unit": "celsius"}}</observation>

You then output:

<response>The current temperature in Madrid is 25 degrees Celsius</response>

Additional constraints:

- If the user asks you something unrelated to any of the tools above, answer freely enclosing your answer with <response></response> tags.
"""
BASE_SYSTEM_PROMPT = ""

class ReactAgent:
    def __init__(self,tools:List[Tool] | Tool,model:str = 'llama-3.3-70b-versatile',system_prompt:str =BASE_SYSTEM_PROMPT)->None:
        self.client = Groq()
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iter = 20
        if self.tools:
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
        usr_prompt = struct_the_prompt(role = "user" , message=usr_msg , tag = "question")
        
        if self.tools:
            self.system_prompt += ( "\n" + REACT_SYSTEM_PROMPT % self.add_tool_signatures())
            
        agent_history = ChatHistory([
            struct_the_prompt(role = "system" , message= self.system_prompt),
            usr_prompt
        ])
        
        if self.tools:
            for _ in range(self.max_iter):
                llm_response = generate_response(self.client, agent_history, self.model)
                
                res = extract_tag_content(str(llm_response), "response")
                if res.found:
                    return res.content[0]
                
                thought = extract_tag_content(str(llm_response),"thought")
                tool_call = extract_tag_content(str(llm_response),"tool_call")
                
                update_chat_history(agent_history,struct_the_prompt("assistant" , thought.content[0],"thought"))
                #print(Fore.RED + f"\n agent history {agent_history}")
                
                print(Fore.MAGENTA + f"\nThought: {thought.content[0]}")
                
                if tool_call.found:
                    observations = self.process_tool_calls(tool_call.content)
                    print(Fore.BLUE + f"\nObservations: {observations}")
                    update_chat_history(agent_history , struct_the_prompt("user" , f"observations are {observations}","observation"))
            
        return generate_response(self.client, agent_history, self.model)
        
        