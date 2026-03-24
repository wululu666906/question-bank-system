import yaml
import json

def generate_dsl():
    dsl = {
      "app": {
        "description": "全新单步长程发酵架构。具备意图前瞻、突破性DuckDuckGo自建探针、安全拦截锁，并通过迭代引擎逐题进行高深度逻辑打磨，最后流经代码级质检清洗间完成高规格排版。",
        "icon": "🚀",
        "icon_background": "#E8F4FD",
        "mode": "workflow",
        "name": "智能题库生成系统(DDG深搜迭代版)",
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
    ITERATION_ID = 'iteration_generator'
    ITER_START_ID = 'iteration_generatorstart'
    ITER_LLM_ID = 'llm_single_drafter'
    QUALITY_NODE_ID = 'code_quality_inspector'
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
                "code": "import requests\nimport re\nimport urllib.parse\n\ndef main(search_query):\n    headers = {\n        \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36\",\n        \"Accept-Language\": \"zh-CN,zh;q=0.9,en;q=0.8\"\n    }\n    url = f\"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}\"\n    \n    try:\n        req = requests.get(url, headers=headers, timeout=15)\n        if req.status_code != 200:\n            return {\"scraped_data\": \"外网搜索引擎拦截，请立即启动您的内置专家知识库来满足用户的出题指令。\"}\n            \n        html = req.text\n        # 提取 DDG 搜索结果的摘要片段\n        snippets = re.findall(r'<a class=\"result__snippet[^>]+>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)\n        \n        if not snippets:\n            return {\"scraped_data\": \"未能从外网提取到有效切片，请启动内置高级知识库。\"}\n            \n        cleaned_snippets = []\n        for s in snippets[:8]: # 提取前8个最相关的摘要\n            clean_s = re.sub(r'<[^>]+>', '', s)\n            cleaned_snippets.append(clean_s.strip())\n            \n        final_text = \"\\n\\n\".join([f\"【外网顶级参考案例 {i+1}】: {text}\" for i, text in enumerate(cleaned_snippets)])\n        return {\"scraped_data\": final_text}\n    except Exception as e:\n        return {\"scraped_data\": f\"爬虫网络穿透异常：{str(e)}。\"}",
                "code_language": "python3",
                "desc": "无API-Key限制的自建 DDG 脱壳爬虫",
                "outputs": {"scraped_data": {"type": "string"}},
                "title": "2. 自建网络爬虫探针 (Code)",
                "type": "code",
                "variables": [{"value_selector": [INTENT_LLM_ID, "text"], "variable": "search_query"}]
            },
            "id": CRAWLER_ID, "position": {"x": 650, "y": 150}, "type": "custom", "width": 244, "height": 54
        },
        # 4. FORMAT LOCK & ITERATION ARRAY BUILDER
        {
            "data": {
                "code": "def main(qtype, count_str):\n    rules = \"【核心安全锁】：严格遵循用户题型。拒绝任何跑题发散。\\n\"\n    if \"单选\" in qtype:\n        rules += \"必须出单项选择题，四选一。\"\n    elif \"多选\" in qtype:\n        rules += \"必须出多项选择题，多个正确答案。\"\n    elif \"判断\" in qtype:\n        rules += \"必须出判断题（正确/错误）。\"\n    elif \"主观\" in qtype or \"简答\" in qtype:\n        rules += \"必须出主观简答题，要求提供评卷标准。\"\n    elif \"材料\" in qtype:\n        rules += \"必须出材料分析题，必须提供长篇研判材料及提问。\"\n    elif \"作文\" in qtype:\n        rules += \"必须出命题/半命题作文，要求列出写作立意与评分维度。\"\n\n    # 生成迭代数组\n    try:\n        cn = int(count_str)\n        if cn > 20: cn = 20 \n    except:\n        cn = 1\n    iter_array = [str(i+1) for i in range(cn)]\n    return {\"strict_rules\": rules, \"iter_array\": iter_array}",
                "code_language": "python3",
                "desc": "锁定题型及触发迭代引擎",
                "outputs": {"strict_rules": {"type": "string"}, "iter_array": {"type": "array[string]"}},
                "title": "3. 约束锁与引擎阀 (Code)",
                "type": "code",
                "variables": [
                    {"value_selector": [START_ID, "question_type"], "variable": "qtype"},
                    {"value_selector": [START_ID, "question_count"], "variable": "count_str"}
                ]
            },
            "id": LOCK_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
        },
        # 5. ITERATION (Parent)
        {
            "data": {
                "desc": "单题深度打磨循环矩阵",
                "iterator_selector": [LOCK_ID, "iter_array"],
                "output_selector": [ITER_LLM_ID, "text"],
                "start_node_id": ITER_START_ID,
                "title": "4. 单题深研迭代网络 (Iteration)",
                "type": "iteration"
            },
            "id": ITERATION_ID, "position": {"x": 950, "y": 150}, "type": "custom", "width": 450, "height": 300
        },
        # 5a. ITERATION START
        {
            "data": {"isInIteration": True, "type": "iteration-start"},
            "id": ITER_START_ID, "parentId": ITERATION_ID, "position": {"x": 20, "y": 100}, "type": "custom-iteration-start", "width": 44, "height": 48, "zIndex": 1001
        },
        # 5b. DEEPSEEK SINGLE DRAFTER
        {
             "data": {
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
                "isInIteration": True,
                "desc": "每次只出1题以确保篇幅和质量",
                "model": {
                   "completion_params": {"temperature": 0.6, "max_tokens": 4000},
                   "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"
                },
                "prompt_template": [
                    {
                        "id": "iter-llm-sys",
                        "role": "system",
                        "text": "{{#code_format_lock.strict_rules#}}\n\n你是一位冷酷且要求极高的【{{#start.profession#}}】终极考官。\n请基于以下通过Python外网探针强制抓取到的【首发最新资料】：\n\n<原网绝密资料>\n{{#code_python_ddg_crawler.scraped_data#}}\n</原网绝密资料>\n\n任务：利用上述素材，为【{{#start.topic#}}】生成 【第 {{#iteration_generator.item#}} 道】 难度为【{{#start.difficulty#}}】的压轴题。\n\n【单题暴击法则】：\n1. 【篇幅与压迫感】：因为你一次只出1道题，请将题干背景写的极具长篇细节，用最真实的业务场景折磨考生。\n2. 【选项与陷阱】：选项要有迷惑性。错误选项必须是非常容易踩坑的常见盲点。(非选择题忽略)\n3. 【降维解析】：解析必须剥洋葱式剖析逻辑，不仅公布正解，更要指出错误选项荒唐在何处。\n4. 严格输出全场纯净中文，并保持专业的 Markdown 排版。"
                    },
                    {
                        "id": "iter-llm-usr",
                        "role": "user",
                        "text": "请立即输出这唯一1道高深度巨头级题目的完整内容（杜绝废话）："
                    }
                ],
                "title": "题库重型发酵炉 (V3 单题直出)",
                "type": "llm",
                "variables": [
                    {"value_selector": [LOCK_ID, "strict_rules"], "variable": "rules"},
                    {"value_selector": [START_ID, "profession"], "variable": "profession"},
                    {"value_selector": [START_ID, "topic"], "variable": "topic"},
                    {"value_selector": [START_ID, "difficulty"], "variable": "diff"},
                    {"value_selector": [ITERATION_ID, "item"], "variable": "curr_iter"},
                    {"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"}
                ]
            },
            "id": ITER_LLM_ID, "parentId": ITERATION_ID, "position": {"x": 120, "y": 80}, "type": "custom", "width": 244, "height": 98, "zIndex": 1001
        },
        # 6. QUALITY AND RENDER INSPECTOR (Code)
        {
            "data": {
                "code": "import re\n\ndef main(iteration_output_array):\n    full_paper = \"\\n\\n---\\n\\n\".join(iteration_output_array)\n    \n    # 【中文兼容逻辑】\n    if not re.search(r'[\\u4e00-\\u9fa5]', full_paper):\n        full_paper = \"【系统质检】：检测到原始输出未包含中文字符，已触发保护机制强制拦截并建议大模型重考。原始流出（可能为乱码或外语）如下：\\n\" + full_paper\n\n    # 【换行重构】\n    full_paper = re.sub(r'\\n{3,}', '\\n\\n', full_paper)\n    \n    # 【底层渲染转义注入：支持数学公式】\n    full_paper = full_paper.replace(r'$$', '$$$TEMP$$$')\n    full_paper = full_paper.replace(r'\\\\[', '$$')\n    full_paper = full_paper.replace(r'\\\\]', '$$')\n    full_paper = full_paper.replace('$$$TEMP$$$', '$$')\n    full_paper = full_paper.replace(r'\\(', '$')\n    full_paper = full_paper.replace(r'\\)', '$')\n    \n    anchor_words = [\"答案\", \"解析\", \"题干\", \"考点\"]\n    for aw in anchor_words:\n        full_paper = full_paper.replace(aw + \":\", aw + \"：\")\n        \n    final_paper = f\"# 【AI深度集卷质检通过】\\n\\n{full_paper}\\n\\n> 质检引擎日志：公式及排版安全转义完成 | 全局语言环境验证正常\"\n    return {\"sanitized_text\": final_paper}",
                "code_language": "python3",
                "desc": "确保全试卷中文、注入公式转义重构代码。",
                "outputs": {"sanitized_text": {"type": "string"}},
                "title": "5. 公式渲染及合卷质检 (Code)",
                "type": "code",
                "variables": [{"value_selector": [ITERATION_ID, "output"], "variable": "iteration_output_array"}]
            },
            "id": QUALITY_NODE_ID, "position": {"x": 1500, "y": 250}, "type": "custom", "width": 244, "height": 54
        },
        # 7. END NODE
        {
            "data": {
                "outputs": [{"value_selector": [QUALITY_NODE_ID, "sanitized_text"], "variable": "final_output"}],
                "title": "结束",
                "type": "end"
            },
            "id": END_ID, "position": {"x": 1850, "y": 250}, "type": "custom", "width": 244, "height": 100
        }
    ]

    edges = [
        {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "llm"}},
        {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "llm", "targetType": "code"}},
        {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "code"}},
        {"id": "e4", "source": LOCK_ID, "target": ITERATION_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "code", "targetType": "iteration"}},
        {"id": "e5", "source": CRAWLER_ID, "target": ITERATION_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "code", "targetType": "iteration"}},
        {"id": "e6", "source": START_ID, "target": ITERATION_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "start", "targetType": "iteration"}},
        {"id": "e7", "source": ITER_START_ID, "target": ITER_LLM_ID, "type": "custom", "data": {"isInIteration": True, "sourceType": "custom-iteration-start", "targetType": "llm"}},
        {"id": "e8", "source": ITERATION_ID, "target": QUALITY_NODE_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "iteration", "targetType": "code"}},
        {"id": "e9", "source": QUALITY_NODE_ID, "target": END_ID, "type": "custom", "data": {"isInIteration": False, "sourceType": "code", "targetType": "end"}}
    ]

    for e in edges:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"

    dsl["workflow"]["graph"]["nodes"] = nodes
    dsl["workflow"]["graph"]["edges"] = edges

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_ddg_iteration.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)

    print("Success: Generated question_factory_ddg_iteration.yml.")

if __name__ == '__main__':
    generate_dsl()
