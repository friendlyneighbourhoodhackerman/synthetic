import string
from syn.core import create_net, add_node, add_edge_to_net


def load_net(net_file, min_ts=-1, max_ts=-1):
    fin = open(net_file)
    
    net = create_net()

    # 0: ?; 1: parsing nodes; 2: parsing edges
    state = 0

    nodes = {}
    
    for line in fin:
        line = line.strip()
        if line == '[nodes]':
            state = 1
        elif line == '[edges]':
            state = 2
        else:
            params = {}
            param_strings = line.split()
            for param in param_strings:
                p = param.split('=')
                if len(p) == 2:
                   params[p[0]] = p[1]

            if state == 1:
                node = add_node(net, 0)
                nodes[params['id']] = node
            elif state == 2:
                orig = nodes[params['orig']]
                targ = nodes[params['targ']]
                ts = 0
                if 'ts' in params:
                    ts = nodes[params['ts']]

                if ((min_ts < 0) or (ts >= min_ts)) and ((max_ts < 0) or (ts < max_ts)):
                    add_edge_to_net(net, orig, targ, ts)

    return net


def snap2syn(in_file, out_file):
    fin = open(in_file)
    fout = open(out_file, 'w')

    nodes = {}
    node_count = 0
    edge_count = 0
    
    # nodes
    fout.write('[nodes]\n')
    for line in fin:
        if (line[0] != '#'):
            strings = string.split(line)
            if len(strings) == 2:
                for s in strings:
                    if not nodes.has_key(s):
                        nodes[s] = node_count
                        fout.write('id=%d\n' % node_count)
                        node_count += 1

    # edges
    fout.write('[edges]\n')
    fin.seek(0)
    for line in fin:
        if (line[0] != '#'):
            strings = string.split(line)
            if len(strings) == 2:
                fout.write('orig=%d targ=%d\n' % (nodes[strings[0]], nodes[strings[1]]))
                edge_count += 1

    fin.close()
    fout.close()

    return node_count, edge_count
