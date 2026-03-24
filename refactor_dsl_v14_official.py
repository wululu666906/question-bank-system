import yaml

def refactor():
    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_script_dsl.yml', 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    dsl['version'] = '0.3.1'
    dsl['workflow']['graph']['nodes'] = []
    dsl['workflow']['graph']['edges'] = []

    # Node IDs
    START_ID = 'start'
    LOCK_ID = 'code_format_lock'
    GOOGLE_ID = 'tool_google_search'
    EXTRACTOR_ID = 'code_url_extractor'
    FIRECRAWL_ID = 'tool_firecrawl'
    LLM_ID = 'llm_official_generator'
    END_ID = 'end'

    # --- 1. Nodes Definitions ---

    start_node = {
        'data': {
            'desc': '接收用户输入的中文知识点及出题参数',
            'title': '开始',
            'type': 'start',
            'variables': [
                {'label': '目标职业/岗位', 'max_length': 200, 'required': True, 'type': 'text-input', 'variable': 'profession'},
                {'label': '知识点内容', 'max_length': 48000, 'required': True, 'type': 'paragraph', 'variable': 'topic'},
                {'label': '题型选择', 'max_length': 200, 'options': ['单选题', '多选题', '判断题', '简答题'], 'required': True, 'type': 'select', 'variable': 'question_type'},
                {'label': '难度级别', 'max_length': 200, 'options': ['简单', '中等', '困难', '专家级'], 'required': True, 'type': 'select', 'variable': 'difficulty'},
                {'label': '题目数量', 'max_length': 10, 'required': True, 'type': 'text-input', 'variable': 'question_count'}
            ]
        },
        'id': START_ID, 'type': 'custom', 'position': {'x': 80, 'y': 282}, 'width': 244, 'height': 312
    }

    # Left Orbit: Rule Lock
    lock_node = {
        'data': {
            'code': "def main(qtype):\n    rules = \"【最高优先级安全锁】：请严格按照用户要求的题型出题，拒绝输出不相关的题型。\"\n    if \"单选题\" in qtype:\n        rules += \"\\n你必须且只能输出“单项选择题”。每道题必须包含 A、B、C、D 四个选项，且只有一个正确答案。绝对不允许输出判断题、简答题或填空题，违规将导致系统崩溃。\"\n    elif \"多选题\" in qtype:\n        rules += \"\\n你必须且只能输出“多项选择题”。每道题必须包含 A、B、C、D 选项，且至少有两个正确答案。\"\n    elif \"判断题\" in qtype:\n        rules += \"\\n你必须且只能输出“判断题”。只能对题干情境提供“正确”或“错误”的判断。\"\n    elif \"简答题\" in qtype:\n        rules += \"\\n你必须且只能输出“简答题”。要求提供问题描述，并直接给出论述型解答。\"\n    return {\"strict_rules\": rules}",
            'code_language': 'python3',
            'desc': '0延时防格式幻觉安全锁',
            'outputs': {'strict_rules': {'type': 'string'}},
            'title': '1. 类型安全锁 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [START_ID, 'question_type'], 'variable': 'qtype'}]
        },
        'id': LOCK_ID, 'type': 'custom', 'position': {'x': 400, 'y': 150}, 'width': 244, 'height': 54
    }

    # Right Orbit: Google Search
    google_node = {
        'data': {
            'desc': '检索最新行业垂直资料',
            'provider_id': 'google',
            'provider_name': 'google',
            'provider_type': 'builtin',
            'tool_label': 'Google Search',
            'tool_name': 'google_search',
            'tool_parameters': {
                'query': '{{profession}} {{topic}} 最新官网快照 白皮书 行业规范'
            },
            'title': '2. 实时检索 (Google)',
            'type': 'tool',
            'variables': [
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'}
            ]
        },
        'id': GOOGLE_ID, 'type': 'custom', 'position': {'x': 400, 'y': 450}, 'width': 244, 'height': 54
    }

    # Right Orbit: URL Extractor
    extractor_node = {
        'data': {
            'code': "import json\ndef main(google_result):\n    try:\n        res = json.loads(google_result)\n        if res and len(res) > 0:\n            return {'url': res[0].get('link', '')}\n    except:\n        pass\n    return {'url': ''}",
            'code_language': 'python3',
            'desc': '提取搜索结果TOP 1链接',
            'outputs': {'url': {'type': 'string'}},
            'title': '3. 链接提取 (Code)',
            'type': 'code',
            'variables': [{'value_selector': [GOOGLE_ID, 'text'], 'variable': 'google_result'}]
        },
        'id': EXTRACTOR_ID, 'type': 'custom', 'position': {'x': 700, 'y': 450}, 'width': 244, 'height': 54
    }

    # Right Orbit: Firecrawl Scrape
    firecrawl_node = {
        'data': {
            'desc': '反爬虫深度脱壳提取Markdown',
            'provider_id': 'firecrawl',
            'provider_name': 'firecrawl',
            'provider_type': 'builtin',
            'tool_label': 'Firecrawl Scrape',
            'tool_name': 'scrape',
            'tool_parameters': {
                'url': '{{url}}',
                'pageOptions': {'onlyMainContent': True}
            },
            'title': '4. 内容抓取 (Firecrawl)',
            'type': 'tool',
            'variables': [{'value_selector': [EXTRACTOR_ID, 'url'], 'variable': 'url'}]
        },
        'id': FIRECRAWL_ID, 'type': 'custom', 'position': {'x': 1000, 'y': 450}, 'width': 244, 'height': 54
    }

    # Convergence: LLM Generator (DeepSeek-V3)
    llm_node = {
        'data': {
            'context': {'enabled': False, 'variable_selector': []},
            'vision': {'enabled': False}, 'memory': None,
            'desc': '全量吸收双轨流数据，执行最终命题',
            'model': {
               'completion_params': {'temperature': 0.7, 'max_tokens': 4000},
               'mode': 'chat', 'name': 'deepseek-ai/DeepSeek-V3', 'provider': 'siliconflow'
            },
            'prompt_template': [
                {
                    'id': 'official-v14-sys',
                    'role': 'system',
                    'text': '{{rules}}\n\n你是一位拥有20年实战经验的【{{profession}}】领域资深考官与终极培训专家。\n请结合以下通过强制反爬拿到的全网页硬核资料进行出题：\n【深度原网页参考资料】：\n{{crawler_content}}\n\n考点摘要：{{topic}}\n难度设定：{{difficulty}}\n题目数量：{{count}}\n\n【绝对红线指标】：\n1. 必须提供真实的行业业务场景作为题干背景，拒绝干瘪的纯理论问答，要求高度贴合实际工作。\n2. 若为选择题，干扰选项必须具有极强的迷惑性（针对业内的真实常见坑点设计）。\n3. 所有题目必须同时输出“深度解析”，逐项剖析错误选项的逻辑漏洞。\n4. 绝对禁止输出任何客套废话（如“好的”、“已收到”），直接开始输出题目 Markdown。\n5. 排版整洁清晰，无杂乱特殊符号。'
                }
            ],
            'title': '5. 核心命题大脑 (V3)',
            'type': 'llm',
            'variables': [
                {'value_selector': [LOCK_ID, 'strict_rules'], 'variable': 'rules'},
                {'value_selector': [START_ID, 'profession'], 'variable': 'profession'},
                {'value_selector': [START_ID, 'topic'], 'variable': 'topic'},
                {'value_selector': [START_ID, 'difficulty'], 'variable': 'difficulty'},
                {'value_selector': [START_ID, 'question_count'], 'variable': 'count'},
                {'value_selector': [FIRECRAWL_ID, 'text'], 'variable': 'crawler_content'}
            ]
        },
        'id': LLM_ID, 'type': 'custom', 'position': {'x': 1300, 'y': 250}, 'width': 244, 'height': 98
    }

    end_node = {
        'data': {
            'outputs': [{'value_selector': [LLM_ID, 'text'], 'variable': 'final_output'}],
            'title': '结束',
            'type': 'end'
        },
        'id': END_ID, 'type': 'custom', 'position': {'x': 1600, 'y': 350}, 'width': 244, 'height': 100
    }

    # --- 2. Edges ---
    edges = [
        {'id': 'e1', 'source': START_ID, 'target': LOCK_ID, 'type': 'custom'},
        {'id': 'e2', 'source': START_ID, 'target': GOOGLE_ID, 'type': 'custom'},
        {'id': 'e3', 'source': GOOGLE_ID, 'target': EXTRACTOR_ID, 'type': 'custom'},
        {'id': 'e4', 'source': EXTRACTOR_ID, 'target': FIRECRAWL_ID, 'type': 'custom'},
        {'id': 'e5', 'source': FIRECRAWL_ID, 'target': LLM_ID, 'type': 'custom'},
        {'id': 'e6', 'source': LOCK_ID, 'target': LLM_ID, 'type': 'custom'},
        {'id': 'e7', 'source': LLM_ID, 'target': END_ID, 'type': 'custom'}
    ]

    dsl['workflow']['graph']['nodes'] = [start_node, lock_node, google_node, extractor_node, firecrawl_node, llm_node, end_node]
    dsl['workflow']['graph']['edges'] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_official_v14.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Official Double Orbit DSL v14 generated.")

if __name__ == "__main__":
    refactor()
