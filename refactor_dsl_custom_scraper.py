import yaml

def generate_dsl():
    dsl = {
      "app": {
        "description": "集成了全功能内置Jina爬虫脚本的专业级智能题库系统，直接突破网络屏障聚合业务素材出题。",
        "icon": "🕷️",
        "icon_background": "#E8F4FD",
        "mode": "workflow",
        "name": "智能题库生成系统(自建外网智囊版)",
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
    SCRAPER_ID = 'code_jina_scraper'
    LLM_ID = 'llm_master_generator'
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
                "desc": "即时阻断格式幻觉",
                "outputs": {"strict_rules": {"type": "string"}},
                "title": "1. 格式约束锁 (Code)",
                "type": "code",
                "variables": [{"value_selector": [START_ID, "question_type"], "variable": "qtype"}]
            },
            "id": RULES_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 54
        },
        {
            "data": {
                "code": "import requests\nimport re\n\ndef main(profession, topic):\n    query = f\"{profession} {topic} 最新实战案例 核心要点解析 业务场景\"\n    url = f\"https://s.jina.ai/{query}\"\n    \n    headers = {\n        \"Accept\": \"text/plain\",\n        \"X-Return-Format\": \"markdown\",\n        \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Dify-Agent Custom\"\n    }\n    \n    try:\n        req = requests.get(url, headers=headers, timeout=12)\n        text = req.text\n        \n        if req.status_code != 200:\n            return {\"scraped_data\": \"网络接口受限，无法直接获取外网资料。请启动LLM内置知识补充生成。\"}\n            \n        # 数据清洗过滤冗余换行，提纯前8000个字符\n        clean_text = re.sub(r'\\n{3,}', '\\n\\n', text).strip()\n        final_text = clean_text[:8000]\n        \n        if len(final_text) < 50:\n            final_text = \"未搜索到有效参考资料，请启用内置世界知识库。\"\n            \n        return {\"scraped_data\": final_text}\n    except Exception as e:\n        return {\"scraped_data\": f\"网络穿透异常：{str(e)}。请强行发挥内置专家能力出题。\"}",
                "code_language": "python3",
                "desc": "自建外部代码实现联网搜索与反爬提纯",
                "outputs": {"scraped_data": {"type": "string"}},
                "title": "2. 全网智囊爬虫 (Code)",
                "type": "code",
                "variables": [
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"}
                ]
            },
            "id": SCRAPER_ID, "position": {"x": 450, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "吸收全网实时资料重构题库",
                "model": {
                   "completion_params": {"temperature": 0.7, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "v15-master-prompt",
                        "role": "system",
                        "text": "{{rules}}\n\n你是一位拥有20年实战经验的【{{profession}}】领域资深考官与终极培训专家。\n请结合以下通过智能网络探针聚合提纯的【最新外网真实资料】进行高水准的命题创作：\n\n<全网深度快照素材>\n{{scraped_data}}\n</全网深度快照素材>\n\n任务核心：针对用户输入的考点【{{topic}}】，生成【{{count}}】道难度标定为【{{diff}}】的压轴级测试题。\n\n【高阶质量红线】：\n1. 场景化沉浸设计（Contextual Depth）：绝不直接问干瘪的理论概念。题干必须是一个真实的、棘手的业务场景或实操流程（强烈建议直接从上方 <快照素材> 中提取真实业务案例进行二次改编）。\n2. 高水平的干扰设计（Distractor Quality）：如果是选择题，选项 A、B、C、D 必须极具迷惑性（Plausible Distractors）。错误选项绝对不能是“一目了然的低级错误”，必须是“从业新手最容易踩坑的常见误区”或“条件不足时的妥协解”。\n3. 剥洋葱式拆解法（Deep Analysis）：每道题必须附带极具深度的底层逻辑解析。不仅要解释正确选项“为什么是对的”，更要深挖每个错误选项的逻辑漏洞“为什么错、错在实战的哪个环节”。\n4. 绝对无废话：你不能输出任何问候语（如“好的”、“立刻给您生成”等客套话），必须使用纯净、整洁的 Markdown 格式立即开始生成试卷。"
                    }
                ],
                "title": "3. 顶级命题大师 (V3)",
                "type": "llm",
                "variables": [
                    {"value_selector": [RULES_ID, "strict_rules"], "variable": "rules"},
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"},
                    {"value_selector": [START_ID, "difficulty"], "variable": "diff"},
                    {"value_selector": [START_ID, "question_count"], "variable": "count"},
                    {"value_selector": [SCRAPER_ID, "scraped_data"], "variable": "scraped_data"}
                ]
            },
            "id": LLM_ID, "position": {"x": 800, "y": 300}, "type": "custom", "width": 244, "height": 98
        },
        {
            "data": {
                "outputs": [{"value_selector": [LLM_ID, "text"], "variable": "final_output"}],
                "title": "结束",
                "type": "end"
            },
            "id": END_ID, "position": {"x": 1100, "y": 300}, "type": "custom", "width": 244, "height": 100
        }
    ]

    edges = [
        {"id": "e1", "source": START_ID, "target": RULES_ID, "type": "custom"},
        {"id": "e2", "source": START_ID, "target": SCRAPER_ID, "type": "custom"},
        {"id": "e3", "source": RULES_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e4", "source": SCRAPER_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e5", "source": START_ID, "target": LLM_ID, "type": "custom"},
        {"id": "e6", "source": LLM_ID, "target": END_ID, "type": "custom"}
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

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_custom_scraper.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Generated question_factory_custom_scraper.yml")

if __name__ == '__main__':
    generate_dsl()
