import yaml
import copy

with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

graph = data["workflow"]["graph"]
nodes = graph["nodes"]
edges = graph["edges"]

# 1. Find the code_extract_url node and modify its code and outputs
for node in nodes:
    if node["id"] == "code_extract_url":
        node["data"]["code"] = """import re
def main(search_result):
    text = str(search_result)
    # Find all http links
    urls = re.findall(r'https?://[^\\s"\\'>]+', text)
    
    # Filter and deduplicate
    clean_urls = []
    seen = set()
    for u in urls:
        if 'google.com' in u or 'youtube.com' in u or 'baidu.com' in u or u in seen:
            continue
        clean_urls.append(u)
        seen.add(u)
        
    # Pad to 5 if not enough
    while len(clean_urls) < 5:
        clean_urls.append("https://zh.wikipedia.org")
        
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

# 2. Find tool_firecrawl and clone it 5 times
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
    new_node["data"]["title"] = f"Firecrawl 节点 {i}"
    new_node["data"]["tool_parameters"]["url"]["value"] = f"{{{{#code_extract_url.url_{i}#}}}}"
    new_node["position"]["y"] = 400 + (i * 80)
    new_node["positionAbsolute"]["y"] = 400 + (i * 80)
    firecrawl_nodes.append(new_node)

nodes.extend(firecrawl_nodes)

# 3. Update edges
# Remove existing Firecrawl edges
edges = [e for e in edges if e["source"] != "tool_firecrawl" and e["target"] != "tool_firecrawl"]

# Add new edges
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

# 4. Update LLM prompt to include 5 contexts
for node in nodes:
    if node["id"] == "llm_generator":
        prompts = node["data"]["prompt_template"]
        for p in prompts:
            if p["role"] == "system":
                p["text"] = p["text"].replace(
                    "{{#tool_firecrawl.text#}}",
                    "\n".join([f"【参考资料 {i}】：\n{{{{#tool_firecrawl_{i}.text#}}}}" for i in range(1, 6)])
                )

# Ensure the prompt updates properly
with open("c:/Users/Auraa/Desktop/题库/question_factory_script_dsl_parallel.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Patch successful!")
