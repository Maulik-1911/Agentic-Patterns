from textwrap import dedent
from src.planning_agent.react_agent import ReactAgent
from src.multiagent_systen.crew import Crew
from src.tool_agent.tool import Tool

class Agent:
    def __init__(
        self,
        name: str,
        backstory: str,
        task_description: str,
        task_expected_output: str = "",
        tools: list[Tool] | None = None,
        llm: str = "llama-3.3-70b-versatile",
    ) -> None:
        self.name = name
        self.backstory = backstory
        self.task_description = task_description
        self.task_expected_output = task_expected_output
        self.tools = tools
        self.model = llm
        self.dependencies: list[Agent] = []  # Agents this agent depends on
        self.dependents: list[Agent] = []  # Agents depending on this agent
        self.context = ""  # Corrected spelling
        if self.tools is None:
            self.tools = []
        self.react_agent = ReactAgent(tools=self.tools, model=self.model, system_prompt=self.backstory)
        Crew.register_agent(self)  # Register agent in the crew

    def __str__(self):
        return self.name

    def __rshift__(self, other):
        """Defines the '>>' operator for setting dependencies."""
        self.add_dependent(other)
        return other

    def __lshift__(self, other):
        """Defines the '<<' operator for setting dependencies."""
        self.add_dependency(other)
        return other

    def __rrshift__(self, other):
        """
        Defines the '<<' operator evaluated from right to left.

        Args:
            other (Agent): The agent this agent depends on.
        """
        self.add_dependency(other)
        return self  # Allow chaining

    def __rlshift__(self, other):
        """
        Defines the '<<' operator when evaluated from right to left.

        Args:
            other (Agent): The agent that depends on this agent.

        Returns:
            Agent: The current agent (self) to allow for chaining.
        """
        self.add_dependent(other)
        return self  # Allow chaining

    def add_dependency(self, other) -> None:
        """
        Adds an agent or list of agents as dependencies.

        Args:
            other (Agent or list[Agent]): Agent(s) this agent depends on.
        """
        if isinstance(other, Agent):
            self.dependencies.append(other)
            other.dependents.append(self)

        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                self.dependencies.append(item)
                item.dependents.append(self)

        else:
            raise TypeError("The dependency must be an instance or list of Agent.")

    def add_dependent(self, other) -> None:
        """
        Adds an agent or list of agents as dependents.

        Args:
            other (Agent or list[Agent]): Agent(s) depending on this agent.
        """
        if isinstance(other, Agent):
            self.dependents.append(other)
            other.dependencies.append(self)

        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                self.dependents.append(item)
                item.dependencies.append(self)

        else:
            raise TypeError("The dependent must be an instance or list of Agent.")

    def receive_context(self, input_data: str):
        """
        Receives and stores context information from other agents.

        Args:
            input_data (str): The context information to be added.
        """
        self.context += f"{self.name} received context:\n{input_data}\n"

    def create_prompt(self) -> str:
        """
        Creates a prompt for the agent based on its task description, expected output, and context.

        Returns:
            str: The formatted prompt string.
        """
        prompt = dedent(
            f"""
            You are an AI agent. You are part of a team of agents working together to complete a task.
            I'm going to give you the task description enclosed in <task_description></task_description> tags. I'll also give
            you the available context from the other agents in <context></context> tags. If the context
            is not available, the <context></context> tags will be empty. You'll also receive the task
            expected output enclosed in <task_expected_output></task_expected_output> tags. With all this information
            you need to create the best possible response, always respecting the format as described in
            <task_expected_output></task_expected_output> tags. If expected output is not available, just create
            a meaningful response to complete the task.

            <task_description>
            {self.task_description}
            </task_description>

            <task_expected_output>
            {self.task_expected_output}
            </task_expected_output>

            <context>
            {self.context}
            </context>

            Your response:
            """
        ).strip()

        return prompt

    def run(self) -> str:
        """
        Runs the agent's task and generates the output.

        Returns:
            str: The output generated by the agent.
        """
        msg = self.create_prompt()
        output = self.react_agent.run(msg)

        # Pass the output to all dependent agents
        for dependent in self.dependents:
            dependent.receive_context(output)
        return output
