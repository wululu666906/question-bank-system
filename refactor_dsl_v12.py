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
    EXPERT_ID = 'llm_expert_r1_architect'
    SPLITTER_ID = 'llm_splitter_v3_strategic'
    PARSER_ID = 'code_json_parser'
    ITERATION_ID = 'iteration_generator'
    INNER_LLM_ID = 'llm_master_generator_v3'
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
            'code': "def main(qtype):\n    rules = \"【核心格式锁】：严格遵循指定题型。\"\n    if \"单选题\" in qtype: rules += \"\\n1. 只能是单项选择题。\\n2. A/B/C/D 四选项。\\n3. 唯一正解。\"\n    elif \"多选题\" in qtype: rules += \"\\n1. 只能是多项选择题。\\n2. 至少两个正解。\"\n    elif \"判断题\" in qtype: rules += \"\\n1. 只能是真/假判断。\"\n    elif \"简答题\" in qtype: rules += \"\\n1. 论述型问法。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3',
            'desc': '题型预处理器',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '题型约束锁定 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': RULES_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    expert_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '知识架构师 (R1)',
            'model': {
               'completion_params': {'temperature': 0.6, 'max_tokens': 4000},
               'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-R1', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v12-r1-sys',
                    'role': 'system',
                    'text': '你是一位融合了“认知心理学”与“行业顶级实战经验”的【知识架构大师】。针对主题【{{topic}}】和职业背景【{{profession}}】，请输出一份极具深度的“认知知识蓝图”。\n\n要求（3500字以上）：\n1. 【底层逻辑推演】：不要罗列书本定义，要推导该知识如何在复杂的商业/技术系统中流转，并分析其“第一性原理”。\n2. 【灰色地带与悖论】：挖掘行业中最具争议、最模棱两可、最考验专家直觉的5个“灰色场景”。这些将是极品题目的灵感来源。\n3. 【逻辑陷阱库】：分析新手、进阶者和资深者在该领域最容易产生的认知偏差（Cognitive Bias）及其诱导根源。\n4. 【实战颗粒度】：补充至少10个该职业在处理此知识点时的具体参数、边界条件或异常监控点。\n\n**目标输出必须是专业中文，具备极强的学术性与实战压迫感。**'
                }
            ],
            'title': '1. 认知专家蓝图 (R1)',
            'type': 'llm',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': EXPERT_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 98
    }

    splitter_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '命题策略官 (V3)',
            'model': {
                'completion_params': {'temperature': 0.1, 'max_tokens': 1000},
                'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v12-split-sys',
                    'role': 'system',
                    'text': '你是一位遵循“MECE原则”且精通“布鲁姆教育目标分类法”的顶级命题策略官。\n\n基于以下蓝图：\n{{blueprint}}\n\n请将其拆解为 {{count}} 个**彼此绝对独立、层级互补**的命题挑战向量。每个挑战向量必须包含：\n1. 考核维度（如：逻辑归纳、异常诊断、效能优化等）。\n2. 高频诱导场景（基于蓝图中的灰色地带）。\n3. 考核核心（该点为什么难）。\n\n**输出格式**：请仅输出一个合法的 JSON 字符数组，内容为具体的挑战描述。例如：["考核维度：XXX；实战场景：YYY；逻辑锚点：ZZZ", "..."]。禁止任何解释性文字。'
                }
            ],
            'title': '2. 战略维度拆解 (V3)',
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
            'desc': 'JSON格式化',
            'outputs': {'list': {'type': 'array[string]'}},
            'title': '3. 格式工厂 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SPLITTER_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    iteration_node = {
        'data': {
            'desc': '题目并行生产工厂',
            'iterator_selector': [PARSER_ID, 'list'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '4. 顶级题目工厂 (并行)',
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
                    'id': 'v12-inner-sys',
                    'role': 'system',
                    'text': '{{rules}}\n\n参考专家蓝图：{{blueprint}}\n本次考核挑战向量：{{task}}\n目标难度：【{{diff}}】\n\n请针对该挑战向量，生成 1 道足以震慑行业专家的“压轴级”题目。要求：\n1. 【高掩护选项】：如果是选择题，选项 A、B、C、D 必须极具迷惑性（Plausible Distractor）。其中两项应针对常见的“半懂不懂”认知陷阱设计，另一项应针对“逻辑过度外推”设计。\n2. 【专业题干】：采用高度专业化、沉浸式的业务语言，避免口语化。\n3. 【核心输出：剥洋葱式深析 (Peel-the-Onion Analysis)】（500字以上）：\n   - 第1层：命题立意（考核什么能力）。\n   - 第2层：实战逻辑陷阱拆解（考生为什么会选错，错在哪里）。\n   - 第3层：排除法精髓（如何剔除干扰项）。\n   - 第4层：底层原理校准（该知识点在系统中的正确角色）。\n   - 第5层：进阶思考点（如果场景参数变化，答案会如何转变）。\n\n**采用极致简约且美观的 Markdown 语法进行排版。**'
                }
            ],
            'title': '顶级命题教授 (V3)',
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

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_v12_quality_boost.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final Premium DSL v12 generated.")

if __name__ == "__main__":
    refactor()
