import yaml

# Load the current DSL
with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
    dsl = yaml.safe_load(f)

graph = dsl['workflow']['graph']
nodes = graph['nodes']
edges = graph['edges']

# 1. New Node: Task Splitter
task_splitter = {
    'data': {
        'context': {'enabled': False, 'variable_selector': []},
        'desc': '将出题任务拆分为具体的子任务列表，准备并行生成',
        'model': {
            'completion_params': {'temperature': 0.1, 'max_tokens': 1000},
            'mode': 'chat',
            'name': 'deepseek-ai/DeepSeek-V3',
            'provider': 'siliconflow'
        },
        'prompt_template': [
            {
                'id': 'splitter-sys',
                'role': 'system',
                'text': '你是一个出题任务拆分专家。\n用户要求生成 {{#start.question_count#}} 道关于【{{#start.topic#}}】的题目。\n请结合背景资料：\n{{#tool_firecrawl.text#}}\n\n请将这个大任务拆分为 {{#start.question_count#}} 个具体的、互不重叠的子方案。\n每个子方案应包含：\n1. 具体的考点或切入点\n2. 建议的题目情境\n\n请**仅输出**一个包含这些子方案字符串的 JSON 数组，不要有任何其他解释性文字。\n例如：["考点1: ..., 情境: ...", "考点2: ..., 情境: ..."]'
            }
        ],
        'title': '出题任务拆分 (LLM)',
        'type': 'llm',
        'variables': []
    },
    'height': 98,
    'id': 'llm_task_splitter',
    'position': {'x': 1250, 'y': 400},
    'positionAbsolute': {'x': 1250, 'y': 400},
    'selected': False,
    'sourcePosition': 'right',
    'targetPosition': 'left',
    'type': 'custom',
    'width': 244
}

# 2. Update llm_generator into llm_single_generator
for node in nodes:
    if node['id'] == 'llm_generator':
        node['id'] = 'llm_single_generator'
        node['title'] = '单题狙击手 (LLM)'
        node['data']['desc'] = '每次只针对一个具体的子任务，生成 1 道高质量题目及其深度解析'
        # Update prompt to focus on single item
        node['data']['prompt_template'][0]['text'] = (
            "{{#code_constraint.strict_rules#}}\n\n"
            "你是一位拥有20年实战经验的【{{#start.profession#}}】领域资深考官与终极培训专家。\n"
            "请结合以下资料出题：\n"
            "【参考资料】：\n"
            "{{#tool_firecrawl.text#}}\n\n"
            "【本次具体任务】：\n"
            "{{#iteration.item#}}\n\n"
            "【生成规则】：\n"
            "请围绕上述具体任务，生成 **1 道** 难度级别为【{{#start.difficulty#}}】的题目（按照指定的题型）。\n"
            "必须包含：题目、选项（如适用）、正确答案、深度解析。\n"
            "必须采用 Markdown 排版。"
        )

# 3. New Node: Iteration
iteration_node = {
    'data': {
        'desc': '并行循环生成每道题目',
        'selected': False,
        'title': '题目并行迭代器',
        'type': 'iteration',
        'variables': [
            {
                'value_selector': ['llm_task_splitter', 'text'],
                'variable': 'iterator_list'
            }
        ],
        'start_node_id': 'llm_single_generator'
    },
    'height': 300, # Large enough to contain the inner node
    'id': 'iteration_generator',
    'position': {'x': 1550, 'y': 250},
    'positionAbsolute': {'x': 1550, 'y': 250},
    'selected': False,
    'sourcePosition': 'right',
    'targetPosition': 'left',
    'type': 'custom',
    'width': 400
}

# 4. Mark llm_single_generator as being in iteration
for node in nodes:
    if node['id'] == 'llm_single_generator':
        node['data']['isInIteration'] = True
        # Position inside iteration relative? Dify uses absolute coordinates but nested logically
        node['position'] = {'x': 1600, 'y': 300}

# 5. Remove old edges connected to llm_generator and add new ones
new_edges = []
for edge in edges:
    # Remove: firecrawl -> llm_generator, code -> llm_generator, llm_generator -> end
    if edge['target'] == 'llm_generator':
        continue
    if edge['source'] == 'llm_generator':
        continue
    new_edges.append(edge)

# Add new connections
# tool_firecrawl -> llm_task_splitter
new_edges.append({
    'data': {'isInIteration': False, 'sourceType': 'tool', 'targetType': 'llm'},
    'id': 'edge-firecrawl-splitter',
    'source': 'tool_firecrawl',
    'sourceHandle': 'source',
    'target': 'llm_task_splitter',
    'targetHandle': 'target',
    'type': 'custom',
    'zIndex': 0
})
# llm_task_splitter -> iteration_generator
new_edges.append({
    'data': {'isInIteration': False, 'sourceType': 'llm', 'targetType': 'iteration'},
    'id': 'edge-splitter-iteration',
    'source': 'llm_task_splitter',
    'sourceHandle': 'source',
    'target': 'iteration_generator',
    'targetHandle': 'target',
    'type': 'custom',
    'zIndex': 0
})
# code_constraint -> iteration_generator
new_edges.append({
    'data': {'isInIteration': False, 'sourceType': 'code', 'targetType': 'iteration'},
    'id': 'edge-code-iteration',
    'source': 'code_constraint',
    'sourceHandle': 'source',
    'target': 'iteration_generator',
    'targetHandle': 'target',
    'type': 'custom',
    'zIndex': 0
})
# iteration_generator -> end
new_edges.append({
    'data': {'isInIteration': False, 'sourceType': 'iteration', 'targetType': 'end'},
    'id': 'edge-iteration-end',
    'source': 'iteration_generator',
    'sourceHandle': 'source',
    'target': 'end',
    'targetHandle': 'target',
    'type': 'custom',
    'zIndex': 0
})

graph['nodes'].append(task_splitter)
graph['nodes'].append(iteration_node)
graph['edges'] = new_edges

# 6. Update End node to output iteration results
for node in nodes:
    if node['id'] == 'end':
        node['data']['outputs'] = [
            {
                'value_selector': ['iteration_generator', 'output'],
                'variable': 'final_questions_array'
            }
        ]
        node['position'] = {'x': 2000, 'y': 250}

# Save the refactored DSL
with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl_v4_parallel.yml', 'w', encoding='utf-8') as f:
    yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

print("Success: DSL refactored to question_factory_script_dsl_v4_parallel.yml")
