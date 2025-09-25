# from src.reflection_pattern import reflection_agent


# agent = reflection_agent.ReflectAgent()

# query = "Write python program to find hcf of two numbers"

# res = agent.run(query)
# print(res)

# from src.tool_agent.tool_agent import ToolAgent
# from src.tool_agent.tool import tool

# @tool
# def find_lucky_number(a: int, b: int) -> int:
#     """
#     Calculates a lucky number based on the given inputs.

#     This function multiplies two integers and adds 25 to the result. 
#     The calculation is intended to represent a fun or arbitrary "lucky number."

#     Args:
#         a (int): The first integer input.
#         b (int): The second integer input.

#     Returns:
#         int: The calculated lucky number based on the expression (a * b + 25).
#     """
#     ans = a * b + 25
#     return ans

# tools = [find_lucky_number]
# agent = ToolAgent(tools)

# res = agent.run("Can you find  lucky number if you know a is 5 and b is 10")

# print(res)


# from src.planning_agent.react_agent import ReactAgent
# from src.tool_agent.tool import tool
# import math

# import math
# from typing import Callable

# @tool
# def add(a: int, b: int) -> int:
#     """Adds two integers and returns the result.

#     Args:
#         a (int): The first integer.
#         b (int): The second integer.

#     Returns:
#         int: The sum of the two integers.
#     """
#     return a + b

# @tool
# def multiply(a: int, b: int) -> int:
#     """Multiplies two integers and returns the result.

#     Args:
#         a (int): The first integer.
#         b (int): The second integer.

#     Returns:
#         int: The product of the two integers.
#     """
#     return a * b

# @tool
# def compute_log(a: int) -> float:
#     """Calculates the natural logarithm of a given positive integer.

#     Args:
#         a (int): A positive integer.

#     Returns:
#         float: The natural logarithm of the given integer.

#     Raises:
#         ValueError: If 'a' is less than or equal to zero, as log is undefined.
#     """
#     if a <= 0:
#         raise ValueError("Input must be a positive integer.")
    
#     return math.log(a)


# tools = [add,multiply,compute_log]

# agent = ReactAgent(tools)

# res = agent.run("What is the final output of log(10*20 + 80 ) + 70")

# print(res)

from src.tool_agent.tool import tool
from src.multiagent_systen.crew import Crew
from src.multiagent_systen.agent import Agent

@tool
def write_str_to_txt(string_data: str, txt_filename: str):
    """
    Writes a string to a txt file.

    This function takes a string and writes it to a text file. If the file already exists, 
    it will be overwritten with the new data.

    Args:
        string_data (str): The string containing the data to be written to the file.
        txt_filename (str): The name of the text file to which the data should be written.
    """
    # Write the string data to the text file
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        file.write(string_data)

    print(f"Data successfully written to {txt_filename}")
    
    
with Crew() as crew:
    print("Entered")
    agent_1 = Agent(
    name="Poet Agent",
    backstory="You are a well-known poet, who enjoys creating high quality poetry.",
    task_description="Write a poem about the meaning of life",
    task_expected_output="Just output the poem, without any title or introductory sentences",
    )

    agent_2 = Agent(
        name="Poem Translator Agent",
        backstory="You are an expert translator especially skilled in Spanish",
        task_description="Translate a poem into Spanish", 
        task_expected_output="Just output the translated poem and nothing else"
        )

    agent_3 = Agent(
        name="Writer Agent",
        backstory="You are an expert transcriber, that loves writing poems into txt files",
        task_description="You'll receive a Spanish poem in your context. You need to write the poem into './poem.txt' file",
        task_expected_output="A txt file containing the greek poem received from the context",
        tools= [write_str_to_txt],
        )

    agent_1 >> agent_2 >> agent_3
    
    crew.run()