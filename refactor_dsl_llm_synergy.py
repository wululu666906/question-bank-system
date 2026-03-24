import yaml

def generate_dsl():
    dsl = {
      "app": {
        "description": "抛弃脆弱的外网连通依赖，采用顶尖的多智能体知识蒸馏架构。利用R1的极致深度思考能力作为虚拟知识库，再由V3实现定点剥洋葱式精编出题。",
        "icon": "💎",
        "icon_background": "#E8F4FD",
        "mode": "workflow",
        "name": "智能题库生成系统(内化知识提纯版)",
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
    R1_EXPANDER_ID = 'llm_r1_virtual_search'
    V3_DRAFTER_ID = 'llm_v3_master_drafter'
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
                "title": "1. 格式约束 (Code)",
                "type": "code",
                "variables": [{"value_selector": [START_ID, "question_type"], "variable": "qtype"}]
            },
            "id": RULES_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 54
        },
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "DeepSeek-R1 替代网络爬虫",
                "model": {
                   "completion_params": {"temperature": 0.6, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-R1", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "v16-r1-sys",
                        "role": "system",
                        "text": "你是一位拥有无穷知识的【{{profession}}】领域泰斗。你的任务是替代“外网搜索引擎”，从你的深度思维中直接调取、提纯出关于【{{topic}}】的最前沿、最硬核的行业白皮书级教案。\n\n请输出至少 3000 字的《实战命题母本参考资料》：\n1. 【业务痛点溯源】：该知识点在真实商业或技术环境中最容易诱发致命错误的操作场景（这是最好的题干来源）。\n2. 【认知盲区揭秘】：从业者极易混淆的“似是而非”的概念陷阱（这是最好的错误选项干扰来源）。\n3. 【第一性原理拆解】：该知识背后不可违背的根本逻辑（这是最终深度解析所需的核心论点）。\n\n注意：你不必出题，只需输出最具压迫感和专业密度的“知识结晶”，供后续命题官使用。"
                    },
                    {
                        "id": "v16-r1-usr",
                        "role": "user",
                        "text": "请直接开始撰写关于【{{topic}}】的《实战命题母本参考资料》，运用你最深度的思考："
                    }
                ],
                "title": "2. R1 虚拟知识库网(代替爬虫)",
                "type": "llm",
                "variables": [
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"}
                ]
            },
            "id": R1_EXPANDER_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 98
        },
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "V3 融合知识与约束进行高能出题",
                "model": {
                   "completion_params": {"temperature": 0.7, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "v16-v3-sys",
                        "role": "system",
                        "text": "{{rules}}\n\n你是一位冷酷且经验丰富的【{{profession}}】终极考官。\n请仔细研读由泰斗级专家编撰的《实战命题母本》：\n\n<权威内参档案>\n{{r1_whitepaper}}\n</权威内参档案>\n\n任务：利用内参档案提供的心智盲区和业务痛点，为【{{topic}}】生成【{{count}}】道难度为【{{diff}}】的压轴题。\n\n【高阶命题法则】：\n1. 【情境重构】：杜绝枯燥填空，直接把考生拖入《内参档案》提及的具体棘手业务场景。\n2. 【干扰项设计（Plausible Distractors）】：每个错误选项必须指向《内参》提及的认知盲区或流派争议，诱骗那些“只懂皮毛”的人。\n3. 【剥洋葱式深析】：解析必须分步撕开题目陷阱。说明为何正确，更要毒辣地指出错误选项错在何种实盘局限下。\n\n禁止说任何客套话，纯净输出 Markdown 试卷编排。"
                    },
                    {
                        "id": "v16-v3-usr",
                        "role": "user",
                        "text": "请完全遵守规则，直接开始输出最终的题库 Markdown："
                    }
                ],
                "title": "3. V3 终极命题官",
                "type": "llm",
                "variables": [
                    {"value_selector": [RULES_ID, "strict_rules"], "variable": "rules"},
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"},
                    {"value_selector": [START_ID, "difficulty"], "variable": "diff"},
                    {"value_selector": [START_ID, "question_count"], "variable": "count"},
                    {"value_selector": [R1_EXPANDER_ID, "text"], "variable": "r1_whitepaper"}
                ]
            },
            "id": V3_DRAFTER_ID, "position": {"x": 750, "y": 300}, "type": "custom", "width": 244, "height": 98
        },
        {
            "data": {
                "outputs": [{"value_selector": [V3_DRAFTER_ID, "text"], "variable": "final_output"}],
                "title": "结束",
                "type": "end"
            },
            "id": END_ID, "position": {"x": 1050, "y": 300}, "type": "custom", "width": 244, "height": 100
        }
    ]

    edges = [
        {"id": "e1", "source": START_ID, "target": RULES_ID, "type": "custom"},
        {"id": "e2", "source": START_ID, "target": R1_EXPANDER_ID, "type": "custom"},
        {"id": "e3", "source": RULES_ID, "target": V3_DRAFTER_ID, "type": "custom"},
        {"id": "e4", "source": R1_EXPANDER_ID, "target": V3_DRAFTER_ID, "type": "custom"},
        {"id": "e5", "source": START_ID, "target": V3_DRAFTER_ID, "type": "custom"},
        {"id": "e6", "source": V3_DRAFTER_ID, "target": END_ID, "type": "custom"}
    ]

    for e in edges:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"
        source_type = next((n['data']['type'] for n in nodes if n['id'] == e['source']), 'custom')
        target_type = next((n['data']['type'] for n in nodes if n['id'] == e['target']), 'custom')
        e["data"] = {
            "isInIteration": False,
            "sourceType": source_type,
            "targetType": target_type
        }

    dsl["workflow"]["graph"]["nodes"] = nodes
    dsl["workflow"]["graph"]["edges"] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_llm_synergy.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Generated question_factory_llm_synergy.yml with user prompts.")

if __name__ == '__main__':
    generate_dsl()
