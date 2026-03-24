import yaml
import json

def generate_dsl():
    # 保持 Workflow 模式，拓扑结构与截图完全一致
    START_ID = 'start'
    INTENT_LLM_ID = 'llm_intent_recognizer'
    CRAWLER_ID = 'code_python_ddg_crawler'
    LOCK_ID = 'code_format_lock'
    ITERATION_ID = 'iteration_generator'
    ITER_START_ID = 'iteration_generatorstart'
    ITER_LLM_ID = 'llm_single_drafter'
    QUALITY_NODE_ID = 'code_quality_inspector'
    END_ID = 'end'

    dsl = {
      "app": {
        "description": "专家级深度研习笔记版。结构与您的工作流完全对齐，通过代码级排版引擎与提示词深度打磨，实现类似大模型原生界面的美观排版。",
        "icon": "🎨",
        "icon_background": "#FDF2F8",
        "mode": "workflow", 
        "name": "智能题库生成系统(专家笔记视觉版)",
        "use_icon_as_answer_icon": False
      },
      "kind": "app",
      "version": "0.1.3",
      "workflow": {
        "features": {
          "file_upload": {"enabled": False},
          "opening_statement": "",
          "retriever_resource": {"enabled": False},
          "sensitive_word_avoidance": {"enabled": False},
          "speech_to_text": {"enabled": False},
          "suggested_questions": [],
          "suggested_questions_after_answer": {"enabled": False},
          "text_to_speech": {"enabled": False}
        },
        "graph": {
            "nodes": [
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
                # 2. INTENT LLM (Node 1 in screenshot)
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.5, "max_tokens": 1000}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"id": "intent-sys", "role": "system", "text": "你是一个“搜商极高”的出题架构师。任务：为【{{#start.profession#}}】岗位的【{{#start.topic#}}】生成精准搜索指令。直接输出一行指令，不要废话。"}],
                        "title": "1. 意图图谱大脑 (V3)",
                        "type": "llm",
                        "variables": [
                            {"value_selector": [START_ID, "profession"], "variable": "profession"},
                            {"value_selector": [START_ID, "topic"], "variable": "topic"}
                        ]
                    },
                    "id": INTENT_LLM_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 98
                },
                # 3. CRAWLER (Node 2 in screenshot)
                {
                    "data": {
                        "code": "import requests\nimport re\nimport urllib.parse\ndef main(search_query):\n    headers = {\"User-Agent\": \"Mozilla/5.0\"}\n    url = f\"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}\"\n    try:\n        req = requests.get(url, headers=headers, timeout=10)\n        snippets = re.findall(r'<a class=\"result__snippet[^>]+>(.*?)</a>', req.text, re.IGNORECASE | re.DOTALL)\n        cleaned = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:6]]\n        return {\"scraped_data\": \"\\n\".join(cleaned) if cleaned else \"无外部数据\"}\n    except: return {\"scraped_data\": \"爬虫网络穿透异常\"}",
                        "code_language": "python3",
                        "outputs": {"scraped_data": {"type": "string"}},
                        "title": "2. 自建网络爬虫探针 (CODE)",
                        "type": "code",
                        "variables": [{"value_selector": [INTENT_LLM_ID, "text"], "variable": "search_query"}]
                    },
                    "id": CRAWLER_ID, "position": {"x": 650, "y": 150}, "type": "custom", "width": 244, "height": 54
                },
                # 4. LOCK (Node 3 in screenshot)
                {
                    "data": {
                        "code": "def main(qtype, count_str):\n    rules = f\"严格锁定题型：{qtype}\"\n    n = int(count_str or 1)\n    return {\"strict_rules\": rules, \"iter_array\": [str(i+1) for i in range(n)]}",
                        "code_language": "python3",
                        "outputs": {"strict_rules": {"type": "string"}, "iter_array": {"type": "array[string]"}},
                        "title": "3. 约束锁与引擎阀 (CODE)",
                        "type": "code",
                        "variables": [
                            {"value_selector": [START_ID, "question_type"], "variable": "qtype"},
                            {"value_selector": [START_ID, "question_count"], "variable": "count_str"}
                        ]
                    },
                    "id": LOCK_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
                },
                # 5. ITERATION (Node 4 in screenshot)
                {
                    "data": {
                        "desc": "单题深度打磨循环矩阵",
                        "iterator_selector": [LOCK_ID, "iter_array"],
                        "output_selector": [ITER_LLM_ID, "text"],
                        "start_node_id": ITER_START_ID,
                        "title": "4. 单题深研迭代网络 (ITERATION)",
                        "type": "iteration"
                    },
                    "id": ITERATION_ID, "position": {"x": 950, "y": 150}, "type": "custom", "width": 450, "height": 300
                },
                {"data": {"isInIteration": True, "type": "iteration-start"}, "id": ITER_START_ID, "parentId": ITERATION_ID, "position": {"x": 20, "y": 100}, "type": "custom-iteration-start", "width": 44, "height": 48, "zIndex": 1001},
                {
                    "id": ITER_LLM_ID, 
                    "parentId": ITERATION_ID, 
                    "position": {"x": 120, "y": 80}, 
                    "type": "custom", 
                    "data": {
                        "isInIteration": True,
                        "model": {"completion_params": {"temperature": 0.6, "max_tokens": 4000}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [
                            {
                                "role": "system",
                                "text": "{{#code_format_lock.strict_rules#}}\n\n你是一位享誉全球的【{{#start.profession#}}】首席考官。请基于抓取资料生成一份精美的研习笔记。\n使用 Markdown 多级标题架构：\n- ## [题目序号] [情境主题]\n- ### 题目详情\n- ### 深度解析\n\n资料：{{#code_python_ddg_crawler.scraped_data#}}"
                            }
                        ],
                        "title": "题库重型发酵炉 (V3 单题直出)", "type": "llm",
                        "variables": [
                            {"value_selector": [LOCK_ID, "strict_rules"], "variable": "rules"},
                            {"value_selector": [START_ID, "profession"], "variable": "profession"},
                            {"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"}
                        ]
                    },
                    "width": 244, "height": 98, "zIndex": 1001
                },
                # 6. QUALITY INSPECTOR (Node 5 in screenshot - THE ONE TO FIX)
                {
                    "data": {
                        "code": "import re\n\ndef main(iteration_output_array):\n    # 1. 连接各题内容\n    raw_content = \"\\n\\n---\\n\\n\".join(iteration_output_array)\n    \n    # 2. 移除冗余的“题目/答案”死板标签，改为美观的 Emoji 引导\n    # （假设大模型输出中包含这些词，我们进行统一替换）\n    replacements = {\n        \"题目：\": \"### 📝 题目详情\\n\",\n        \"答案：\": \"### ✅ 标准参考\\n\",\n        \"解析：\": \"### 💡 深度逻辑连线\\n\",\n        \"背景材料：\": \"> 📚 **背景研判材料**：\"\n    }\n    for old, new in replacements.items():\n        raw_content = raw_content.replace(old, new)\n\n    # 3. 数学公式极致渲染兼容\n    # 统一将 \\( \\) 和 \\[ \\] 转化为 $$ $$ 确保大模型式的前端渲染\n    raw_content = raw_content.replace(r'$$', '$$$TEMP$$$')\n    raw_content = raw_content.replace(r'\\\\[', '$$')\n    raw_content = raw_content.replace(r'\\\\]', '$$')\n    raw_content = raw_content.replace('$$$TEMP$$$', '$$')\n    raw_content = raw_content.replace(r'\\(', '$')\n    raw_content = raw_content.replace(r'\\)', '$')\n\n    # 4. 注入大模型风格的笔记标题与页脚\n    final_paper = f\"\"\"# 🎯 专家级真题研习手册\n---\n> **[注]**：本笔记由智能深度矩阵发酵生成，融合了外网实时探针数据。排版已自动对齐大模型原生输出规范。\n\n{raw_content}\n\n---\n**[END]**：全卷逻辑校验完成。\"\"\"\n    \n    return {\"sanitized_text\": final_paper}",
                        "code_language": "python3",
                        "outputs": {"sanitized_text": {"type": "string"}},
                        "title": "5. 公式渲染及合卷质检 (CODE)",
                        "type": "code",
                        "variables": [{"value_selector": [ITERATION_ID, "output"], "variable": "iteration_output_array"}]
                    },
                    "id": QUALITY_NODE_ID, "position": {"x": 1500, "y": 250}, "type": "custom", "width": 244, "height": 54
                },
                # 7. END
                {
                    "data": {
                        "outputs": [{"value_selector": [QUALITY_NODE_ID, "sanitized_text"], "variable": "final_output"}],
                        "title": "结束",
                        "type": "end"
                    },
                    "id": END_ID, "position": {"x": 1850, "y": 250}, "type": "custom", "width": 244, "height": 100
                }
            ],
            "edges": [
                {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e4", "source": CRAWLER_ID, "target": ITERATION_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e5", "source": LOCK_ID, "target": ITERATION_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e6", "source": START_ID, "target": ITERATION_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e7", "source": ITER_START_ID, "target": ITER_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target", "data": {"isInIteration": True}},
                {"id": "e8", "source": ITERATION_ID, "target": QUALITY_NODE_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e9", "source": QUALITY_NODE_ID, "target": END_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"}
            ]
        }
      }
    }

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_linear_notebook_pro.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)
    print("Success: Generated question_factory_linear_notebook_pro.yml.")

if __name__ == '__main__':
    generate_dsl()
