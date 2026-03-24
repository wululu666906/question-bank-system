import yaml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    # Move to 0.3.1 for better iteration support
    dsl['version'] = '0.3.1'

    graph = dsl['workflow']['graph']
    nodes = graph['nodes']
    edges = graph['edges']

    # Node IDs
    SPLITTER_ID = 'llm_task_splitter'
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_single_generator'
    ITERATION_START_ID = ITERATION_ID + 'start'

    # 1. Task Splitter LLM
    task_splitter = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'desc': '把题目要求拆成具体的大纲列表 (JSON Array)',
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
                    'text': '你是一个出题专家。\n用户要求生成 {{#start.question_count#}} 道关于【{{#start.topic#}}】的题目。\n请参照背景资料：{{#tool_firecrawl.text#}}\n\n请将任务拆分为 {{#start.question_count#}} 个独立的知识点/具体出题任务。\n**仅输出一个 JSON 字符数组**，不要回复任何多余文字。\n例如: ["任务1: ...", "任务2: ..."]'
                }
            ],
            'title': '1. 任务拆分',
            'type': 'llm',
            'variables': []
        },
        'height': 98,
        'id': SPLITTER_ID,
        'position': {'x': 1250, 'y': 350},
        'positionAbsolute': {'x': 1250, 'y': 350},
        'selected': False,
        'sourcePosition': 'right',
        'targetPosition': 'left',
        'type': 'custom',
        'width': 244
    }

    # 2. Iteration Node
    iteration_node = {
        'data': {
            'desc': '循环生成每一个题目',
            'iterator_selector': [SPLITTER_ID, 'text'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '2. 题目并行生成器',
            'type': 'iteration'
        },
        'height': 300,
        'id': ITERATION_ID,
        'position': {'x': 1550, 'y': 250},
        'positionAbsolute': {'x': 1550, 'y': 250},
        'selected': False,
        'sourcePosition': 'right',
        'targetPosition': 'left',
        'type': 'custom',
        'width': 450
    }

    # 3. Iteration Start
    iteration_start = {
        'data': {
            'desc': '',
            'isInIteration': True,
            'selected': False,
            'title': '',
            'type': 'iteration-start'
        },
        'id': ITERATION_START_ID,
        'parentId': ITERATION_ID,
        'position': {'x': 20, 'y': 100},
        'positionAbsolute': {'x': 1570, 'y': 350},
        'type': 'custom-iteration-start',
        'width': 44,
        'height': 48,
        'zIndex': 1001
    }

    # 4. Inner LLM Node
    inner_llm = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'desc': '生成单道题目',
            'isInIteration': True,
            'model': {
                'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-V3',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'inner-sys',
                    'role': 'system',
                    'text': '{{#strict_rules#}}\n\n参考背景：{{#background#}}\n\n当前任务：{{#task_item#}}\n\n请围绕该具体任务生成 1 道难度级别为【{{#difficulty#}}】的题目。必须包含题目、选项、答案和深度解析。采用 Markdown 排版。'
                }
            ],
            'title': '单题生成器',
            'type': 'llm',
            'variables': [
                {'value_selector': ['code_constraint', 'strict_rules'], 'variable': 'strict_rules'},
                {'value_selector': ['tool_firecrawl', 'text'], 'variable': 'background'},
                {'value_selector': [ITERATION_ID, 'item'], 'variable': 'task_item'},
                {'value_selector': ['start', 'difficulty'], 'variable': 'difficulty'}
            ]
        },
        'id': INNER_LLM_ID,
        'parentId': ITERATION_ID,
        'position': {'x': 120, 'y': 80},
        'positionAbsolute': {'x': 1670, 'y': 330},
        'selected': False,
        'sourcePosition': 'right',
        'targetPosition': 'left',
        'type': 'custom',
        'width': 244,
        'height': 98,
        'zIndex': 1001
    }

    # 5. Connect Edges
    # Remove old connections to original llm_generator
    edges = [e for e in edges if e['target'] != 'llm_generator' and e['source'] != 'llm_generator']

    edges.append({'data':{'isInIteration':False}, 'id':'e1', 'source':'tool_firecrawl', 'target':SPLITTER_ID, 'type':'custom'})
    edges.append({'data':{'isInIteration':False}, 'id':'e2', 'source':SPLITTER_ID, 'target':ITERATION_ID, 'type':'custom'})
    edges.append({'data':{'isInIteration':True, 'iteration_id':ITERATION_ID}, 'id':'e3', 'source':ITERATION_START_ID, 'target':INNER_LLM_ID, 'type':'custom'})
    edges.append({'data':{'isInIteration':False}, 'id':'e4', 'source':ITERATION_ID, 'target':'end', 'type':'custom'})

    # 6. Final graph assembly
    new_nodes = [n for n in nodes if n['id'] != 'llm_generator' and n['id'] != 'end']
    
    # End node
    end_node = {
        'data': {
            'desc': '输出合并后的题库',
            'outputs': [{'value_selector': [ITERATION_ID, 'output'], 'variable': 'result'}],
            'title': '结束',
            'type': 'end'
        },
        'id': 'end',
        'height': 100,
        'width': 244,
        'position': {'x': 2100, 'y': 250},
        'positionAbsolute': {'x': 2100, 'y': 250},
        'type': 'custom'
    }

    new_nodes.extend([task_splitter, iteration_node, iteration_start, inner_llm, end_node])
    
    dsl['workflow']['graph']['nodes'] = new_nodes
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_parallel_v5_final.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final DSL generated at question_factory_parallel_v5_final.yml")

if __name__ == "__main__":
    refactor()
