import yaml

def patch_dsl():
    path = r'c:\Users\Auraa\Desktop\题库\question_factory_ddg_iteration.yml'
    with open(path, 'r', encoding='utf-8') as f:
        dsl = yaml.safe_load(f)

    # 1. 找到节点 4 (llm_single_drafter) 并修改提示词
    for node in dsl['workflow']['graph']['nodes']:
        if node['id'] == 'llm_single_drafter':
            # 简化提示词，移除层级标题和 Emoji 要求
            node['data']['prompt_template'][0]['text'] = """{{#code_format_lock.strict_rules#}}

你是一位专业的教育研究员。请基于以下抓取资料，为【{{#start.topic#}}】生成下一道高质量题目。

【排版规范】：
1. 整体风格：使用简洁、清爽的专业文档排版（如同执法规范或专业教材）。
2. 标题引导：使用简单的加粗标题，如 **一、修订专题分析** 或 **1. [题目名称]**。
3. 段落引导：使用 **问题描述：** 和 **解答：**。禁止使用 Emoji。
4. 自然语言：语气平实、逻辑严密，不要有花哨的装饰。

资料参考：
{{#code_python_ddg_crawler.scraped_data#}}
"""
            print("Node 4 Prompt patched.")

        # 2. 找到节点 5 (code_quality_inspector) 并修改代码
        if node['id'] == 'code_quality_inspector':
            # 彻底移除所有装饰性 Header/Footer 和分割线
            node['data']['code'] = """import re

def main(iteration_output_array):
    # 1. 使用双换行自然连接，移除之前的 --- 分割线
    full_text = "\\n\\n".join(iteration_output_array)
    
    # 2. 确保换行符不过度堆叠
    full_text = re.sub(r'\\n{3,}', '\\n\\n', full_text)

    # 3. 基础数学公式渲染兼容（这是为了确保像 $x$ 或 $$y$$ 能正确显示）
    full_text = full_text.replace(r'\\\\[', '$$').replace(r'\\\\]', '$$')
    full_text = full_text.replace(r'\\(', '$').replace(r'\\)', '$')
    
    # 4. 直接输出内容，不加任何“质检功过”字样的开头和结尾
    return {"sanitized_text": full_text.strip()}"""
            node['data']['desc'] = "极致简约排版：移除所有装饰性元素，仅保留核心文本与公式兼容性。"
            print("Node 5 Code patched.")

    # 3. 保存回原文件
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, sort_keys=False)
    print(f"Success: {path} has been updated to match Image 2 style.")

if __name__ == '__main__':
    patch_dsl()
