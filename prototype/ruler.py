
if len(nodes) == 0:                 # 如果没有其他节点，则本节点处理
    process_request(data)
elif len(nodes) > 0:                # 如果有其他节点
    if total_load() == 0:           # 如果所有节点负载都为0
        if min_node(i, nodes):      # 如果自己的节点号最小，则本节点处理
            process_request(data)
    else:                           # 如果负载大于0
        if min_node():              # 如果本节点负载最小，则本节点处理
            process_request(data)
