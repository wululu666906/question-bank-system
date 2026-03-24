import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

graph = data["workflow"]["graph"]
nodes = graph["nodes"]
edges = graph["edges"]

# 1. 升级 Code 节点为全能爬虫
for node in nodes:
    if node["id"] == "code_extract_url":
        node["id"] = "code_jina_scraper"
        node["data"]["title"] = "Jina 并发特种爬虫 (Code)"
        node["data"]["desc"] = "提取5条顶级链接，并纯代码请求 Jina Reader 原地爬取全文Markdown"
        node["data"]["code"] = """import re
import requests

def main(search_result):
    text = str(search_result)
    urls = re.findall(r'https?://[^\\s"\\'>]+', text)
    
    clean_urls = []
    seen = set()
    for u in urls:
        u_lower = u.lower()
        if any(ext in u_lower for ext in ['.jpg', '.png', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.css', '.js']):
            continue
        if 'gstatic.com' in u_lower or 'youtube.com' in u_lower or 'baidu.com' in u_lower:
            continue
        if u in seen:
            continue
        clean_urls.append(u)
        seen.add(u)
        if len(clean_urls) == 5:
            break
            
    combined_texts = []
    headers = {"User-Agent": "Mozilla/5.0 Dify-Agent"}
    
    for i, u in enumerate(clean_urls):
        try:
            res = requests.get(f"https://r.jina.ai/{u}", headers=headers, timeout=8)
            if res.status_code == 200:
                # 每个源限制 8000 字符，防止大模型 Token 撑爆
                article = res.text[:8000]
                combined_texts.append(f"【独立精选信息源 {i+1}】:\\n{article}")
        except:
            continue
            
    if not combined_texts:
        combined_texts.append("未能成功抓取到外部网页资料，请启动大模型深度内置知识库，强行满足用户出题指令。")
        
    return {"raw_materials": "\\n\\n".join(combined_texts)}
"""
        node["data"]["outputs"] = {
            "raw_materials": {"children": None, "type": "string"}
        }

# 2. 完全删除 Firecrawl 节点
firecrawl_node = None
for node in nodes:
    if node.get("id") == "tool_firecrawl":
        firecrawl_node = node
        break
if firecrawl_node:
    nodes.remove(firecrawl_node)

# 3. 重构边（Edges）：Start -> Google -> Jina Crawler -> LLM
new_edges = []
for edge in edges:
    # 删掉所有跟 firecrawl 和老 extracting 相关的旧线
    if "tool_firecrawl" in edge.get("source", "") or "tool_firecrawl" in edge.get("target", ""):
        continue
    if "code_extract_url" in edge.get("source", "") or "code_extract_url" in edge.get("target", ""):
        continue
    new_edges.append(edge)

# 添加新边：Google -> Jina Crawler
new_edges.append({
    "id": "edge-google-jina",
    "data": {"isInIteration": False, "sourceType": "tool", "targetType": "code"},
    "source": "tool_google_search",
    "sourceHandle": "source",
    "target": "code_jina_scraper",
    "targetHandle": "target",
    "type": "custom",
    "zIndex": 0
})

# 添加新边：Jina Crawler -> LLM
new_edges.append({
    "id": "edge-jina-llm",
    "data": {"isInIteration": False, "sourceType": "code", "targetType": "llm"},
    "source": "code_jina_scraper",
    "sourceHandle": "source",
    "target": "llm_generator",
    "targetHandle": "target",
    "type": "custom",
    "zIndex": 0
})

graph["edges"] = new_edges

# 4. 修改大模型提示词，指向新的 raw_materials
for node in nodes:
    if node["id"] == "llm_generator":
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                # 无论之前是什么占位符，统一强行替换
                new_text = p["text"]
                if "{{#tool_firecrawl.text#}}" in new_text:
                    new_text = new_text.replace("{{#tool_firecrawl.text#}}", "{{#code_jina_scraper.raw_materials#}}")
                elif "【独立来源参考" in new_text:
                    # 应对 possible v2/v3 修改痕迹，重置参考资料区块
                    pass
                else:
                    new_text = new_text.replace("{{#code_extract_url.target_url#}}", "{{#code_jina_scraper.raw_materials#}}") # fallback
                
                # 如果没被替换，强行覆盖写入
                if "{{#code_jina_scraper.raw_materials#}}" not in new_text:
                    new_text = new_text + "\\n\\n【深度原网页参考资料】：\\n{{#code_jina_scraper.raw_materials#}}"
                    
                p["text"] = new_text

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_jina.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Jina Scraper workflow successfully generated!")
