import yaml
import json
import uuid
import os

def generate_dify_dsl(output_file="dify_workflow.yml"):
    dsl = {
        "app": {
            "description": "通过HTTP请求外部自建Python API，实现联网搜索、反爬网页提取，并在外部进行题目生成及Prompt反思优化的完整工作流。",
            "icon": "🧠",
            "icon_background": "#F5F8FF",
            "mode": "workflow",
            "name": "外部API智能出题引擎"
        },
        "kind": "app",
        "version": "0.1.2",
        "workflow": {
            "environment_variables": [],
            "features": {
                "file_upload": {
                    "image": {"enabled": False, "number_limits": 3, "transfer_methods": ["local_file", "remote_url"]}
                },
                "opening_statement": "",
                "retriever_resource": {"enabled": True},
                "sensitive_word_avoidance": {"enabled": False},
                "speech_to_text": {"enabled": False},
                "suggested_questions": [],
                "suggested_questions_after_answer": {"enabled": False},
                "text_to_speech": {"enabled": False, "language": "", "voice": ""}
            },
            "graph": {
                "edges": [
                    {
                        "data": {"isInIteration": False, "sourceType": "start", "targetType": "http-request"},
                        "id": "start-http_request",
                        "source": "start",
                        "sourceHandle": "source",
                        "target": "http_request",
                        "targetHandle": "target",
                        "type": "custom"
                    },
                    {
                        "data": {"isInIteration": False, "sourceType": "http-request", "targetType": "end"},
                        "id": "http_request-end",
                        "source": "http_request",
                        "sourceHandle": "source",
                        "target": "end",
                        "targetHandle": "target",
                        "type": "custom"
                    }
                ],
                "nodes": [
                    {
                        "data": {
                            "desc": "输入出题主题及本地API地址",
                            "selected": False,
                            "title": "开始",
                            "type": "start",
                            "variables": [
                                {
                                    "label": "知识点/主题",
                                    "max_length": 256,
                                    "options": [],
                                    "required": True,
                                    "type": "text-input",
                                    "variable": "topic"
                                },
                                {
                                    "label": "API地址 (默认 http://127.0.0.1:8000)",
                                    "max_length": 256,
                                    "options": [],
                                    "required": True,
                                    "type": "text-input",
                                    "variable": "api_url"
                                }
                            ]
                        },
                        "height": 115,
                        "id": "start",
                        "position": {"x": 80, "y": 282},
                        "positionAbsolute": {"x": 80, "y": 282},
                        "selected": False,
                        "sourcePosition": "right",
                        "targetPosition": "left",
                        "type": "custom",
                        "width": 244
                    },
                    {
                        "data": {
                            "authorization": {"config": None, "type": "no-auth"},
                            "body": {
                                "data": "{\n  \"topic\": \"{{#start.topic#}}\"\n}",
                                "type": "json"
                            },
                            "desc": "请求外部自建Python API",
                            "headers": "Content-Type: application/json",
                            "method": "post",
                            "params": "",
                            "selected": False,
                            "timeout": {
                                "connect": 60,
                                "read": 300,
                                "write": 100
                            },
                            "title": "HTTP 请求外部出题API",
                            "type": "http-request",
                            "url": "{{#start.api_url#}}/api/generate_questions",
                            "variables": []
                        },
                        "height": 105,
                        "id": "http_request",
                        "position": {"x": 384, "y": 282},
                        "positionAbsolute": {"x": 384, "y": 282},
                        "selected": False,
                        "sourcePosition": "right",
                        "targetPosition": "left",
                        "type": "custom",
                        "width": 244
                    },
                    {
                        "data": {
                            "desc": "输出生成的题目JSON",
                            "outputs": [
                                {
                                    "value_selector": ["http_request", "body"],
                                    "variable": "final_questions_json"
                                }
                            ],
                            "selected": False,
                            "title": "结束",
                            "type": "end"
                        },
                        "height": 90,
                        "id": "end",
                        "position": {"x": 688, "y": 282},
                        "positionAbsolute": {"x": 688, "y": 282},
                        "selected": False,
                        "sourcePosition": "right",
                        "targetPosition": "left",
                        "type": "custom",
                        "width": 244
                    }
                ]
            }
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"Dify DSL file successfully generated at: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    generate_dify_dsl()
