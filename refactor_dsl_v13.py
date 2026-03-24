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
    EXPERT_ID = 'llm_industry_advisor'
    SPLITTER_ID = 'llm_topic_splitter'
    PARSER_ID = 'code_json_parser'
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_question_builder'
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
                {'label': '知识点/素材', 'max_length': 48000, 'required': True, 'type': 'paragraph', 'variable': 'topic'},
                {'label': '题型', 'max_length': 200, 'options': ['单选题', '多选题', '判断题', '简答题'], 'required': True, 'type': 'select', 'variable': 'question_type'},
                {'label': '难度', 'max_length': 200, 'options': ['简单', '中等', '困难', '专家级'], 'required': True, 'type': 'select', 'variable': 'difficulty'},
                {'label': '数量', 'max_length': 10, 'required': True, 'type': 'text-input', 'variable': 'question_count'}
            ]
        },
        'id': START_ID, 'type': 'custom', 'position': {'x': 80, 'y': 282}, 'width': 244, 'height': 312
    }

    code_rules = {
        'data': {
            'code': "def main(qtype):\n    rules = \"【格式要求】：请输出标准专业题目格式。\"\n    if \"单选题\" in qtype: rules += \"\\n1. 单项选择题（A/B/C/D四个选项）。\"\n    elif \"多选题\" in qtype: rules += \"\\n1. 多项选择题（多选）。\"\n    elif \"判断题\" in qtype: rules += \"\\n1. 判断题（正确/错误）。\"\n    elif \"简答题\" in qtype: rules += \"\\n1. 简答题（详细解析）。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3',
            'desc': '基础约束',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '规则预处理 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': RULES_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    # Expert Advisor (R1)
    expert_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '跨行业知识顾问 (R1)',
            'model': {
               'completion_params': {'temperature': 0.6, 'max_tokens': 4000},
               'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-R1', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v13-r1-sys',
                    'role': 'system',
                    'text': '你是一位博学且务实的【跨行业知识专家】。你的任务是精准理解用户输入的【{{topic}}】及职业背景【{{profession}}】，并从中提炼出核心考点。\n\n要求：\n1. 深度分析：听懂用户的问题，找出用户素材中的隐性逻辑和核心知识点。\n2. 知识萃取：将素材改编为适合命题的专业考点库。如果用户提供的素材较少，请利用你的专业知识进行合理补充和垂直深度挖掘。\n3. 专业性：确保所有分析符合【{{profession}}】的行业标准和通用术语。\n\n**输出一份详尽且专业的“行业命题指南”，为后续出题提供高质量参考。**'
                }
            ],
            'title': '1. 行业知识指南 (R1)',
            'type': 'llm',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': EXPERT_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 98
    }

    # Topic Splitter (V3)
    splitter_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '命题维度分拆 (V3)',
            'model': {
                'completion_params': {'temperature': 0.1, 'max_tokens': 1000},
                'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v13-split-sys',
                    'role': 'system',
                    'text': '基于提供的行业命题指南：\n{{blueprint}}\n\n请将其拆解为 {{count}} 个具体的、互不重复的命题维度。\n\n要求：\n1. 垂直细分：每个维度必须对应一个具体的知识应用场景。\n2. 独立性：确保题目之间没有逻辑重叠。\n\n**输出格式**：仅输出一个 JSON 字符数组。例如：["维度A：XXX场景应用", "维度B：YYY逻辑判断"]。'
                }
            ],
            'title': '2. 题目维度分拆 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [EXPERT_ID, 'text'], 'variable': 'blueprint'},
                {'value_selector': [START_ID, 'question_count'], 'variable': 'count'}
            ]
        },
        'id': SPLITTER_ID, 'type': 'custom', 'position': {'x': 700, 'y': 450}, 'width': 244, 'height': 98
    }

    json_parser = {
        'data': {
            'code': "import json\ndef main(text):\n    text = text.strip()\n    if text.startswith('```json'): text = text[7:]\n    if text.startswith('```'): text = text[3:]\n    if text.endswith('```'): text = text[:-3]\n    try: return {'list': json.loads(text.strip())}\n    except: return {'list': [text]}",
            'code_language': 'python3',
            'desc': '数据格式化',
            'outputs': {'list': {'type': 'array[string]'}},
            'title': '3. 格式化工具 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SPLITTER_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    iteration_node = {
        'data': {
            'desc': '题目快速生产流水线',
            'iterator_selector': [PARSER_ID, 'list'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '4. 题目快速工厂 (并行)',
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

    # Question Builder (V3)
    inner_llm = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'isInIteration': True,
            'model': {
               'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
               'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v13-inner-sys',
                    'role': 'system',
                    'text': '{{rules}}\n\n参考指南：{{blueprint}}\n当前维度：{{task}}\n难度：【{{diff}}】\n\n请针对该维度生成 1 道专业的行业题目。要求：\n1. 改编与重构：根据指南中的知识点，结合实际行业场景改编出题。确保题目严谨、无歧义。\n2. 排版清晰：使用标准 Markdown 格式。包含：题干、选项、正确答案、详细解析。\n3. 解析深度：解析要讲清楚逻辑，指导考生理解核心原理。\n4. 无杂质：严禁输出任何特殊符号、表情包或无关赘述。'
                }
            ],
            'title': '专业命题人 (V3)',
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

    end_node = {
        'data': {
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

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_v13_practical.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final Practical DSL v13 generated.")

if __name__ == "__main__":
    refactor()
