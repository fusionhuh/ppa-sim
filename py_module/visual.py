import matplotlib.pyplot as plt
import numpy as np
from matplotlib import collections as mc
import graph

def create_bit_position_lines(bit_width: int):
    first_points = [(i, 0) for i in range(0, bit_width)]
    second_points = [(i, 20) for i in range(0, bit_width)]
    lines = [[first_points[i], second_points[i]] for i in range(0, bit_width)]
    return lines

def create_node_points(graph, bit_width: int):
    points: list = []
    for i in range(0, len(graph)):
        for n in graph[i].values():
            if not n.is_operator: continue

            points.append([n.bit_pos, n.level])
    return points

def create_node_connection_lines(graph, bit_width: int):
    node_points = []
    pred_points = []
    for i in range(1, len(graph)):
        for n in graph[i].values():
            if not n.is_operator: continue

            node_pos = [n.bit_pos, n.level]
            pred_up: graph.node = n.pred_up
            pred_right: graph.node = n.pred_right
            node_points.append(node_pos)
            node_points.append(node_pos)
            pred_points.append([pred_up.bit_pos, n.level-1])
            pred_points.append([pred_right.bit_pos, n.level-1])
    lines = [[node_points[i], pred_points[i]] for i in range(len(node_points))]
    return lines

def draw_node_graph(graph, bit_width:int):
    lines = create_bit_position_lines(bit_width)
    points = create_node_points(graph, bit_width)
    connections = create_node_connection_lines(graph, bit_width)
    lc = mc.LineCollection(lines)
    fig, ax = plt.subplots()
    ax.set_xlim(-1, bit_width)
    ax.set_ylim(0, len(graph)+1)
    ax.add_collection(lc)
    lc = mc.LineCollection(connections)
    ax.add_collection(lc)
    for point in points:
        ax.plot(point[0], point[1], marker="o", markersize=15)
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()
    plt.show()
