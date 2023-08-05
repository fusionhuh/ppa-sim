import math

class node:
    def __init__(self, level: int, bit_pos: int, is_operator: bool, up = None, right = None):
        self.pred_up = up
        self.pred_right = right
        self.level = level
        self.bit_pos = bit_pos
        self.is_operator = is_operator

def generate_precalc_layer(bit_width: int):
    node_graph = [{}]
    for i in range(0, bit_width):
        node_graph[0][i] = node(is_operator=False, level=0, bit_pos=i) 
    return node_graph

def test_graph_completeness(bit_width: int, graph: list):
    for i in range(1, bit_width):
        assert is_sum_bit_complete(i, graph) == True

def is_sum_bit_complete(bit_pos: int, graph) -> bool:
    def helper(n: node):
        up_bounds: tuple
        right_bounds: tuple
        if n.pred_up.level == 0:
            up_bounds = [n.pred_up.bit_pos, n.pred_up.bit_pos]
        else:
            up_bounds = helper(n.pred_up)

        if n.pred_right.level == 0: 
            right_bounds = [n.pred_right.bit_pos, n.pred_right.bit_pos]
        else:
            right_bounds = helper(n.pred_right)
        assert up_bounds[1] == right_bounds[0] + 1
        return [up_bounds[0], right_bounds[1]]
    bounds: tuple = helper(get_lowest_node(bit_pos, graph))
    return (bounds[0] == bit_pos and bounds[1] == 0)

def generate_ks_graph(bit_width: int):
    assert math.floor(math.log(bit_width, 2)) == math.log(bit_width,2)

    node_graph = generate_precalc_layer(bit_width)

    depth = int(math.log(bit_width, 2))

    for i in range(0, depth): 
        new_row: dict = {}
        for j in range(0, bit_width):
            if j < int(math.pow(2, i)):
                connection_node: node = node(level=i+1, bit_pos=j, is_operator=False, up=node_graph[i][j])
                new_row[j] = connection_node
            else:
                reach = int(math.pow(2, i))
                operator_node: node = node(level=i+1, is_operator=True, bit_pos=j, up=get_lowest_node(j, node_graph), right=get_lowest_node(j-reach, node_graph))
                new_row[j] = operator_node
        node_graph.append(new_row)

    return node_graph

def get_lowest_node(bit_pos: int, graph):
    lowest: node = graph[0][bit_pos]
    for i in range(1, len(graph)):
        if bit_pos in graph[i].keys() and graph[i][bit_pos].is_operator:
            lowest = graph[i][bit_pos]
    return lowest

def generate_bk_graph(bit_width: int):
    assert math.floor(math.log(bit_width, 2)) == math.log(bit_width,2)

    node_graph = generate_precalc_layer(bit_width)

    twos_operator_depth = int(math.log(bit_width, 2))

    for i in range(1, twos_operator_depth+1):
        new_row: dict = {}
        stride = int(math.pow(2, i))
        j = int(math.pow(2, i)) - 1
        while j < bit_width:
            pred_up: node = get_lowest_node(j, node_graph)
            pred_right: node = get_lowest_node(j - stride/2, node_graph)
            new_node: node = node(level=i, bit_pos=j, is_operator=True, up=pred_up, right=pred_right)
            new_row[j] = new_node
            j += stride
        node_graph.append(new_row)

    curr_level = twos_operator_depth
    for i in range(twos_operator_depth-1, 0, -1):
        if curr_level == len(node_graph):
            node_graph.append({})
        new_row: dict = {}
        stride = int(math.pow(2, i))
        reach = int(stride/2)
        j = int(math.pow(2, i)) - 1 + reach
        while j < bit_width-1:
            pred_up: node = get_lowest_node(j, node_graph)
            pred_right: node = get_lowest_node(j-reach, node_graph)
            new_node: node = node(level=curr_level, bit_pos=j, is_operator=True, up=pred_up, right=pred_right)
            new_row[j] = new_node
            j += stride
        for i, n in new_row.items():
            node_graph[curr_level][i] = n
        curr_level += 1

    return node_graph

