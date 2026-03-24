import yaml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    dsl['version'] = '0.3.1'
    dsl['workflow']['graph']['nodes'] = []
    dsl['workflow']['graph']['edges'] = []

    # Node IDs
    START_ID = 'start'
    RULES_ID = 'code_constraint'
    EXPERT_ID = 'llm_expert_r1'
    SPLITTER_ID = 'llm_splitter_v3'
    PARSER_ID = 'code_json_parser'
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_generator_v3'
    ITERATION_START_ID = ITERATION_ID + 'start'
    END_ID = 'end'

    # --- 1. Nodes Definitions ---

    # Start Node
    start_node = {
        'data': {
            'desc': '获取出题参数',
            'title': '开始',
            'type': 'start',
            'variables': [
                {'label': '目标职业', 'max_length': 200, 'required': True, 'type': 'text-input', 'variable': 'profession'},
                {'label': '知识点', 'max_length': 48000, 'required': True, 'type': 'paragraph', 'variable': 'topic'},
                {'label': '题型', 'max_length': 200, 'options': ['单选题', '多选题', '判断题', '简答题'], 'required': True, 'type': 'select', 'variable': 'question_type'},
                {'label': '难度', 'max_length': 200, 'options': ['简单', '中等', '困难', '专家级'], 'required': True, 'type': 'select', 'variable': 'difficulty'},
                {'label': '数量', 'max_length': 10, 'required': True, 'type': 'text-input', 'variable': 'question_count'}
            ]
        },
        'id': START_ID, 'type': 'custom', 'position': {'x': 80, 'y': 282}, 'width': 244, 'height': 312
    }

    # Code Node 1: Rules
    code_rules = {
        'data': {
            'code': "def main(qtype):\n    rules = \"【最高优先级规则锁】：请严格按照用户要求的题型出题。\"\n    if \"单选题\" in qtype: rules = \"【规则锁】：你必须且只能输出“单项选择题”。包含 A、B、C、D 四个选项，且只有一个正确答案。\"\n    elif \"多选题\" in qtype: rules = \"【规则锁】：你必须且只能输出“多项选择题”。包含 A、B、C、D 等选项，至少两个正确答案。\"\n    elif \"判断题\" in qtype: rules = \"【规则锁】：你必须且只能输出“判断题”。只能对题干情境提供“正确”或“错误”的判断。\"\n    elif \"简答题\" in qtype: rules = \"【规则锁】：你必须且只能输出“简答题”。给出详细的论述型解答。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3', # REQUIRED
            'desc': '获取约束词',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '题型规则 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': RULES_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    # LLM Node 1: Expert (R1)
    expert_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []}, # REQUIRED
            'vision': {'enabled': False}, # REQUIRED
            'memory': None, # REQUIRED
            'desc': '专家架构',
            'model': {
                'completion_params': {'temperature': 0.6, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-R1',
                'provider': 'siliconflow'
            },
            'prompt_template': [{'id': 'v11-r1', 'role': 'system', 'text': '你是一位最顶级的命题专家。针对主题【{{topic}}】和职业背景【{{profession}}】，撰写一份2500字以上的深度蓝图。包含底层逻辑推导及行业前沿挑战。要求全中文。'}],
            'title': '1. 专家蓝图 (R1)',
            'type': 'llm',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': EXPERT_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 98
    }

    # LLM Node 2: Splitter (V3)
    splitter_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False},
            'memory': None,
            'desc': '任务拆解',
            'model': {
                'completion_params': {'temperature': 0.1, 'max_tokens': 1000},
                'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [{'id': 'v11-s', 'role': 'system', 'text': '基于专家蓝图：\n{{blueprint}}\n将任务精准拆解为 {{count}} 个深度考核维度。输出 JSON 数组格式。例如：["维度1：案例背景A", "维度2：案例背景B"]'}],
            'title': '2. 维度拆解 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [EXPERT_ID, 'text'], 'variable': 'blueprint'},
                {'value_selector': [START_ID, 'question_count'], 'variable': 'count'}
            ]
        },
        'id': SPLITTER_ID, 'type': 'custom', 'position': {'x': 700, 'y': 450}, 'width': 244, 'height': 98
    }

    # Code Node 2: JSON Parser
    json_parser = {
        'data': {
            'code': "import json\ndef main(text):\n    text = text.strip()\n    if text.startswith('```json'): text = text[7:]\n    if text.startswith('```'): text = text[3:]\n    if text.endswith('```'): text = text[:-3]\n    try: return {'list': json.loads(text.strip())}\n    except: return {'list': [text]}",
            'code_language': 'python3', # FIXED: PREVIOUSLY MISSING
            'desc': 'JSON转换',
            'outputs': {'list': {'type': 'array[string]'}},
            'title': '3. 格式工厂 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SPLITTER_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    # Iteration Node
    iteration_node = {
        'data': {
            'desc': '题目并行生成器',
            'iterator_selector': [PARSER_ID, 'list'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '4. 题目快速工厂',
            'type': 'iteration',
            'variables': [
                {'value_selector': [RULES_ID, 'strict_rules'], 'variable': 'rules'},
                {'value_selector': [EXPERT_ID, 'text'], 'variable': 'blueprint'},
                {'value_selector': [START_ID, 'difficulty'], 'variable': 'diff'}
            ]
        },
        'id': ITERATION_ID, 'type': 'custom', 'position': {'x': 1300, 'y': 250}, 'width': 450, 'height': 300
    }

    iteration_start = {
        'data': {'isInIteration': True, 'type': 'iteration-start'},
        'id': ITERATION_START_ID, 'parentId': ITERATION_ID, 'position': {'x': 20, 'y': 100}, 'type': 'custom-iteration-start', 'width': 44, 'height': 48, 'zIndex': 1001
    }

    # LLM Node 3: Generator (V3)
    inner_llm = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False},
            'memory': None,
            'isInIteration': True,
            'model': {
               'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
               'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [{'id': 'v11-i', 'role': 'system', 'text': '{{rules}}\n\n蓝图参考：{{blueprint}}\n考核子项：{{task}}\n\n请针对该项生成 1 道极致专业的【{{diff}}】级题目。包含深度剥洋葱式解析。'}],
            'title': '顶级命题专家 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [RULES_ID, 'strict_rules'], 'variable': 'rules'},
                {'value_selector': [EXPERT_ID, 'text'], 'variable': 'blueprint'},
                {'value_selector': [ITERATION_ID, 'item'], 'variable': 'task'},
                {'value_selector': [START_ID, 'difficulty'], 'variable': 'diff'}
            ]
        },
        'id': INNER_LLM_ID, 'parentId': ITERATION_ID, 'position': {'x': 120, 'y': 80}, 'type': 'custom', 'width': 244, 'height': 98, 'zIndex': 1001
    }

    # End Node
    end_node = {
        'data': {
            'desc': '输出结果',
            'outputs': [{'value_selector': [ITERATION_ID, 'output'], 'variable': 'final_output'}],
            'title': '结束',
            'type': 'end'
        },
        'id': END_ID, 'type': 'custom', 'position': {'x': 1850, 'y': 350}, 'width': 244, 'height': 100
    }

    # --- 2. Edges ---
    edges = [
        {'id': 'e1', 'source': START_ID, 'target': RULES_ID, 'type': 'custom'},
        {'id': 'e2', 'source': START_ID, 'target': EXPERT_ID, 'type': 'custom'},
        {'id': 'e3', 'source': EXPERT_ID, 'target': SPLITTER_ID, 'type': 'custom'},
        {'id': 'e4', 'source': SPLITTER_ID, 'target': PARSER_ID, 'type': 'custom'},
        {'id': 'e5', 'source': PARSER_ID, 'target': ITERATION_ID, 'type': 'custom'},
        {'id': 'e6', 'source': RULES_ID, 'target': ITERATION_ID, 'type': 'custom'},
        {'id': 'e7', 'source': EXPERT_ID, 'target': ITERATION_ID, 'type': 'custom'},
        {'id': 'e8', 'source': START_ID, 'target': ITERATION_ID, 'type': 'custom'},
        {'id': 'e9', 'source': ITERATION_START_ID, 'target': INNER_LLM_ID, 'type': 'custom', 'data': {'isInIteration': True, 'iteration_id': ITERATION_ID}},
        {'id': 'e10', 'source': ITERATION_ID, 'target': END_ID, 'type': 'custom'}
    ]

    dsl['workflow']['graph']['nodes'] = [start_node, code_rules, expert_node, splitter_node, json_parser, iteration_node, iteration_start, inner_llm, end_node]
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_final_v11.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final Validated DSL v11 generated.")

if __name__ == "__main__":
    refactor()
