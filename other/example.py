import matplotlib.pyplot as plt
from matplotlib.axes import Axes, math
from matplotlib.patches import Circle

from neural_networks import NeuralNetwork, InputNode, HiddenNode

x = [
    0.05, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, -0.05
]

inputs = 36
outputs = 3

nn = NeuralNetwork(inputs, outputs)
nn.mutate_add_connection()
nn.mutate_add_connection()
nn.mutate_add_node()
nn.mutate_add_node()
nn.mutate_add_connection()

output = nn.forward(x)

axis = plt.axes()  # type: Axes

hidden_nodes = list(filter(lambda node: type(node) == HiddenNode, nn.nodes))

if len(hidden_nodes) > 0:
    output_x = max(node.key for node in hidden_nodes) + 1
else:
    output_x = inputs

node_coords = dict()

for node in nn.nodes:
    if type(node) == InputNode:
        coords = (0, node.key)
        axis.add_patch(Circle(xy=coords, radius=0.3))
    elif type(node) == HiddenNode:
        connections = list(filter(lambda con: con.child == node, nn.connections))
        height = connections[0].parent.key

        while len(connections) > 0:
            connections = list(filter(lambda con: con.child == connections[0].parent, nn.connections))
            if len(connections) > 0:
                height = connections[0].parent.key

        coords = (node.key - inputs - outputs, height)
        axis.add_patch(Circle(xy=coords, radius=0.3))
    else:
        coords = (output_x, node.key - inputs / 2)
        axis.add_patch(Circle(xy=coords, radius=0.3))

    node_coords[node] = coords

for con in nn.connections:
    head_length = 0.5
    a = node_coords[con.parent]
    b = node_coords[con.child]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    vec_ab = [dx, dy]
    vec_ab_magnitude = math.sqrt(dx ** 2 + dy ** 2)
    dx = dx / vec_ab_magnitude
    dy = dy / vec_ab_magnitude
    vec_ab_magnitude = vec_ab_magnitude - head_length
    axis.arrow(a[0], a[1], vec_ab_magnitude * dx, vec_ab_magnitude * dy, head_width=0.5, head_length=0.7, fc='lightgreen', ec='green')

plt.yticks([i for i in range(inputs + 2)])
plt.xticks([i for i in range(output_x + 2)])

plt.show()
print('KK')
