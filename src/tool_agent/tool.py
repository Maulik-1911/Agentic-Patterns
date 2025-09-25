
from typing import Callable, Dict
import json

def get_fn_signatures(fn: Callable) -> Dict:
    """
    Extracts the signature of a given function and formats it into a dictionary.

    Args:
        fn (Callable): The function for which the signature needs to be extracted.

    Returns:
        dict: A dictionary containing:
            - 'name': The name of the function.
            - 'description': The docstring of the function, if available.
            - 'parameters': A dictionary with:
                - 'properties': A mapping of argument names to their types (as strings).
                - 'return_type': The return type of the function, if annotated.
    """
    
    res = {
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": {
            "properties": {},
        }
    }

    # Extract parameters and their types
    res["parameters"]["properties"] = {
        k: {"type": v.__name__ if hasattr(v, '__name__') else str(v)}
        for k, v in fn.__annotations__.items()
        if k != "return"
    }

    return res


def validate_arguments(tool_call: dict, tool_signature: dict) -> dict:
    """
    Validates and converts arguments in the input dictionary to match the expected types.

    Args:
        tool_call (dict): A dictionary containing the arguments passed to the tool.
        tool_signature (dict): The expected function signature and parameter types.

    Returns:
        dict: The tool call dictionary with the arguments converted to the correct types if necessary.
    """
    properties = tool_signature["parameters"]["properties"]

    # TODO: This is overly simplified but enough for simple Tools.
    type_mapping = {
        "int": int,
        "str": str,
        "bool": bool,
        "float": float,
    }

    for arg_name, arg_value in tool_call["arguments"].items():
        expected_type = properties[arg_name].get("type")

        if not isinstance(arg_value, type_mapping[expected_type]):
            tool_call["arguments"][arg_name] = type_mapping[expected_type](arg_value)

    return tool_call


class Tool:
    def __init__(self,name:str ,fn:Callable , fn_signature:str):
        self.name = name
        self.fn = fn
        self.fn_signature = fn_signature
    
    def __str__(self):
        return self.fn_signature
    
    def run(self,**kwargs):
        return self.fn(**kwargs)
    
    
def tool(fn):
    def wrapper():
        fn_sign = get_fn_signatures(fn)
        
        return Tool(name=fn_sign['name'] , fn=fn,fn_signature=json.dumps(fn_sign))
    
    return wrapper()
            
## Method -1
# def add(a:int , b:int)->int:
#     """add two numbers"""
#     return a+b

# x = tool(add)

## Method -2 calling decorators
# @tool
# def add(a:int , b:int)->int:
#     """add two numbers"""
#     return a+b

if __name__ == '__main__':
    args = {"a":2,"b":3}
    # x = add.run(**args)
    # print(x.run(**args))