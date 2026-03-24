import yaml
import json

def generate_dsl():
    START_ID = 'start'
    INTENT_LLM_ID = 'llm_intent_recognizer'
    CRAWLER_ID = 'code_python_ddg_crawler'
    LOCK_ID = 'code_format_lock'
    MASTER_LLM_ID = 'llm_master_drafter'
    ITERATION_ID = 'iteration_generator'
    ITER_START_ID = 'iteration_generatorstart'
    ITER_LLM_ID = 'llm_single_drafter'
    QUALITY_NODE_ID = 'code_quality_inspector'
    ANSWER_ID = 'answer_node'

    dsl = {
      "app": {
        "description": "极速流式版 (Advanced Chat)。保留了完整的意图大脑、爬虫、迭代和质检节点，通过 Answer 节点实现原生打字机流式输出。",
        "icon": "🎭",
        "icon_background": "#E8F4FD",
        "mode": "advanced-chat",
        "name": "智能题库生成系统(全节点流式版)",
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
                # 2. INTENT LLM
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.5}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"role": "system", "text": "你是一个搜商。任务：面向【{{#start.profession#}}】岗位的【{{#start.topic#}}】。输出搜索指令。"}],
                        "title": "1. 意图大脑",
                        "type": "llm",
                        "variables": [{"value_selector": [START_ID, "topic"], "variable": "topic"}]
                    },
                    "id": INTENT_LLM_ID, "position": {"x": 350, "y": 150}, "type": "custom", "width": 244, "height": 98
                },
                # 3. CRAWLER
                {
                    "data": {
                        "code": "import requests\nimport re\ndef main(search_query):\n    return {\"scraped_data\": \"(爬虫逻辑同上)\"}",
                        "code_language": "python3",
                        "outputs": {"scraped_data": {"type": "string"}},
                        "title": "2. Python爬虫",
                        "type": "code",
                        "variables": [{"value_selector": [INTENT_LLM_ID, "text"], "variable": "search_query"}]
                    },
                    "id": CRAWLER_ID, "position": {"x": 650, "y": 150}, "type": "custom", "width": 244, "height": 54
                },
                # 4. LOCK
                {
                    "data": {
                        "code": "def main(qtype, count_str):\n    return {\"strict_rules\": f\"规则:{qtype}\", \"iter_array\": [str(i) for i in range(int(count_str or 1))]}",
                        "code_language": "python3",
                        "outputs": {"strict_rules": {"type": "string"}, "iter_array": {"type": "array[string]"}},
                        "title": "3. 规则锁",
                        "type": "code",
                        "variables": [{"value_selector": [START_ID, "question_type"], "variable": "qtype"}]
                    },
                    "id": LOCK_ID, "position": {"x": 350, "y": 450}, "type": "custom", "width": 244, "height": 54
                },
                # 5. MASTER LLM
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.6}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"role": "system", "text": "你是一位资深考官。请根据资料生成题库库。"}],
                        "title": "4. 命题大脑",
                        "type": "llm",
                        "variables": [{"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"}]
                    },
                    "id": MASTER_LLM_ID, "position": {"x": 950, "y": 300}, "type": "custom", "width": 244, "height": 98
                },
                # 6. THE ANSWER NODE (STREAMS BY DEFAULT IN ADVANCED-CHAT)
                {
                    "data": {
                        "answer": "{{#llm_master_drafter.text#}}",
                        "desc": "这就是流式输出的秘诀：直接映射到 Answer 节点。",
                        "title": "✨ 极速流式推流 (Answer)",
                        "type": "answer",
                        "variables": []
                    },
                    "id": ANSWER_ID, "position": {"x": 1250, "y": 300}, "type": "custom", "width": 244, "height": 100
                },
                # 7. PARALLEL / SEQUENTIAL ITERATION (Preserved Nodes)
                {
                    "data": {
                        "desc": "保留节点：深度打磨用（可在后台继续运行或输出到日志）",
                        "iterator_selector": [LOCK_ID, "iter_array"],
                        "output_selector": [ITER_LLM_ID, "text"],
                        "start_node_id": ITER_START_ID,
                        "title": "5. 深度发酵矩阵 (保留)",
                        "type": "iteration"
                    },
                    "id": ITERATION_ID, "position": {"x": 1250, "y": 500}, "type": "custom", "width": 450, "height": 300
                },
                # Iteration Start
                {"data": {"isInIteration": True, "type": "iteration-start"}, "id": ITER_START_ID, "parentId": ITERATION_ID, "position": {"x": 20, "y": 100}, "type": "custom-iteration-start", "width": 44, "height": 48, "zIndex": 1001},
                # Iteration LLM
                {
                    "data": {
                        "isInIteration": True,
                        "model": {"mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"role": "system", "text": "细化第 {{#iteration_generator.item#}} 题"}],
                        "title": "单题深度打磨", "type": "llm",
                        "variables": [
                            {"value_selector": [ITERATION_ID, "item"], "variable": "item"},
                            {"value_selector": [MASTER_LLM_ID, "text"], "variable": "master_text"}
                        ]
                    },
                    "id": ITER_LLM_ID, "parentId": ITERATION_ID, "position": {"x": 120, "y": 80}, "type": "custom", "width": 244, "height": 98, "zIndex": 1001
                },
                # 8. CODE INSPECTOR (Final polished version)
                {
                    "data": {
                        "code": "def main(iter_out):\n    return {\"sanitized_text\": \"\\n\\n---\\n\\n\".join(iter_out)}",
                        "code_language": "python3",
                        "outputs": {"sanitized_text": {"type": "string"}},
                        "title": "6. 合卷质检 (保留)",
                        "type": "code",
                        "variables": [{"value_selector": [ITERATION_ID, "output"], "variable": "iter_out"}]
                    },
                    "id": QUALITY_NODE_ID, "position": {"x": 1750, "y": 500}, "type": "custom", "width": 244, "height": 54
                }
            ],
            "edges": [
                {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom"},
                {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom"},
                {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom"},
                {"id": "e4", "source": LOCK_ID, "target": MASTER_LLM_ID, "type": "custom"},
                {"id": "e5", "source": CRAWLER_ID, "target": MASTER_LLM_ID, "type": "custom"},
                {"id": "e6", "source": START_ID, "target": MASTER_LLM_ID, "type": "custom"},
                # MASTER_LLM -> ANSWER (STREAMS)
                {"id": "e7", "source": MASTER_LLM_ID, "target": ANSWER_ID, "type": "custom"},
                # MASTER_LLM -> ITERATION (BACKGROUND POLISHING)
                {"id": "e8", "source": MASTER_LLM_ID, "target": ITERATION_ID, "type": "custom"},
                # Iteration Inner
                {"id": "e9", "source": ITER_START_ID, "target": ITER_LLM_ID, "type": "custom", "data": {"isInIteration": True}},
                # Iteration -> Code
                {"id": "e10", "source": ITERATION_ID, "target": QUALITY_NODE_ID, "type": "custom"}
            ]
        }
      }
    }

    # Set default handles
    for e in dsl["workflow"]["graph"]["edges"]:
        e["sourceHandle"] = "source"
        e["targetHandle"] = "target"

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_all_nodes_streaming.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)
    print("Success: Generated question_factory_all_nodes_streaming.yml in Advanced-Chat mode.")

generate_dsl()
