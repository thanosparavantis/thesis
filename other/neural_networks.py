import math
import random
from typing import List


class Node:
    def __init__(self, key: int):
        self.key = key


class NeuronNode(Node):
    def __init__(self, key: int):
        super().__init__(key)
        self.bias = random.uniform(0, 1)

    @staticmethod
    def activation(z: float) -> float:
        return 1 / (1 + math.exp(z))

    def forward(self, x: List[float], weights: List[float]) -> float:
        z = 0
        for idx, inp in enumerate(x):
            weight = weights[idx]
            z += weight * inp
        return self.activation(z + self.bias)


class InputNode(Node):
    def __init__(self, key: int):
        super().__init__(key)

    def __str__(self):
        return f'Input Node {self.key}'


class HiddenNode(NeuronNode):
    def __init__(self, key: int):
        super().__init__(key)

    def __str__(self):
        return f'Hidden Node {self.key}'


class OutputNode(NeuronNode):
    def __init__(self, key: int):
        super().__init__(key)

    def __str__(self):
        return f'Output Node {self.key}'


class Connection:
    def __init__(self, parent: Node, child: Node, weight: float):
        self.parent = parent
        self.child = child
        self.weight = weight

    def __str__(self):
        return f'Connection from {self.parent} to {self.child}'


class NeuralNetwork:
    def __init__(self, inputs: int, outputs: int):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = []
        self.connections = []

        for key in range(1, inputs + 1):
            self.nodes.append(InputNode(key))

        for key in range(inputs + 1, inputs + outputs + 1):
            self.nodes.append(OutputNode(key))

    def mutate_add_node(self) -> None:
        con = random.choice(self.connections)

        node = HiddenNode(len(self.nodes) + 1)
        self.nodes.append(node)

        self.connections.append(Connection(con.parent, node, random.uniform(0, 1)))
        self.connections.append(Connection(node, con.child, 1.0))
        self.connections.remove(con)

    def mutate_add_connection(self) -> None:
        node1 = random.choice(self.nodes)
        node2 = random.choice(self.nodes)

        while node1 == node2 \
                or self.is_connected(node1, node2) \
                or self.is_connected(node2, node1) \
                or (type(node1) == InputNode and type(node2) == InputNode) \
                or (type(node1) == OutputNode and type(node2) == OutputNode):
            node1 = random.choice(self.nodes)
            node2 = random.choice(self.nodes)

        if node1.key > node2.key or type(node1) == OutputNode:
            self.connections.append(Connection(node2, node1, random.uniform(0, 1)))
        else:
            self.connections.append(Connection(node1, node2, random.uniform(0, 1)))

    def mutate_weight(self) -> None:
        connection = random.choice(self.connections)
        connection.weight = random.uniform(0, 1)

    def mutate_bias(self) -> None:
        neuron_nodes = list(filter(lambda node: isinstance(node, NeuronNode), self.nodes))
        node = random.choice(neuron_nodes)
        node.bias = random.uniform(0, 1)

    def is_connected(self, node1: Node, node2: Node) -> bool:
        return len(list(filter(lambda con: con.parent == node1 and con.child == node2, self.connections))) > 0

    def get_input_nodes(self):
        return list(filter(lambda x: type(x) == InputNode, self.nodes))

    def forward(self, x: List[float]) -> List[float]:
        evaluated = {self.nodes[idx]: inp for idx, inp in enumerate(x)}
        hidden_nodes = list(filter(lambda node: type(node) == HiddenNode, self.nodes))
        output_nodes = list(filter(lambda node: type(node) == OutputNode, self.nodes))
        hidden_nodes.reverse()
        output_nodes.reverse()
        nodes = hidden_nodes + output_nodes

        for node in nodes:
            connections = list(filter(lambda con: con.child == node, self.connections))

            if len(connections) == 0:
                evaluated[node] = 0.0
            else:
                weights = [con.weight for con in connections]
                parent_nodes = [con.parent for con in connections if con.parent != node]
                print(parent_nodes)
                values = [evaluated[parent] for parent in parent_nodes]
                evaluated[node] = node.forward(values, weights)

        output_nodes.reverse()
        return [evaluated[node] for node in output_nodes]
