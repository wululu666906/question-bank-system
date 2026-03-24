import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

graph = data["workflow"]["graph"]
nodes = graph["nodes"]
edges = graph["edges"]

# 1. 精准清洗链接节点
for node in nodes:
    if node["id"] == "code_extract_url":
        node["data"]["code"] = """import re
def main(search_result):
    text = str(search_result)
    urls = re.findall(r'https?://[^\\s"\\'>]+', text)
    
    clean_urls = []
    seen = set()
    
    # 严格过滤垃圾链接和图片缓存链接
    for u in urls:
        u_lower = u.lower()
        if any(ext in u_lower for ext in ['.jpg', '.png', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.css', '.js']):
            continue
        if 'gstatic.com' in u_lower or 'google.com' in u_lower or 'youtube.com' in u_lower or 'baidu.com' in u_lower:
            continue
        if u in seen:
            continue
        clean_urls.append(u)
        seen.add(u)
        if len(clean_urls) == 5:
            break
            
    # 巧妙地用全网最轻量、没有有效内容的 example 网站占位，防止 Dify 节点失败或爬取超时
    while len(clean_urls) < 5:
        clean_urls.append("https://example.com")
        
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
        node["data"]["desc"] = "从谷歌结果中智能过滤缩略图，剥离5个纯正知识外链"

# 2. 克隆出5个并行沙虫节点
firecrawl_node = None
for node in nodes:
    if node["id"] == "tool_firecrawl":
        firecrawl_node = node
        break

nodes.remove(firecrawl_node)

firecrawl_nodes = []
for i in range(1, 6):
    new_node = copy.deepcopy(firecrawl_node)
    new_node["id"] = f"tool_firecrawl_{i}"
    new_node["data"]["title"] = f"Firecrawl 并发槽 {i}"
    new_node["data"]["tool_parameters"]["url"]["value"] = f"{{{{#code_extract_url.url_{i}#}}}}"
    new_node["position"]["y"] = 400 + (i * 90)
    new_node["positionAbsolute"]["y"] = 400 + (i * 90)
    firecrawl_nodes.append(new_node)

nodes.extend(firecrawl_nodes)

# 3. 编排连线矩阵
edges = [e for e in edges if e["source"] != "tool_firecrawl" and e["target"] != "tool_firecrawl"]

base_edge_in = {
    "data": {"isInIteration": False, "sourceType": "code", "targetType": "tool"},
    "source": "code_extract_url",
    "sourceHandle": "source",
    "targetHandle": "target",
    "type": "custom",
    "zIndex": 0
}
base_edge_out = {
    "data": {"isInIteration": False, "sourceType": "tool", "targetType": "llm"},
    "sourceHandle": "source",
    "target": "llm_generator",
    "targetHandle": "target",
    "type": "custom",
    "zIndex": 0
}

for i in range(1, 6):
    edge_in = copy.deepcopy(base_edge_in)
    edge_in["id"] = f"edge-extract-firecrawl-{i}"
    edge_in["target"] = f"tool_firecrawl_{i}"
    edges.append(edge_in)
    
    edge_out = copy.deepcopy(base_edge_out)
    edge_out["id"] = f"edge-firecrawl-llm-{i}"
    edge_out["source"] = f"tool_firecrawl_{i}"
    edges.append(edge_out)

graph["edges"] = edges

# 4. 指路给最终生成节点
for node in nodes:
    if node["id"] == "llm_generator":
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                # Clean up legacy contexts if re-running
                text = p["text"]
                if "【深度原网页参考资料】" in text:
                    text = text.replace(
                        "{{#tool_firecrawl.text#}}", 
                        "\n".join([f"【独立来源参考 {i}】：\n{{{{#tool_firecrawl_{i}.text#}}}}" for i in range(1, 6)])
                    )
                p["text"] = text

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_parallel.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Patch v3 successfully generated!")
