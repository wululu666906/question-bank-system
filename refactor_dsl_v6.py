import yaml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    dsl['version'] = '0.3.1'

    graph = dsl['workflow']['graph']
    nodes = graph['nodes']
    edges = graph['edges']

    # Node IDs
    SPLITTER_ID = 'llm_task_splitter'
    PARSER_ID = 'code_json_parser' # NEW
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_single_generator'
    ITERATION_START_ID = ITERATION_ID + 'start'

    # 1. Task Splitter LLM
    task_splitter = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'desc': '生成 JSON 数组字符串',
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
                    'text': '你是一个任务拆分专家。\n要求生成 {{#start.question_count#}} 个关于【{{#start.topic#}}】的具体任务。\n结合资料：{{#tool_firecrawl.text#}}\n\n**仅输出一个 JSON 数组**，例如: ["任务1", "任务2"]。不要有任何解释。'
                }
            ],
            'title': '1. 任务拆分 (LLM)',
            'type': 'llm',
            'variables': []
        },
        'id': SPLITTER_ID,
        'height': 98, 'width': 244,
        'position': {'x': 1250, 'y': 350},
        'positionAbsolute': {'x': 1250, 'y': 350},
        'type': 'custom'
    }

    # 2. JSON Parser Code Node (CRITICAL FIX)
    json_parser = {
        'data': {
            'code': "import json\ndef main(text):\n    try:\n        # 清理可能存在的 markdown 代码块包裹\n        text = text.strip()\n        if text.startswith('```json'): text = text[7:]\n        if text.startswith('```'): text = text[3:]\n        if text.endswith('```'): text = text[:-3]\n        return {'list': json.loads(text.strip())}\n    except:\n        return {'list': [text]} # 兜底防止崩溃",
            'code_language': 'python3',
            'desc': '将字符串解析为数组',
            'outputs': {'list': {'children': None, 'type': 'array[string]'}},
            'title': '2. 格式转换 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SPLITTER_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID,
        'height': 54, 'width': 244,
        'position': {'x': 1550, 'y': 350},
        'positionAbsolute': {'x': 1550, 'y': 350},
        'type': 'custom'
    }

    # 3. Iteration Node
    iteration_node = {
        'data': {
            'desc': '循环生成题目',
            'iterator_selector': [PARSER_ID, 'list'], # POINT TO THE CODE NODE
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '3. 题目并行生成器',
            'type': 'iteration'
        },
        'id': ITERATION_ID,
        'height': 300, 'width': 450,
        'position': {'x': 1850, 'y': 250},
        'positionAbsolute': {'x': 1850, 'y': 250},
        'type': 'custom'
    }

    # 4. Iteration Start
    iteration_start = {
        'data': {'desc': '', 'isInIteration': True, 'type': 'iteration-start'},
        'id': ITERATION_START_ID,
        'parentId': ITERATION_ID,
        'position': {'x': 20, 'y': 100},
        'positionAbsolute': {'x': 1870, 'y': 350},
        'type': 'custom-iteration-start',
        'width': 44, 'height': 48,
        'zIndex': 1001
    }

    # 5. Inner LLM Node
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
                    'text': '{{#strict_rules#}}\n\n参考资料：{{#background#}}\n\n具体任务：{{#task_item#}}\n\n请针对该任务生成 1 道难度为【{{#difficulty#}}】的题目及解析。'
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
        'positionAbsolute': {'x': 1970, 'y': 330},
        'type': 'custom',
        'width': 244, 'height': 98,
        'zIndex': 1001
    }

    # 6. Edges
    edges = [e for e in edges if e['target'] != 'llm_generator' and e['source'] != 'llm_generator']
    
    edges.append({'id':'e1', 'source':'tool_firecrawl', 'target':SPLITTER_ID, 'type':'custom'})
    edges.append({'id':'e2', 'source':SPLITTER_ID, 'target':PARSER_ID, 'type':'custom'})
    edges.append({'id':'e3', 'source':PARSER_ID, 'target':ITERATION_ID, 'type':'custom'})
    edges.append({'id':'e4', 'source':ITERATION_START_ID, 'target':INNER_LLM_ID, 'type':'custom', 'data':{'isInIteration':True, 'iteration_id':ITERATION_ID}})
    edges.append({'id':'e5', 'source':ITERATION_ID, 'target':'end', 'type':'custom'})

    # 7. Final nodes
    new_nodes = [n for n in nodes if n['id'] != 'llm_generator' and n['id'] != 'end']
    
    end_node = {
        'data': {
            'desc': '',
            'outputs': [{'value_selector': [ITERATION_ID, 'output'], 'variable': 'result'}],
            'title': '结束',
            'type': 'end'
        },
        'id': 'end', 'height': 100, 'width': 244,
        'position': {'x': 2400, 'y': 250},
        'positionAbsolute': {'x': 2400, 'y': 250},
        'type': 'custom'
    }

    new_nodes.extend([task_splitter, json_parser, iteration_node, iteration_start, inner_llm, end_node])
    
    dsl['workflow']['graph']['nodes'] = new_nodes
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_parallel_v6_fixed.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Fixed DSL (v6) generated.")

if __name__ == "__main__":
    refactor()
