import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

nodes = data["workflow"]["graph"]["nodes"]

for node in nodes:
    if node["id"] == "llm_generator":
        # 彻底重写 LLM 节点的变量声明，映射到短变量名
        node["data"]["variables"] = [
            {"variable": "rules", "value_selector": ["code_constraint", "strict_rules"]},
            {"variable": "profession", "value_selector": ["start", "profession"]},
            {"variable": "topic", "value_selector": ["start", "topic"]},
            {"variable": "count", "value_selector": ["start", "question_count"]},
            {"variable": "difficulty", "value_selector": ["start", "difficulty"]},
            {"variable": "txt1", "value_selector": ["tool_firecrawl_1", "text"]},
            {"variable": "txt2", "value_selector": ["tool_firecrawl_2", "text"]},
            {"variable": "txt3", "value_selector": ["tool_firecrawl_3", "text"]},
            {"variable": "txt4", "value_selector": ["tool_firecrawl_4", "text"]},
            {"variable": "txt5", "value_selector": ["tool_firecrawl_5", "text"]}
        ]
        
        # 提示词改为使用局部短变量名 {{variable}}，这是 Dify 最稳定的变量引用方式
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                p["text"] = """{{rules}}

你是一位拥有20年实战经验的【{{profession}}】领域资深考官与终极培训专家。

请结合以下通过反爬拿到的全网页资料进行出题：

【深度原网页参考资料】：
【独立来源 1】：{{txt1}}
【独立来源 2】：{{txt2}}
【独立来源 3】：{{txt3}}
【独立来源 4】：{{txt4}}
【独立来源 5】：{{txt5}}

【任务目标】：
围绕知识点【{{topic}}】，生成 {{count}} 道难度为【{{difficulty}}】的题目。

【绝对红线指标】：
1. 必须提供真实的行业业务场景。
2. 所有题目必须同时输出“深度解析”。
3. 绝对禁止输出任何废话，直接开始输出 Markdown 内容。"""

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Final DSL Polish Applied: Fixed variable binding using local aliases.")
