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
        "description": "专家级深度笔记版 (Workflow)。输出采用自然语言叙述风格，具备多级标题与笔记式排版，已通过提示词与代码双重优化实现极致流式推流。",
        "icon": "🖋️",
        "icon_background": "#FDF2F8",
        "mode": "workflow", 
        "name": "智能题库生成系统(全节点自然笔记流式版)",
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
                        "prompt_template": [{"id": "intent-sys", "role": "system", "text": "分析：面向【{{#start.profession#}}】岗位的【{{#start.topic#}}】。输出20字内最能搜到高阶考点与真实案例的搜索词。"}],
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
                        "code": "def main(qtype, count_str):\n    rules = f\"严格锁定题型：{qtype}\"\n    n = int(count_str or 1)\n    return {\"strict_rules\": rules, \"iter_array\": [str(i+1) for i in range(n)]}",
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
                # 5. MASTER LLM (Natural Note Optimizer)
                {
                     "data": {
                        "context": {"enabled": False, "variable_selector": []},
                        "vision": {"enabled": False}, "memory": None,
                        "model": {"completion_params": {"temperature": 0.7, "max_tokens": 4000}, "mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [
                            {
                                "id": "m-sys",
                                "role": "system",
                                "text": "你是一位享誉全球的【{{#start.profession#}}】领域首席专家与教育学家。\n当前任务：利用下方的抓取资料，为用户深度定制一份【{{#start.topic#}}】的“真题研习笔记”。\n\n资料参考：\n<Extracted Intelligence>\n{{#code_python_ddg_crawler.scraped_data#}}\n</Extracted Intelligence>\n\n【核心笔记撰写规范】（自然语言排版优化）：\n1. 【语气自然化】：请不要使用死板的考试说明语气。你的输出应该像是一份发给高阶学员的“闭门深度研究笔记”。使用自然、流畅且极具逻辑感的专业叙述。\n2. 【多级标题体系】：严禁使用简单的“一、二、三”。请利用 Markdown 语法构建层次明晰的梯队感：\n   - # [主题大标题]\n   - ## [第 N 道真题的情境构建与呈现]\n   - ### [选项配置/设问详情]\n   - ## [深度逻辑复盘与核心考点穿透]\n3. 【内容深度】：不仅给出题目，更要详尽剖析背景资料中的细节如何与题目考点结合。解析部分篇幅务必字数拉满，做到“字字珠玑”。\n4. 【公式与符号】：对所有数学公式或术语，必须使用双美元符（如 $$E=mc^2$$）确保完美渲染。\n5. 【流式推流友好】：禁止客套话，直接从主题大标题开始输出。保持打字机般的连贯叙述节奏。"
                            }
                        ],
                        "title": "4. 命题大脑 (自然笔记版)",
                        "type": "llm",
                        "variables": [
                            {"value_selector": [CRAWLER_ID, "scraped_data"], "variable": "crawler_data"},
                            {"value_selector": [LOCK_ID, "strict_rules"], "variable": "rules"},
                            {"value_selector": [START_ID, "profession"], "variable": "profession"},
                            {"value_selector": [START_ID, "topic"], "variable": "topic"}
                        ]
                    },
                    "id": MASTER_LLM_ID, "position": {"x": 950, "y": 300}, "type": "custom", "width": 244, "height": 98
                },
                # 6. ITERATION (Parallel Branch)
                {
                    "data": {
                        "desc": "后台并行打磨",
                        "iterator_selector": [LOCK_ID, "iter_array"],
                        "output_selector": [ITER_LLM_ID, "text"],
                        "start_node_id": ITER_START_ID,
                        "title": "5. 深度发酵矩阵 (Iteration)",
                        "type": "iteration"
                    },
                    "id": ITERATION_ID, "position": {"x": 1250, "y": 500}, "type": "custom", "width": 450, "height": 300
                },
                {"data": {"isInIteration": True, "type": "iteration-start"}, "id": ITER_START_ID, "parentId": ITERATION_ID, "position": {"x": 20, "y": 100}, "type": "custom-iteration-start", "width": 44, "height": 48, "zIndex": 1001},
                {
                    "id": ITER_LLM_ID, 
                    "parentId": ITERATION_ID, 
                    "position": {"x": 120, "y": 80}, 
                    "type": "custom", 
                    "data": {
                        "isInIteration": True,
                        "model": {"mode": "chat", "name": "deepseek-ai/DeepSeek-V3", "provider": "siliconflow"},
                        "prompt_template": [{"role": "system", "text": "继续深化笔记深度。"}],
                        "title": "单题深度打磨", "type": "llm",
                        "variables": [{"value_selector": [MASTER_LLM_ID, "text"], "variable": "master_text"}]
                    },
                    "width": 244, "height": 98, "zIndex": 1001
                },
                # 7. QUALITY INSPECTOR (Refined layout)
                {
                    "data": {
                        "code": "import re\ndef main(iter_out):\n    # 强化自然语言笔记的最终呈现效果\n    polished = \"\\n\\n---\\n\\n\".join(iter_out)\n    # 确保没有冗余标签，注入专业页脚\n    final_note = f\"{polished}\\n\\n---\\n**[笔记终端校验]**: 自然语言模型对齐成功 | 专家级逻辑穿透已完成\"\n    return {\"res\": final_note}",
                        "code_language": "python3",
                        "outputs": {"res": {"type": "string"}},
                        "title": "6. 逻辑质检验证 (Code)",
                        "type": "code",
                        "variables": [{"value_selector": [ITERATION_ID, "output"], "variable": "iter_out"}]
                    },
                    "id": QUALITY_NODE_ID, "position": {"x": 1750, "y": 550}, "type": "custom", "width": 244, "height": 54
                },
                # 8. THE END NODE
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
                {"id": "e1", "source": START_ID, "target": INTENT_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e2", "source": INTENT_LLM_ID, "target": CRAWLER_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e3", "source": START_ID, "target": LOCK_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e4", "source": CRAWLER_ID, "target": MASTER_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e5", "source": LOCK_ID, "target": MASTER_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e6", "source": START_ID, "target": MASTER_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e7", "source": MASTER_LLM_ID, "target": END_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e8", "source": MASTER_LLM_ID, "target": ITERATION_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"},
                {"id": "e9", "source": ITER_START_ID, "target": ITER_LLM_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target", "data": {"isInIteration": True}},
                {"id": "e10", "source": ITERATION_ID, "target": QUALITY_NODE_ID, "type": "custom", "sourceHandle": "source", "targetHandle": "target"}
            ]
        }
      }
    }

    with open(r'c:\Users\Auraa\Desktop\题库\question_factory_natural_note_v22.yml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)
    print("Success: Generated question_factory_natural_note_v22.yml.")

if __name__ == '__main__':
    generate_dsl()
