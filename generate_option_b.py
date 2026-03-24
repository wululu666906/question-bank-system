import yaml
import copy

# 基准文件
with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

graph = data["workflow"]["graph"]
nodes = graph["nodes"]
edges = graph["edges"]

# 1. 修复代码节点：提取前 5 条链接，并根据用户反馈严格过滤垃圾
for node in nodes:
    if node["id"] == "code_extract_url" or node.get("id") == "code_jina_scraper":
        node["id"] = "code_extract_url"
        node["data"]["title"] = "并发外链提取 (Code)"
        node["data"]["code"] = """import re
def main(search_result):
    text = str(search_result)
    urls = re.findall(r'https?://[^\\s"\\'>]+', text)
    
    clean_urls = []
    seen = set()
    for u in urls:
        u_lower = u.lower()
        if any(ext in u_lower for ext in ['.jpg', '.png', '.jpeg', '.gif', '.ico', '.svg', '.webp']):
            continue
        if 'gstatic.com' in u_lower or 'youtube.com' in u_lower or 'baidu.com' in u_lower:
            continue
        if u in seen:
            continue
        clean_urls.append(u)
        seen.add(u)
        if len(clean_urls) == 5:
            break
            
    # 填充百度百科作为稳定可靠的兜底源
    while len(clean_urls) < 5:
        clean_urls.append("https://baike.baidu.com/item/%E5%9C%86%E9%94%A5%E6%9B%B2%E7%BA%BF")
        
    return {
        "url_1": clean_urls[0],
        "url_2": clean_urls[1],
        "url_3": clean_urls[2],
        "url_4": clean_urls[3],
        "url_5": clean_urls[4]
    }
"""
        node["data"]["outputs"] = {
            f"url_{i}": {"children": None, "type": "string"} for i in range(1, 6)
        }

# 2. 定位 Firecrawl 模板并克隆
firecrawl_node = None
for node in nodes:
    # 兼容之前可能被改名的旧节点
    if "firecrawl" in node["id"].lower() or "scrape" in node["id"].lower():
        firecrawl_node = node
        break

# 如果找不到，手动重建一个标准的内置爬虫节点
if not firecrawl_node:
    firecrawl_node = {
        "id": "tool_firecrawl",
        "data": {
            "desc": "专破反爬系统，提取全文Markdown",
            "provider_id": "firecrawl",
            "provider_name": "firecrawl",
            "provider_type": "builtin",
            "tool_label": "Firecrawl Scrape",
            "tool_name": "scrape",
            "tool_parameters": {"url": {"type": "mixed", "value": ""}},
        },
        "type": "custom",
    }

# 清理旧节点
nodes = [n for n in nodes if not ("firecrawl" in n["id"].lower() or "scraper" in n["id"].lower())]

firecrawl_nodes = []
for i in range(1, 6):
    new_node = copy.deepcopy(firecrawl_node)
    new_node["id"] = f"tool_firecrawl_{i}"
    new_node["data"]["title"] = f"Firecrawl 并发槽 {i}"
    new_node["data"]["tool_parameters"]["url"]["value"] = f"{{{{#code_extract_url.url_{i}#}}}}"
    new_node["position"] = {"x": 950, "y": 400 + (i * 90)}
    new_node["positionAbsolute"] = {"x": 950, "y": 400 + (i * 90)}
    firecrawl_nodes.append(new_node)
nodes.extend(firecrawl_nodes)

# 3. 连线重组
edges = [e for e in edges if not ("firecrawl" in str(e).lower() or "scraper" in str(e).lower())]
# 确保 Google -> Code 连着
edges = [e for e in edges if not (e["source"] == "tool_google_search" and e["target"] == "code_extract_url")]
edges.append({
    "id": "edge-google-code",
    "source": "tool_google_search",
    "target": "code_extract_url",
    "sourceHandle": "source",
    "targetHandle": "target",
    "type": "custom",
    "data": {"sourceType": "tool", "targetType": "code"}
})

for i in range(1, 6):
    # Code -> Firecrawl
    edges.append({
        "id": f"edge-code-fc-{i}",
        "source": "code_extract_url",
        "target": f"tool_firecrawl_{i}",
        "sourceHandle": "source",
        "targetHandle": "target",
        "type": "custom",
        "data": {"sourceType": "code", "targetType": "tool"}
    })
    # Firecrawl -> LLM
    edges.append({
        "id": f"edge-fc-llm-{i}",
        "source": f"tool_firecrawl_{i}",
        "target": "llm_generator",
        "sourceHandle": "source",
        "targetHandle": "target",
        "type": "custom",
        "data": {"sourceType": "tool", "targetType": "llm"}
    })

graph["nodes"] = nodes
graph["edges"] = edges

# 4. 最终 LLM 提示词同步 & 变量名同步至 result
for node in nodes:
    if node["id"] == "llm_generator":
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                p["text"] = p["text"].replace("{{#code_jina_scraper.raw_materials#}}", "") # 清理
                materials = "\\n".join([f"【独立来源 {i}】：\\n{{{{#tool_firecrawl_{i}.text#}}}}" for i in range(1, 6)])
                if "【深度原网页参考资料】" in p["text"]:
                    p["text"] = p["text"].split("【深度原网页参考资料】")[0] + "【深度原网页参考资料】：\\n" + materials
                else:
                    p["text"] += "\\n\\n【深度原网页参考资料】：\\n" + materials
    
    if node["id"] == "end":
        node["data"]["outputs"][0]["variable"] = "result" # 同步用户刚才的前端修改

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_option_b.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Option B DSL generated successfully!")
