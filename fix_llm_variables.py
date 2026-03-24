import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

nodes = data["workflow"]["graph"]["nodes"]

for node in nodes:
    if node["id"] == "llm_generator":
        # CRITICAL FIX: Dify 需要 LLM 节点显式注册它订阅的变量，否则提示词里的插值会变为空白字符串！
        node["data"]["variables"] = [
            {"variable": "rules", "value_selector": ["code_constraint", "strict_rules"]},
            {"variable": "profession", "value_selector": ["start", "profession"]},
            {"variable": "topic", "value_selector": ["start", "topic"]},
            {"variable": "count", "value_selector": ["start", "question_count"]},
            {"variable": "diff", "value_selector": ["start", "difficulty"]},
            {"variable": "txt1", "value_selector": ["tool_firecrawl_1", "text"]},
            {"variable": "txt2", "value_selector": ["tool_firecrawl_2", "text"]},
            {"variable": "txt3", "value_selector": ["tool_firecrawl_3", "text"]},
            {"variable": "txt4", "value_selector": ["tool_firecrawl_4", "text"]},
            {"variable": "txt5", "value_selector": ["tool_firecrawl_5", "text"]}
        ]
        
        # 同时修改 Prompt 模板，使用显式注册的变量名，确保 Dify 解析器 100% 捕获
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                p["text"] = """你是一位拥有20年实战经验的【{{#start.profession#}}】领域资深考官与终极培训专家。

请结合以下全网页硬核资料以及你的深厚专业知识库进行出题：

【深度原网页参考资料】：
【独立来源 1】：
{{#tool_firecrawl_1.text#}}
【独立来源 2】：
{{#tool_firecrawl_2.text#}}
【独立来源 3】：
{{#tool_firecrawl_3.text#}}
【独立来源 4】：
{{#tool_firecrawl_4.text#}}
【独立来源 5】：
{{#tool_firecrawl_5.text#}}

【任务目标】：
围绕核心知识点【{{#start.topic#}}】，生成 {{#start.question_count#}} 道难度级别为【{{#start.difficulty#}}】的题目。

【绝对红线指标】：
1. 必须提供真实的行业业务场景作为题干背景。
2. 所有题目必须同时输出“深度解析”。
3. 绝对禁止输出任何废话，直接开始输出 Markdown 内容。"""

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Double Fix Applied: Variables explicitly registered in LLM node!")
