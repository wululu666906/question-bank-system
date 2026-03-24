import yaml
import json

def generate_dsl():
    dsl = {
      "app": {
        "description": "极速流式打字机版。剔除了会卡顿缓冲的迭代与代码质检节点，大模型直奔主题，支持数学公式自修正排版，纵享丝滑的超长文本流式输出体验。",
        "icon": "⚡",
        "icon_background": "#E8F4FD",
        "mode": "workflow",
        "name": "智能题库生成系统(极速流式版)",
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
    INTENT_LLM_ID = 'llm_intent_recognizer'
    CRAWLER_ID = 'code_python_ddg_crawler'
    LOCK_ID = 'code_format_lock'
    MASTER_LLM_ID = 'llm_master_drafter_streaming'
    END_ID = 'end'

    nodes = [
        # 1. START
        {
            "data": {
                "desc": "接收用户表单",
                "title": "开始",
                "type": "start",
                "variables": [
                    {"label": "知识点/题目主体", "max_length": 48000, "required": True, "type": "paragraph", "variable": "topic"},
                    {"label": "难度", "max_length": 200, "options": ["简单", "中等", "困难", "专家级"], "required": True, "type": "select", "variable": "difficulty"},
                    {"label": "数量", "max_length": 10, "required": True, "type": "text-input", "variable": "question_count"},
                    {"label": "岗位/职业", "max_length": 200, "required": True, "type": "text-input", "variable": "profession"},
                    {"label": "题型", "max_length": 200, "options": ["单选题", "多选题", "判断题", "主观题", "材料题", "作文"], "required": True, "type": "select", "variable": "question_type"}
                ]
            },
            "id": START_ID, "position": {"x": 50, "y": 300}, "type": "custom", "width": 244, "height": 312
        },
        # 2. INTENT LLM (DeepSeek)
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "专门理解出题需求并拓展精准搜索指令",
                "model": {
                   "completion_params": {"temperature": 0.5, "max_tokens": 1000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "intent-sys",
                        "role": "system",
                        "text": "你是一个“搜商极高”的出题架构师。你需要理解用户当前正在进行【智能卷库出题】环节，其发起的挑战是：面向【{{#start.profession#}}】岗位的【{{#start.topic#}}】。\n请据此拓展出最能搜到高质量真实案例与硬核解析的“原生搜索引擎查询指令”（不超过20字，用空格分隔关键字）。\n\n除了这个单行指令外，绝对不要输出任何标点、解释或客套话。"
                    },
                    {
                        "id": "intent-usr",
                        "role": "user",
                        "text": "请直接输出您的检索指令字符串："
                    }
                ],
                "title": "1. 意图拓展大脑 (V3)",
                "type": "llm",
                "variables": [
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"}
                ]
            },
            "id": INTENT_LLM_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 98
        },
        # 3. PYTHON CRAWLER (DDG)
        {
            "data": {
                "code": "import requests\nimport re\nimport urllib.parse\n\ndef main(search_query):\n    headers = {\n        \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36\",\n        \"Accept-Language\": \"zh-CN,zh;q=0.9,en;q=0.8\"\n    }\n    url = f\"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}\"\n    \n    try:\n        req = requests.get(url, headers=headers, timeout=15)\n        if req.status_code != 200:\n            return {\"scraped_data\": \"外网搜索引擎拦截，请立即启动您的内置专家知识库来满足用户的出题指令。\"}\n            \n        html = req.text\n        snippets = re.findall(r'<a class=\"result__snippet[^>]+>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)\n        \n        if not snippets:\n            return {\"scraped_data\": \"未能从外网提取到有效切片，请启动内置高级知识库。\"}\n            \n        cleaned_snippets = []\n        for s in snippets[:8]:\n            clean_s = re.sub(r'<[^>]+>', '', s)\n            cleaned_snippets.append(clean_s.strip())\n            \n        final_text = \"\\n\\n\".join([f\"【外网顶级参考案例 {i+1}】: {text}\" for i, text in enumerate(cleaned_snippets)])\n        return {\"scraped_data\": final_text}\n    except Exception as e:\n        return {\"scraped_data\": f\"爬虫网络穿透异常：{str(e)}。\"}",
                "code_language": "python3",
                "desc": "无API-Key限制的自建 DDG 脱壳爬虫",
                "outputs": {"scraped_data": {"type": "string"}},
                "title": "2. 自建网络爬虫探针 (Code)",
                "type": "code",
                "variables": [{"value_selector": [INTENT_LLM_ID, "text"], "variable": "search_query"}]
            },
            "id": CRAWLER_ID, "position": {"x": 650, "y": 150}, "type": "custom", "width": 244, "height": 54
        },
        # 4. FORMAT LOCK
        {
            "data": {
                "code": "def main(qtype):\n    rules = \"【核心安全锁】：严格遵循用户题型。拒绝任何跑题发散。\\n\"\n    if \"单选\" in qtype:\n        rules += \"必须出单项选择题，四选一。\"\n    elif \"多选\" in qtype:\n        rules += \"必须出多项选择题，多个正确答案。\"\n    elif \"判断\" in qtype:\n        rules += \"必须出判断题（正确/错误）。\"\n    elif \"主观\" in qtype or \"简答\" in qtype:\n        rules += \"必须出主观简答题，要求提供评卷标准。\"\n    elif \"材料\" in qtype:\n        rules += \"必须出材料分析题，必须提供长篇研判材料及提问。\"\n    elif \"作文\" in qtype:\n        rules += \"必须出命题/半命题作文，要求列出写作立意与评分维度。\"\n    return {\"strict_rules\": rules}",
                "code_language": "python3",
                "desc": "锁定出题题型底层约束锁",
                "outputs": {"strict_rules": {"type": "string"}},
                "title": "3. 题型约束锁 (Code)",
                "type": "code",
                "variables": [
                    {"value_selector": [START_ID, "question_type"], "variable": "qtype"}
                ]
            },
            "id": LOCK_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        # 5. STREAMING MASTER DRAFTER
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "desc": "直连End节点实现极速流式打字机输出",
                "model": {
                   "completion_params": {"temperature": 0.6, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "stream-llm-sys",
                        "role": "system",
                        "text": "{{#code_format_lock.strict_rules#}}\n\n你是一位冷酷且要求极高的【{{#start.profession#}}】终极考官。\n请基于以下通过Python外网探针强制抓取到的【首发最新资料】：\n\n<原网绝密资料>\n{{#code_python_ddg_crawler.scraped_data#}}\n</原网绝密资料>\n\n任务：利用上述素材，为【{{#start.topic#}}】生成 【一共 {{#start.question_count#}} 道】 难度为【{{#start.difficulty#}}】的压轴题。\n\n【单题暴击法则】（基于原本指令）：\n1. 【篇幅与压迫感】：因为你需要把每道题当做终极决战去出，请将题干背景写的极具长篇细节，用最真实的业务场景折磨考生。\n2. 【选项与陷阱】：选项要有迷惑性。错误选项必须是非常容易踩坑的常见盲点。(非选择题忽略)\n3. 【降维解析】：解析必须剥洋葱式剖析逻辑，不仅公布正解，更要指出错误选项荒唐在何处。\n4. 严格输出全场纯净中文，并保持专业的 Markdown 排版。\n5. 【强制输出结构】：对于每一道题，都必须且只能严格按顺序依次输出三大模块：「一、题目（必须包含背景材料）」 -> 「二、答案（明确给出正解）」 -> 「三、深度解析」。每生成完一道题，请用 `---` 划线隔开。\n\n【全局流式输出增补保护协议】（替代原质检节点）：\n- 【格式字体要求】：请使用 Markdown 标准标题（如 `### 第N题`）。所有【答案】和【解析】字段必须采用加粗换行的形式规范排版，例如 `**答案**：\\n`。\n- 【极危警告 - 数学渲染转义】：请极其警惕公式兼容问题！**绝对禁止**使用 `\\[` 和 `\\]` 来渲染任何独立区块公式。所有独立公式必须用 `$$` 完全包裹（如 `$$ y=x^2 $$`）；所有内联文本公式必须用 `$` 包裹，禁止使用 `\\(` 和 `\\)`。\n- 【质量极其优先】：你不受生成的 Token 烦恼，系统会打通极长并发链路。你需要向这 【{{#start.question_count#}}】道题倾注不可思议的解析深度。因此，就算遇到极长截断的可能，也请不要随意总结结尾！后续框架自带上下文迭代机制来弥补未尽之言。"
                    },
                    {
                        "id": "stream-llm-usr",
                        "role": "user",
                        "text": "请直接开始输出这【{{#start.question_count#}}】道压轴题的连贯内容库，拒绝一切废话："
                    }
                ],
                "title": "4. 流式题库直写炉 (V3 流式)",
                "type": "llm",
                "variables": [
                    {"value_selector": [LOCK_ID, "strict_rules"], "variable": "rules"},
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"},
                    {"value_selector": [START_ID, "difficulty"], "variable": "diff"},
                    {"value_selector": [START_ID, "question_count"], "variable": "count"},
                    {"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"}
                ]
            },
            "id": MASTER_LLM_ID, "position": {"x": 1050, "y": 300}, "type": "custom", "width": 244, "height": 98
        },
        # 6. END NODE
        {
            "data": {
                "outputs": [{"value_selector": [MASTER_LLM_ID, "text"], "variable": "final_output"}],
                "title": "结束",
                "type": "end"
            },
            "id": END_ID, "position": {"x": 1400, "y": 300}, "type": "custom", "width": 244, "height": 100
        }
    ]

    edges = [
        {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "llm"}},
        {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "llm", "targetType": "code"}},
        {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "code"}},
        # Crawler -> V3
        {"id": "e4", "source": CRAWLER_ID, "target": MASTER_LLM_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "code", "targetType": "llm"}},
        # Lock -> V3
        {"id": "e5", "source": LOCK_ID, "target": MASTER_LLM_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "code", "targetType": "llm"}},
        # Start -> V3
        {"id": "e6", "source": START_ID, "target": MASTER_LLM_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "llm"}},
        # V3 -> End
        {"id": "e7", "source": MASTER_LLM_ID, "target": END_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "llm", "targetType": "end"}}
    ]

    for e in edges:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"

    dsl["workflow"]["graph"]["nodes"] = nodes
    dsl["workflow"]["graph"]["edges"] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_streaming_v19.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Generated question_factory_streaming_v19.yml.")

if __name__ == '__main__':
    generate_dsl()
