import yaml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    dsl['version'] = '0.3.1'
    dsl['workflow']['graph']['nodes'] = []
    dsl['workflow']['graph']['edges'] = []

    # Node IDs
    START_ID = 'start'
    CODE_RULES_ID = 'code_constraint'
    KNOWLEDGE_ID = 'llm_knowledge_specialist'
    SCENARIO_ID = 'llm_scenario_architect'
    PARSER_ID = 'code_json_parser'
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_single_generator'
    ITERATION_START_ID = ITERATION_ID + 'start'
    END_ID = 'end'

    # --- 1. Nodes Definitions ---

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

    code_rules = {
        'data': {
            'code': "def main(qtype):\n    rules = \"【最高优先级安全锁】：请严格按照用户要求的题型出题。\"\n    if \"单选题\" in qtype: rules = \"【安全锁】：你必须且只能输出“单项选择题”。包含 A、B、C、D 四个选项，且只有一个正确答案。\"\n    elif \"多选题\" in qtype: rules = \"【安全锁】：你必须且只能输出“多项选择题”。包含 A、B、C、D 等选项，至少两个正确答案。\"\n    elif \"判断题\" in qtype: rules = \"【安全锁】：你必须且只能输出“判断题”。只能对题干情境提供“正确”或“错误”的判断。\"\n    elif \"简答题\" in qtype: rules = \"【安全锁】：你必须且只能输出“简答题”。直接给出论述型解答。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3',
            'desc': '格式约束词生成',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '题型规则锁 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': CODE_RULES_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    # Added required fields: context, vision, memory
    knowledge_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False},
            'memory': None,
            'desc': '深度知识蓝图合成',
            'model': {
                'completion_params': {'temperature': 0.6, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-R1',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'k-sys',
                    'role': 'system',
                    'text': '你是一位拥有30年行业经验的【{{profession}}】领域专家。针对主题【{{topic}}】，请撰写一份极其详尽的“深度考点蓝图”。包含该知识点的逻辑推导过程、最前沿的行业业务标准、3-5个高难度的实战应用坑点、以及相关的国家或国际标准。要求内容深度足以支撑专家级出题，篇幅在2000字以上。'
                }
            ],
            'title': '1. 深度考点蓝图 (R1)',
            'type': 'llm',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': KNOWLEDGE_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 98
    }

    scenario_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False},
            'memory': None,
            'desc': '实战业务场景设计',
            'model': {
                'completion_params': {'temperature': 0.3, 'max_tokens': 1000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-V3',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 's-sys',
                    'role': 'system',
                    'text': '基于提供的【深度考点蓝图】：\n{{dossier}}\n\n请设计 {{count}} 个高度贴合实际生产环境的业务场景描述。每个场景应包含具体的故障、业务需求或技术决策难点。**仅以 JSON 数组格式输出**，确保 Dify 能够解析。\n例如: ["场景A: ...", "场景B: ..."]'
                }
            ],
            'title': '2. 业务场景设计 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [KNOWLEDGE_ID, 'text'], 'variable': 'dossier'},
                {'value_selector': [START_ID, 'question_count'], 'variable': 'count'}
            ]
        },
        'id': SCENARIO_ID, 'type': 'custom', 'position': {'x': 700, 'y': 450}, 'width': 244, 'height': 98
    }

    json_parser = {
        'data': {
            'code': "import json\ndef main(text):\n    text = text.strip()\n    if text.startswith('```json'): text = text[7:]\n    if text.startswith('```'): text = text[3:]\n    if text.endswith('```'): text = text[:-3]\n    try: return {'list': json.loads(text.strip())}\n    except: return {'list': [text]}",
            'code_language': 'python3',
            'desc': 'JSON转换',
            'outputs': {'list': {'type': 'array[string]'}},
            'title': '3. 格式工厂 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SCENARIO_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    iteration_node = {
        'data': {
            'desc': '循环生成题目',
            'iterator_selector': [PARSER_ID, 'list'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '4. 题目并行生成器',
            'type': 'iteration'
        },
        'id': ITERATION_ID, 'type': 'custom', 'position': {'x': 1300, 'y': 250}, 'width': 450, 'height': 300
    }

    iteration_start = {
        'data': {'isInIteration': True, 'type': 'iteration-start'},
        'id': ITERATION_START_ID, 'parentId': ITERATION_ID, 'position': {'x': 20, 'y': 100}, 'type': 'custom-iteration-start', 'width': 44, 'height': 48, 'zIndex': 1001
    }

    inner_generator = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False},
            'memory': None,
            'isInIteration': True,
            'model': {
                'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-V3',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'i-sys',
                    'role': 'system',
                    'text': '{{rules}}\n\n深度蓝图参考：{{dossier}}\n\n本次场景：{{scene}}\n\n请针对该场景生成 1 道难度为【{{diff}}】的题目。必须包含题干、选项、答案和极其深度的解析（含错项干扰逻辑分析）。输出必须为专业中文。'
                }
            ],
            'title': '单题生成器',
            'type': 'llm',
            'variables': [
                {'value_selector': [CODE_RULES_ID, 'strict_rules'], 'variable': 'rules'},
                {'value_selector': [KNOWLEDGE_ID, 'text'], 'variable': 'dossier'},
                {'value_selector': [ITERATION_ID, 'item'], 'variable': 'scene'},
                {'value_selector': [START_ID, 'difficulty'], 'variable': 'diff'}
            ]
        },
        'id': INNER_LLM_ID, 'parentId': ITERATION_ID, 'position': {'x': 120, 'y': 80}, 'type': 'custom', 'width': 244, 'height': 98, 'zIndex': 1001
    }

    end_node = {
        'data': {
            'desc': '输出题库',
            'outputs': [{'value_selector': [ITERATION_ID, 'output'], 'variable': 'result'}],
            'title': '结束',
            'type': 'end'
        },
        'id': END_ID, 'type': 'custom', 'position': {'x': 1850, 'y': 350}, 'width': 244, 'height': 100
    }

    # --- 2. Edges ---
    edges = [
        {'id': 'e1', 'source': START_ID, 'target': CODE_RULES_ID, 'type': 'custom'},
        {'id': 'e2', 'source': START_ID, 'target': KNOWLEDGE_ID, 'type': 'custom'},
        {'id': 'e3', 'source': KNOWLEDGE_ID, 'target': SCENARIO_ID, 'type': 'custom'},
        {'id': 'e4', 'source': SCENARIO_ID, 'target': PARSER_ID, 'type': 'custom'},
        {'id': 'e5', 'source': PARSER_ID, 'target': ITERATION_ID, 'type': 'custom'},
        {'id': 'e6', 'source': CODE_RULES_ID, 'target': ITERATION_ID, 'type': 'custom', 'data': {'isInIteration': False}}, # Ensuring data exists
        {'id': 'e7', 'source': ITERATION_START_ID, 'target': INNER_LLM_ID, 'type': 'custom', 'data': {'isInIteration': True, 'iteration_id': ITERATION_ID}},
        {'id': 'e8', 'source': ITERATION_ID, 'target': END_ID, 'type': 'custom'}
    ]

    # --- 3. Graph Assembly ---
    nodes_all = [start_node, code_rules, knowledge_node, scenario_node, json_parser, iteration_node, iteration_start, inner_generator, end_node]
    dsl['workflow']['graph']['nodes'] = nodes_all
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_expert_v8_fixed.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final Expert DSL v8 (Fixed Context) generated.")

if __name__ == "__main__":
    refactor()
