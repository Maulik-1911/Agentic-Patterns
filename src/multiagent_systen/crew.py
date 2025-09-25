from collections import deque
from colorama import Fore
from graphviz import Digraph  


## Corrected Context Manager Class
class Crew:
    Current_crew = None  # Class-level attribute

    def __init__(self):
        self.agents = []

    def __enter__(self):
        Crew.Current_crew = self  # Corrected: Use Crew.Current_crew
        return self

    def __exit__(self, type, value, traceback):
        Crew.Current_crew = None  # Reset correctly

    def add_agent(self, agent):
        self.agents.append(agent)

    @staticmethod
    def register_agent(agent):
        if Crew.Current_crew is not None:
            Crew.Current_crew.add_agent(agent)

    def topological_sort(self):
        """
        Performs a topological sort of agents based on their dependencies.

        Returns:
            list: A sorted list of agents in the order of execution.
        Raises:
            ValueError: If a cyclic dependency is detected.
        """
        indegree = {agent: len(agent.dependencies) for agent in self.agents}
        queue = deque([agent for agent, count in indegree.items() if count == 0])
        
        sorted_agents = []

        while queue:
            agent = queue.popleft()
            sorted_agents.append(agent)  # Append agent to sorted list
            
            for dependent in agent.dependents:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)

        # Detect cycle
        if len(sorted_agents) != len(self.agents):
            raise ValueError("Cyclic dependency detected in the crew")

        return sorted_agents

    def plot(self):
        """
        Plots the Directed Acyclic Graph (DAG) of agents in the crew using Graphviz.

        Returns:
            Digraph: A Graphviz Digraph object representing the agent dependencies.
        """
        dot = Digraph(format="png")

        # Add nodes and edges
        for agent in self.agents:
            dot.node(agent.name)
            for dependency in agent.dependencies:
                dot.edge(dependency.name, agent.name)

        return dot

    def run(self):
        """
        Executes the agents in topological order.

        Prints the agent execution results in a formatted manner.
        """
        sorted_agents = self.topological_sort()

        for agent in sorted_agents:
            print(Fore.GREEN + f"RUNNING AGENT: {agent.name}")
            result = agent.run()
            print(Fore.RED + f"Result: {result}")
