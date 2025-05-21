RE_REPEAT_LIMIT = 1024
# a|b|c...
def parse_split(r, idx):
    idx, prev = parse_concat(r, idx)
    while idx < len(r):
        if r[idx] == ')':
            # return to the outer parse_node
            break
        assert r[idx] == '|', 'BUG'
        idx, node = parse_concat(r, idx + 1)
        prev = ('split', prev, node)
    return idx, prev

# abc...
def parse_concat(r, idx):
    prev = None
    while idx < len(r):
        if r[idx] in '|)':
            # return to the outer parse_split or parse_node
            break
        idx, node = parse_node(r, idx)
        if prev is None:
            prev = node
        else:
            prev = ('cat', prev, node)
    # when the prev is still None, it denotes the empty string
    return idx, prev

# parse a single element
def parse_node(r, idx):
    ch = r[idx]
    idx += 1
    assert ch not in '|)'
    if ch == '(':
        idx, node = parse_split(r, idx)
        if idx < len(r) and r[idx] == ')':
            idx += 1
        else:
            raise Exception('unbalanced parenthesis')
    elif ch == '.':
        node = 'dot'
    elif ch in '*':
        raise Exception('nothing to repeat')
    else:
        node = ch

    idx, node = parse_postfix(r, idx, node)
    return idx, node

# a*, a+, a{x}, a{x,}, a{x,y}
def parse_postfix(r, idx, node):
    if idx == len(r) or r[idx] != '*':
        return idx, node

    idx += 1

    node = ('repeat', node)
    return idx, node

def parse_int(r, idx):
    save = idx
    while idx < len(r) and r[idx].isdigit():
        idx += 1
    return idx, int(r[save:idx]) if save != idx else None

def re_parse(r):
    idx, node = parse_split(r, 0)
    if idx != len(r):
        # parsing stopped at a bad ")"
        raise Exception('unexpected ")"')
    return node


class Node:
    @classmethod
    def gen_id(cls):
        if not hasattr(cls, '_id'):
            cls._id = 0
        cls._id += 1
        return cls._id - 1
    
    @classmethod
    def to_dot(cls, node):
        visited = set()
        queue = [node]
        dot_lines = ['digraph G {', '    rankdir=LR;']
        
        # BFS to visit all nodes and their transitions
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
                
            visited.add(current)
            
            # Add node with its label
            dot_lines.append(f'    {current.id} [label="{str(current)}"];')
            
            # Add transitions
            for cond, dst in current.transitions:
                edge_label = 'ε' if cond is None else cond
                dot_lines.append(f'    {current.id} -> {dst.id} [label="{edge_label}"];')
                if dst not in visited:
                    queue.append(dst)
        
        dot_lines.append('}')
        return '\n'.join(dot_lines)
    
    def __init__(self, name = None) -> None:
        self.name = name
        self.id = Node.gen_id()
        self.transitions = []
    
    def add_transitions(self, edge):
        self.transitions.append(edge)

    def __repr__(self) -> str:
        if self.name:
            return self.name
        return f'Node {self.id}'
    
    def __hash__(self) -> int:
        return self.id
 
def build_repeat(pattern, start: Node, end: Node):
    _, node= pattern
    in_node = Node('in')
    start.add_transitions((None, in_node))
    out_node = Node('out')
    out_node.add_transitions((None, end))
    out_node.add_transitions((None, in_node))

    build_nfa(node, in_node, out_node)
    start.add_transitions((None, out_node))
    

def build_nfa(pattern, start: Node, end: Node):
    if pattern is None:
        start.add_transitions((None, end))
    elif pattern == 'dot':
        start.add_transitions(('.', end))
    elif isinstance(pattern, str):
        start.add_transitions((pattern, end))
    elif pattern[0] == 'cat':
        mid = Node('mid')
        build_nfa(pattern[1], start, mid)
        build_nfa(pattern[2], mid, end)
    elif pattern[0] == 'split':
        build_nfa(pattern[1], start, end)
        build_nfa(pattern[2], start, end)
    elif pattern[0] == 'repeat':
        build_repeat(pattern, start, end)

def step_nfa(node_set, ch):
    next_nodes = set()
    for node in node_set:
        for cond, dst in node.transitions:
            if cond == '.' or cond == ch:
                next_nodes.add(dst)
    
    return next_nodes

def closure(node_set: set):
    changed = True

    while changed:
        changed = False
        new_set = set()
        for node in node_set:
            for cond, dst in node.transitions:
                if cond is None:
                    new_set.add(dst)
                    changed = (dst not in node_set)

        node_set.update(new_set)
    
    return node_set

def match_nfa(start, end, s):
    work_list = {start}
    work_list = closure(work_list)

    for ch in s:
        work_list = step_nfa(work_list, ch)
        work_list = closure(work_list)

    return end in work_list

def match(pattern, s, save_dot = False):
    global_start = Node('start')
    global_end = Node('end')
    pattern = re_parse(pattern)
    build_nfa(pattern, global_start, global_end)
    if save_dot:
        dot = Node.to_dot(global_start)
        with open('nfa.dot', 'w') as f:
            f.write(dot)
    return match_nfa(global_start, global_end, s)