import yaml

def generate_dsl():
    dsl = {
      "app": {
        "description": "集成了全球顶尖搜索引擎与Firecrawl反溯源防爬虫节点的专业级系统，确保获得最全面准确的前沿业务素材。",
        "icon": "🧠",
        "icon_background": "#E8F4FD",
        "mode": "workflow",
        "name": "智能题库生成系统(官方并行架构版)",
        "use_icon_as_answer_icon": False
      },
      "kind": "app",
      "version": "0.1.3",
      "workflow": {
        "features": {
          "file_upload": {"allowed_file_extensions": [".PDF", ".DOCX", ".TXT"], "allowed_file_types": ["document"], "allowed_file_upload_methods": ["local_file", "remote_url"], "enabled": False, "image": {"enabled": False, "number_limits": 3, "transfer_methods": ["local_file", "remote_url"]}, "max_length": 3, "number_limits": 3},
          "opening_statement": "",
          "retriever_resource": {"enabled": False},
          "sensitive_word_avoidance": {"enabled": False},
          "speech_to_text": {"enabled": False},
          "suggested_questions": [],
          "suggested_questions_after_answer": {"enabled": False},
          "text_to_speech": {"enabled": False, "language": "", "voice": ""}
        },
        "graph": {
            "nodes": [],
            "edges": []
        }
      }
    }

    START_ID = 'start'
    RULES_ID = 'code_format_lock'
    SYS_SEARCH_ID = 'tool_google_search'
    EXTRACTOR_ID = 'code_url_extractor'
    FIRECRAWL_ID = 'tool_firecrawl'
    LLM_ID = 'llm_core_generator'
    END_ID = 'end'

    nodes = [
        {
            "data": {
                "desc": "接收用户表单",
                "title": "开始",
                "type": "start",
                "variables": [
                    {"label": "职业", "max_length": 200, "required": True, "type": "text-input", "variable": "profession"},
                    {"label": "知识点", "max_length": 48000, "required": True, "type": "paragraph", "variable": "topic"},
                    {"label": "题型", "max_length": 200, "options": ["单选题", "多选题", "判断题", "简答题"], "required": True, "type": "select", "variable": "question_type"},
                    {"label": "难度", "max_length": 200, "options": ["简单", "中等", "困难", "专家级"], "required": True, "type": "select", "variable": "difficulty"},
                    {"label": "数量", "max_length": 10, "required": True, "type": "text-input", "variable": "question_count"}
                ]
            },
            "id": START_ID, "position": {"x": 50, "y": 300}, "type": "custom", "width": 244, "height": 312
        },
        {
            "data": {
                "code": "def main(qtype):\n    rules = \"【最高优先级安全锁】：请严格按照用户要求的题型出题，拒绝输出不相关的题型。\"\n    if \"单选题\" in qtype:\n        rules += \"\\n你必须且只能输出“单项选择题”。每道题必须包含 A、B、C、D 四个选项，且只有一个正确答案。绝对不允许输出判断题、简答题或填空题，违规将导致系统崩溃。\"\n    elif \"多选题\" in qtype:\n        rules += \"\\n你必须且只能输出“多项选择题”。每道题必须包含 A、B、C、D 等多个选项，且至少有两个或以上正确答案。\"\n    elif \"判断题\" in qtype:\n        rules += \"\\n你必须且只能输出“判断题”。只能对题干情境提供“正确”或“错误”的判断，严禁输出ABCD选项。\"\n    elif \"简答题\" in qtype:\n        rules += \"\\n你必须且只能输出“简答题”。要求提供问题描述，并直接给出论述型解答。\"\n    return {\"strict_rules\": rules}",
                "code_language": "python3",
                "desc": "左侧轨：即时阻断格式幻觉",
                "outputs": {"strict_rules": {"type": "string"}},
                "title": "代码约束锁 (Code)",
                "type": "code",
                "variables": [{"value_selector": [START_ID, "question_type"], "variable": "qtype"}]
            },
            "id": RULES_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 54
        },
        {
            "data": {
                "desc": "检索全网最新资料",
                "provider_id": "google",
                "provider_name": "google",
                "provider_type": "builtin",
                "tool_label": "GoogleSearch",
                "tool_name": "google_search",
                "tool_parameters": {
                    "query": "{{profession}} {{topic}} 最新 行业规范 白皮书 优质解析"
                },
                "title": "广度搜索 (Google)",
                "type": "tool",
                "variables": [
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"}
                ]
            },
            "id": SYS_SEARCH_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        {
            "data": {
                "code": "import json\ndef main(search_result):\n    try:\n        res = json.loads(search_result)\n        if res and isinstance(res, list) and len(res) > 0:\n            return {'url': res[0].get('link', '')}\n    except:\n        pass\n    return {'url': ''}",
                "code_language": "python3",
                "desc": "提取排行第一的权威链接",
                "outputs": {"url": {"type": "string"}},
                "title": "链接提取 (Code)",
                "type": "code",
                "variables": [{"value_selector": [SYS_SEARCH_ID, "text"], "variable": "search_result"}]
            },
            "id": EXTRACTOR_ID, "position": {"x": 650, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        {
            "data": {
                "desc": "无视护盾榨取全站文本",
                "provider_id": "firecrawl",
                "provider_name": "firecrawl",
                "provider_type": "builtin",
                "tool_label": "Firecrawl Scrape",
                "tool_name": "scrape",
                "tool_parameters": {
                    "url": "{{url}}",
                    "pageOptions": {"onlyMainContent": True}
                },
                "title": "深度扒取 (Firecrawl)",
                "type": "tool",
                "variables": [{"value_selector": [EXTRACTOR_ID, "url"], "variable": "url"}]
            },
            "id": FIRECRAWL_ID, "position": {"x": 950, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        {
            "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "吸收双轨数据出题",
                "model": {
                   "completion_params": {"temperature": 0.7, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "official-prompt",
                        "role": "system",
                        "text": "{{rules}}\n\n你是一位拥有20年实战经验的【{{profession}}】领域资深考官与终极培训专家。\n请结合以下通过强制反爬拿到的全网页硬核资料（如适用）进行出题：\n【深度原网页参考资料】：\n{{firecrawl_text}}\n\n你需要根据知识点：【{{topic}}】\n为考生生成【{{count}}】道难度为【{{diff}}】的题目。\n\n【绝对红线指标】：\n1. 必须提供真实的行业业务场景作为题干背景，拒绝干瘪的纯理论问答，要求高度贴合实际工作。\n2. 若为选择题，干扰选项必须具有极强的迷惑性（针对业内的真实常见坑点设计）。\n3. 所有题目必须同时输出“深度解析”，逐一剖析错误选项的槽点。\n4. 绝对禁止输出任何类似“好的”之类的客套废话，直接开始输出题目Markdown。"
                    }
                ],
                "title": "最终出题核心 (V3)",
                "type": "llm",
                "variables": [
                    {"value_selector": [RULES_ID, "strict_rules"], "variable": "rules"},
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"},
                    {"value_selector": [START_ID, "difficulty"], "variable": "diff"},
                    {"value_selector": [START_ID, "question_count"], "variable": "count"},
                    {"value_selector": [FIRECRAWL_ID, "text"], "variable": "firecrawl_text"}
                ]
            },
            "id": LLM_ID, "position": {"x": 1250, "y": 250}, "type": "custom", "width": 244, "height": 98
        },
        {
            "data": {
                "outputs": [{"value_selector": [LLM_ID, "text"], "variable": "final_output"}],
                "title": "结束",
                "type": "end"
            },
            "id": END_ID, "position": {"x": 1550, "y": 300}, "type": "custom", "width": 244, "height": 100
        }
    ]

    edges = [
        {"id": "e1", "source": START_ID, "target": RULES_ID, "type": "custom"},
        {"id": "e2", "source": START_ID, "target": SYS_SEARCH_ID, "type": "custom"},
        {"id": "e3", "source": SYS_SEARCH_ID, "target": EXTRACTOR_ID, "type": "custom"},
        {"id": "e4", "source": EXTRACTOR_ID, "target": FIRECRAWL_ID, "type": "custom"},
        {"id": "e5", "source": RULES_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e6", "source": FIRECRAWL_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e7", "source": START_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e8", "source": LLM_ID, "target": END_ID, "type": "custom"}
    ]

    for e in edges:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"
        
        # Derive sourceType and targetType from nodes
        source_type = next((n['data']['type'] for n in nodes if n['id'] == e['source']), 'custom')
        target_type = next((n['data']['type'] for n in nodes if n['id'] == e['target']), 'custom')
        
        e["data"] = {
            "isInIteration": False,
            "sourceType": source_type,
            "targetType": target_type
        }

    dsl["workflow"]["graph"]["nodes"] = nodes
    dsl["workflow"]["graph"]["edges"] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_official_v_final.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Generated question_factory_official_v_final.yml")

if __name__ == '__main__':
    generate_dsl()
