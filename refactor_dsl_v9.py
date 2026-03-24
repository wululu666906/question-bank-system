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
            'code': "def main(qtype):\n    rules = \"【最高优先级规则锁】：请严格按照用户要求的题型出题。\"\n    if \"单选题\" in qtype: rules = \"【规则锁】：你必须且只能输出“单项选择题”。包含 A、B、C、D 四个选项，且只有一个正确答案。\"\n    elif \"多选题\" in qtype: rules = \"【规则锁】：你必须且只能输出“多项选择题”。包含 A、B、C、D 等选项，至少两个正确答案。\"\n    elif \"判断题\" in qtype: rules = \"【规则锁】：你必须且只能输出“判断题”。只能对题干情境提供“正确”或“错误”的判断。\"\n    elif \"简答题\" in qtype: rules = \"【规则锁】：你必须且只能输出“简答题”。给出详细的论述型解答。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3',
            'desc': '强制格式约束',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '题型约束锁 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': RULES_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    # 1. Expert Architect (R1) - Synthesis
    expert_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '使用思考模型构建深层知识架构',
            'model': {
                'completion_params': {'temperature': 0.6, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-R1',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v9-exp-sys',
                    'role': 'system',
                    'text': '你是一位拥有30年命题经验的顶级行业专家。针对主题【{{topic}}】和职业背景【{{profession}}】，请撰写一份极其专业的“全维度命题蓝图”。\n\n要求：\n1. 深度推导：分析该知识点的底层逻辑、演进历程和核心难点。\n2. 实战穿透：结合最新行业动态，列出5个真实的业务痛点、决策难点或技术争议点。\n3. 高阶知识点：挖掘那些容易被忽视的“角落知识”和“复合交叉点”。\n4. 篇幅要求：2000字以上，确保具备极高的专业性和前瞻性。'
                }
            ],
            'title': '1. 专家知识架构 (R1)',
            'type': 'llm',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': EXPERT_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 98
    }

    # 2. Task Dimension Splitter (V3)
    splitter_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '将蓝图拆解为互不重复的命题任务',
            'model': {
                'completion_params': {'temperature': 0.1, 'max_tokens': 1000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-V3',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v9-split-sys',
                    'role': 'system',
                    'text': '基于以下专家蓝图：\n{{blueprint}}\n\n请将其拆分为 {{count}} 个**绝对独立、互不重叠**的命题任务子项。每个子项必须包含：1. 具体的考核维度；2. 针对性的业务案例背景。\n\n**输出要求**：请仅输出一个合法的 JSON 字符数组，不要回复任何多余文字。例如：["维度A：案例背景B", "维度C：案例背景D"]'
                }
            ],
            'title': '2. 命题维度拆解 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [EXPERT_ID, 'text'], 'variable': 'blueprint'},
                {'value_selector': [START_ID, 'question_count'], 'variable': 'count'}
            ]
        },
        'id': SPLITTER_ID, 'type': 'custom', 'position': {'x': 700, 'y': 450}, 'width': 244, 'height': 98
    }

    # 3. JSON Parser (Code)
    json_parser = {
        'data': {
            'code': "import json\ndef main(text):\n    text = text.strip()\n    if text.startswith('```json'): text = text[7:]\n    if text.startswith('```'): text = text[3:]\n    if text.endswith('```'): text = text[:-3]\n    try: return {'list': json.loads(text.strip())}\n    except: return {'list': [text]}",
            'outputs': {'list': {'type': 'array[string]'}},
            'title': '3. 格式安全网 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [SPLITTER_ID, 'text'], 'variable': 'text'}]
        },
        'id': PARSER_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    # 4. Iteration Node
    iteration_node = {
        'data': {
            'iterator_selector': [PARSER_ID, 'list'],
            'output_selector': [INNER_LLM_ID, 'text'],
            'start_node_id': ITERATION_START_ID,
            'title': '4. 题目快速工厂 (并行)',
            'type': 'iteration'
        },
        'id': ITERATION_ID, 'type': 'custom', 'position': {'x': 1300, 'y': 250}, 'width': 450, 'height': 300
    }

    # 5. Iteration Start
    iteration_start = {
        'data': {'isInIteration': True, 'type': 'iteration-start'},
        'id': ITERATION_START_ID, 'parentId': ITERATION_ID, 'position': {'x': 20, 'y': 100}, 'type': 'custom-iteration-start', 'width': 44, 'height': 48, 'zIndex': 1001
    }

    # 6. Final Question Maker (V3)
    inner_llm = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'isInIteration': True,
            'model': {
                'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
                'mode': 'chat',
                'name': 'deepseek-ai/DeepSeek-V3',
                'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'v9-inner-sys',
                    'role': 'system',
                    'text': '{{rules}}\n\n参考专家蓝图：{{blueprint}}\n本次考核子项：{{task}}\n\n请针对该具体任务，生成 1 道难度级别为【{{diff}}】的极致专业题目。要求：\n1. 内容必须为行业级实战难题。\n2. 包含：题干、选项（如果是选择题）、正确答案、以及极具深度的“剥洋葱式”解析（包括错误选项的逻辑诱导分析）。\n3. 采用 Markdown 完美排版，确保输出为专业中文。'
                }
            ],
            'title': '顶级命题人 (V3)',
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

    # 7. End
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
        {'id': 'e6', 'source': RULES_ID, 'target': ITERATION_ID, 'type': 'custom', 'data': {'isInIteration': False}},
        {'id': 'e7', 'source': ITERATION_START_ID, 'target': INNER_LLM_ID, 'type': 'custom', 'data': {'isInIteration': True, 'iteration_id': ITERATION_ID}},
        {'id': 'e8', 'source': ITERATION_ID, 'target': END_ID, 'type': 'custom'}
    ]

    dsl['workflow']['graph']['nodes'] = [start_node, code_rules, expert_node, splitter_node, json_parser, iteration_node, iteration_start, inner_llm, end_node]
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_v9_production.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Final Production DSL v9 generated.")

if __name__ == "__main__":
    refactor()
