import yaml
import json

# Ensure we use the correct structure for Dify 0.1.x / 0.3.x Iteration nodes
# Based on c:\Users\Auraa\Desktop\题库\dify-repo\api\tests\fixtures\workflow\array_iteration_formatting_workflow.yml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    # Change version to a more stable one if needed, but let's keep it or move to 0.3.1
    dsl['version'] = '0.1.3' 

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
                    'text': '你是一个出题专家。\n用户要求生成 {{#start.question_count#}} 道关于【{{#start.topic#}}】的题目。\n请参照背景：{{#tool_firecrawl.text#}}\n\n请将任务拆分为 {{#start.question_count#}} 个独立的知识点/题目大纲。\n**仅输出一个 JSON 字符数组**，例如: ["考点A: 场景B", "考点C: 场景D"]。不要回复任何多余文字。'
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
                    'text': '{{#code_constraint.strict_rules#}}\n\n参考：{{#tool_firecrawl.text#}}\n\n当前任务：{{#iteration.item#}}\n\n请围绕该任务生成 1 道难度为【{{#start.difficulty#}}】的题目。包含：题目、选项、答案、深度解析。'
                }
            ],
            'title': '单题生成器',
            'type': 'llm',
            'variables': []
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

    # tool_firecrawl -> splitter
    edges.append({
        'data': {'isInIteration': False, 'sourceType': 'tool', 'targetType': 'llm'},
        'id': 'edge-fire-split',
        'source': 'tool_firecrawl',
        'sourceHandle': 'source',
        'target': SPLITTER_ID,
        'targetHandle': 'target',
        'type': 'custom'
    })

    # splitter -> iteration
    edges.append({
        'data': {'isInIteration': False, 'sourceType': 'llm', 'targetType': 'iteration'},
        'id': 'edge-split-iter',
        'source': SPLITTER_ID,
        'sourceHandle': 'source',
        'target': ITERATION_ID,
        'targetHandle': 'target',
        'type': 'custom'
    })
    
    # iteration-start -> inner_llm
    edges.append({
        'data': {'isInIteration': True, 'iteration_id': ITERATION_ID, 'sourceType': 'iteration-start', 'targetType': 'llm'},
        'id': 'edge-iterstart-inner',
        'source': ITERATION_START_ID,
        'sourceHandle': 'source',
        'target': INNER_LLM_ID,
        'targetHandle': 'target',
        'type': 'custom'
    })

    # iteration -> end
    edges.append({
        'data': {'isInIteration': False, 'sourceType': 'iteration', 'targetType': 'end'},
        'id': 'edge-iter-end',
        'source': ITERATION_ID,
        'sourceHandle': 'source',
        'target': 'end',
        'targetHandle': 'target',
        'type': 'custom'
    })

    # 6. Final graph assembly
    # Remove old llm_generator node
    new_nodes = [n for n in nodes if n['id'] != 'llm_generator']
    
    # Update End node output
    for node in new_nodes:
        if node['id'] == 'end':
            node['data']['outputs'] = [{
                'value_selector': [ITERATION_ID, 'output'],
                'variable': 'result'
            }]
            node['position']['x'] = 2200

    new_nodes.extend([task_splitter, iteration_node, iteration_start, inner_llm])
    
    dsl['workflow']['graph']['nodes'] = new_nodes
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl_v4_parallel_fixed.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Fixed DSL generated: question_factory_script_dsl_v4_parallel_fixed.yml")

if __name__ == "__main__":
    refactor()
