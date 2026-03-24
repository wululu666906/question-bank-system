import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

nodes = data["workflow"]["graph"]["nodes"]

for node in nodes:
    if node["id"] == "llm_generator":
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                # 构建完整的、安全的、符合逻辑的提示词
                p["text"] = """你是一位拥有20年实战经验的【{{#start.profession#}}】领域资深考官与终极培训专家。

请结合以下通过强制反爬拿到的全网页硬核资料以及你的深厚专业知识库进行出题：

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
1. 必须提供真实的行业业务场景作为题干背景，拒绝干瘪的纯理论问答，要求高度贴合实际工作。
2. 若为选择题，干扰选项必须具有极强的迷惑性。
3. 所有题目必须同时输出“深度解析”，逐一剖析错误选项。
4. 绝对禁止输出任何废话，直接开始输出题目内容。
5. 必须采用清晰严谨的 Markdown 排版，符合专业题库质感。"""

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Final Fix Applied: Prompt instructions restored!")