def get_node_count(node_graph):
    count: int = 0
    for i in range(1, len(node_graph)):
        for node in node_graph[i].values():
            if node.is_operator:
                count += 1
    return count

def generate_hybrid_graph(bit_width: int, bk_levels: int):
    assert math.floor(math.log(bit_width, 2)) == math.log(bit_width,2)
    assert int(math.log(bit_width, 2)) - 3 >= bk_levels

    node_graph = generate_precalc_layer

    bk_graph = generate_bk_graph(bit_width)

    bk_upper_levels = [bk_graph[i] for i in range(0,bk_levels+1)]
    node_graph = bk_upper_levels
    bk_lower_levels = [bk_graph[i] for i in range(len(bk_graph)-bk_levels, len(bk_graph))]

    # 1) place first ks node at (2 ** (bk_levels+1)) - 1
    # 2) place more nodes with stride 2 ** bk_levels
    # 3) connect nodes with starting reach 2 ** bk_levels
    # 4) for each new layer of ks:
    #   a) increase starting pos by current reach
    #   b) multiply reach by 2
    # 5) stop placing layers when bit_width - current reach == -1

    starting_pos = (2 ** (bk_levels+1)) - 1
    stride = 2**bk_levels
    reach = stride
    curr_level = bk_levels + 1
    while (bit_width-1) - reach != -1:
        new_row: dict = {}
        curr_pos = starting_pos
        while curr_pos < bit_width:
            pred_up: node = get_lowest_node(curr_pos, node_graph)
            pred_right: node = get_lowest_node(curr_pos-reach, node_graph)
            new_node: node = node(curr_level, curr_pos, is_operator=True, up=pred_up, right=pred_right)
            new_row[curr_pos] = new_node
            curr_pos += stride
        node_graph.append(new_row)
        curr_level+=1
        starting_pos += reach
        reach *= 2
    
    # copy lower levels of bk graph to main graph...

    ending_ks_level = len(node_graph)
    for i in range(0, bk_levels):
        curr_bk_level = bk_lower_levels[i]
        reach = 2 ** (bk_levels - i - 1)
        for n in curr_bk_level.values():
            n.level = ending_ks_level + i
            pred_up: node = get_lowest_node(n.bit_pos, node_graph)
            pred_right: node = get_lowest_node(n.bit_pos-reach, node_graph)
            n.pred_up = pred_up
            n.pred_right = pred_right
        node_graph.append(curr_bk_level)

    return node_graph

def generate_serial_graph(bit_width: int):
    node_graph = generate_precalc_layer(bit_width)

    for i in range(1, bit_width):
        new_node: node = node(level=i, bit_pos=i, is_operator=True, up=node_graph[0][i], right=get_lowest_node(i-1, node_graph))
        new_row: dict = {i: new_node}
        node_graph.append(new_row)
    return node_graph

def generate_skl_graph(bit_width: int) -> list:
    node_graph = generate_precalc_layer(bit_width)

    curr_level = 1
    group_size = 1
    while group_size != bit_width:
        new_row = {}
        curr_pos = group_size
        while curr_pos < bit_width:
            pred_right = get_lowest_node(curr_pos - 1, node_graph)
            for i in range(0, group_size):
                pred_up = get_lowest_node(curr_pos, node_graph)
                new_node: node = node(curr_level, curr_pos, is_operator=True, up=pred_up, right=pred_right)
                new_row[curr_pos] = new_node
                curr_pos += 1
            curr_pos += group_size
        group_size *= 2
        curr_level += 1
        node_graph.append(new_row)
    return node_graph

def generate_graph(function_name: str, block_size: int, hybrid_levels=-1):
    if hybrid_levels == -1:
        return globals()[function_name](block_size)
    else:
        return globals()[function_name](block_size, hybrid_levels)
