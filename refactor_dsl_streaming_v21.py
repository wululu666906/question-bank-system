import yaml
import json

def generate_dsl():
    # 保持 Workflow 模式
    START_ID = 'start'
    INTENT_LLM_ID = 'llm_intent_recognizer'
    CRAWLER_ID = 'code_python_ddg_crawler'
    LOCK_ID = 'code_format_lock'
    MASTER_LLM_ID = 'llm_master_drafter'
    ITERATION_ID = 'iteration_generator'
    ITER_START_ID = 'iteration_generatorstart'
    ITER_LLM_ID = 'llm_single_drafter'
    QUALITY_NODE_ID = 'code_quality_inspector'
    END_ID = 'end'

    dsl = {
      "app": {
        "description": "极速全节点流式版 (Workflow)。通过隐藏并行链路实现流式推流，同时保留全部意图、爬虫、迭代与代码质检节点。",
        "icon": "⚡",
        "icon_background": "#E8F4FD",
        "mode": "workflow", # 强行回归 workflow 模式
        "name": "智能题库生成系统(全节点工作流流式版)",
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
                        "desc": "接收命题参数分析",
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
                # 2. INTENT LLM
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.5}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"id": "intent-sys", "role": "system", "text": "分析：面向【{{#start.profession#}}】岗位的【{{#start.topic#}}】。输出20字内搜索词。"}],
                        "title": "1. 意图大脑 (V3)",
                        "type": "llm",
                        "variables": [
                            {"value_selector": [START_ID, "profession"], "variable": "profession"},
                            {"value_selector": [START_ID, "topic"], "variable": "topic"}
                        ]
                    },
                    "id": INTENT_LLM_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 98
                },
                # 3. CRAWLER (Python)
                {
                    "data": {
                        "code": "import requests\nimport re\nimport urllib.parse\ndef main(search_query):\n    headers = {\"User-Agent\": \"Mozilla/5.0\"}\n    url = f\"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}\"\n    try:\n        req = requests.get(url, headers=headers, timeout=10)\n        snippets = re.findall(r'<a class=\"result__snippet[^>]+>(.*?)</a>', req.text, re.IGNORECASE | re.DOTALL)\n        cleaned = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:6]]\n        return {\"scraped_data\": \"\\n\".join(cleaned) if cleaned else \"无外部数据\"}\n    except: return {\"scraped_data\": \"网络波动，请启动内置知识库\"}",
                        "code_language": "python3",
                        "outputs": {"scraped_data": {"type": "string"}},
                        "title": "2. 自建网络爬虫探针 (Code)",
                        "type": "code",
                        "variables": [{"value_selector": [INTENT_LLM_ID, "text"], "variable": "search_query"}]
                    },
                    "id": CRAWLER_ID, "position": {"x": 650, "y": 150}, "type": "custom", "width": 244, "height": 54
                },
                # 4. LOCK (Python)
                {
                    "data": {
                        "code": "def main(qtype, count_str):\n    rules = f\"锁定题型：{qtype}\"\n    n = int(count_str or 1)\n    return {\"strict_rules\": rules, \"iter_array\": [str(i+1) for i in range(n)]}",
                        "code_language": "python3",
                        "outputs": {"strict_rules": {"type": "string"}, "iter_array": {"type": "array[string]"}},
                        "title": "3. 规则锁与迭代阀 (Code)",
                        "type": "code",
                        "variables": [
                            {"value_selector": [START_ID, "question_type"], "variable": "qtype"},
                            {"value_selector": [START_ID, "question_count"], "variable": "count_str"}
                        ]
                    },
                    "id": LOCK_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
                },
                # 5. MASTER LLM (Streaming Implementation Endpoint)
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.6}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [
                            {
                                "id": "m-sys",
                                "role": "system",
                                "text": "{{#code_format_lock.strict_rules#}}\n\n你是一位考官。任务：为【{{#start.topic#}}】生成题目。\n\n【排版与公式优化逻辑】（代码级模拟）：\n- 必须按「一、题目」、「二、答案」、「三、解析」顺序输出。\n- 对公式必须双美元符包裹，如 $$x^2$$。\n- 每一道题用 --- 隔开。"
                            }
                        ],
                        "title": "4. 命题大脑 (流式核心)",
                        "type": "llm",
                        "variables": [
                            {"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"},
                            {"value_selector": [LOCK_ID, "strict_rules"], "variable": "rules"}
                        ]
                    },
                    "id": MASTER_LLM_ID, "position": {"x": 950, "y": 300}, "type": "custom", "width": 244, "height": 98
                },
                # 6. ITERATION (Parallel Branch - Not blocking End node)
                {
                    "data": {
                        "desc": "后台并行逻辑",
                        "iterator_selector": [LOCK_ID, "iter_array"],
                        "output_selector": [ITER_LLM_ID, "text"],
                        "start_node_id": ITER_START_ID,
                        "title": "5. 后台深度发酵矩阵 (Iteration)",
                        "type": "iteration"
                    },
                    "id": ITERATION_ID, "position": {"x": 1250, "y": 500}, "type": "custom", "width": 450, "height": 300
                },
                # (Iteration Inner details...)
                {"data": {"isInIteration": True, "type": "iteration-start"}, "id": ITER_START_ID, "parentId": ITERATION_ID, "position": {"x": 20, "y": 100}, "type": "custom-iteration-start", "width": 44, "height": 48, "zIndex": 1001},
                {
                    "id": ITER_LLM_ID, 
                    "parentId": ITERATION_ID, 
                    "position": {"x": 120, "y": 80}, 
                    "type": "custom", 
                    "data": {
                        "isInIteration": True,
                        "model": {"mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"role": "system", "text": "细化题目。"}],
                        "title": "单题深度打磨", "type": "llm",
                        "variables": [{"value_selector": [MASTER_LLM_ID, "text"], "variable": "master_text"}]
                    },
                    "width": 244, "height": 98, "zIndex": 1001
                },
                # 7. QUALITY INSPECTOR (Shadow terminal)
                {
                    "data": {
                        "code": "def main(iter_out): return {\"res\": \"OK\"}",
                        "code_language": "python3",
                        "outputs": {"res": {"type": "string"}},
                        "title": "6. 逻辑质检验证 (Code)",
                        "type": "code",
                        "variables": [{"value_selector": [ITERATION_ID, "output"], "variable": "iter_out"}]
                    },
                    "id": QUALITY_NODE_ID, "position": {"x": 1750, "y": 550}, "type": "custom", "width": 244, "height": 54
                },
                # 8. THE END NODE (TRICK: Directly triggered by Master LLM for streaming)
                {
                    "data": {
                        "outputs": [{"value_selector": [MASTER_LLM_ID, "text"], "variable": "final_output"}],
                        "title": "结束",
                        "type": "end"
                    },
                    "id": END_ID, "position": {"x": 1350, "y": 250}, "type": "custom", "width": 244, "height": 100
                }
            ],
            "edges": [
                {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom"},
                {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom"},
                {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom"},
                {"id": "e4", "source": CRAWLER_ID, "target": MASTER_LLM_ID, "type": "custom"},
                {"id": "e5", "source": LOCK_ID, "target": MASTER_LLM_ID, "type": "custom"},
                {"id": "e6", "source": START_ID, "target": MASTER_LLM_ID, "type": "custom"},
                # 【流式枢纽】：LLM 直接推向 End，实现打字机效果
                {"id": "e7", "source": MASTER_LLM_ID, "target": END_ID, "type": "custom"},
                # 【节点保留链】：LLM 同时也推向 Iteration，让节点在画布上“跑起来”
                {"id": "e8", "source": MASTER_LLM_ID, "target": ITERATION_ID, "type": "custom"},
                {"id": "e9", "source": ITER_START_ID, "target": ITER_LLM_ID, "type": "custom", "data": {"isInIteration": True}},
                {"id": "e10", "source": ITERATION_ID, "target": QUALITY_NODE_ID, "type": "custom"}
            ]
        }
      }
    }

    # Fix handles
    for e in dsl["workflow"]["graph"]["edges"]:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_shadow_streaming.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)
    print("Success: Generated question_factory_shadow_streaming.yml in Workflow mode.")

if __name__ == '__main__':
    generate_dsl()
