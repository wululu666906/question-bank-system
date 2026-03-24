import logging
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Default API Base and Key
DEFAULT_API_BASE = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3"

def get_llm_client():
    api_key = os.environ.get("LLM_API_KEY", "")
    api_base = os.environ.get("LLM_API_BASE", DEFAULT_API_BASE)
    if not api_key:
        logger.warning("LLM_API_KEY not found in environment variables. Calls may fail if required.")
    
    return OpenAI(api_key=api_key or "empty", base_url=api_base)

def clean_json_output(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate_questions_initial(context: str, topic: str, model: str = DEFAULT_MODEL) -> dict:
    client = get_llm_client()
    system_prompt = f"""
    你是一个专业的教育内容开发者。请根据以下参考资料，为主题 '{topic}' 生成高质量的练习题。
    要求：
    1. 生成包含 3 道选择题和 1 道简答题。
    2. 题目必须与参考资料高度相关，避免超出资料范围的过度发散。
    3. 输出必须是一个合法的 JSON 对象，不要包含任何多余文字，格式如下：
    {{
        "questions": [
            {{
                "type": "multiple_choice",
                "question": "题目内容",
                "options": ["A", "B", "C", "D"],
                "answer": "A",
                "explanation": "解析内容"
            }},
            {{
                "type": "short_answer",
                "question": "题目内容",
                "answer": "标准答案核心点",
                "explanation": "解析内容"
            }}
        ]
    }}
    """
    
    user_prompt = f"参考资料：\n{context}\n\n请严格按照JSON格式输出题目："
    
    logger.info("Calling LLM for initial question generation...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        
        result_text = clean_json_output(response.choices[0].message.content)
        return json.loads(result_text)
    except Exception as e:
        logger.error(f"Error during initial generation: {e}")
        return {"error": str(e), "raw_output": locals().get('result_text', '')}

def evaluate_and_refine(questions_json: dict, context: str, topic: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Evaluates the generated questions. If they lack quality, generates a better prompt and regenerates.
    """
    client = get_llm_client()
    
    eval_prompt = f"""
    请作为一位资深学科教研专家，评估以下由AI基于主题 "{topic}" 生成的题目。
    评估标准：
    1. 知识准确性（是否符合事实，是否有歧义）
    2. 区分度与深度（题目是否过于简单或是过于生僻）
    3. 格式合法性（必须符合原始要求的 JSON 数组结构）
    
    生成的题目：
    {json.dumps(questions_json, ensure_ascii=False, indent=2)}
    
    请仔细思考，并严格只输出合法的 JSON 格式数据，结构如下：
    {{
        "score": 85, // 0-100分
        "feedback": "哪里做得不好或有何改进空间，请具体指出",
        "needs_refinement": true, // 若认为无法作为最终试题发布，则设为true (例如 score < 85)
        "improved_system_prompt": "如果 needs_refinement 为 true，请输出一个新的、更严厉、要求更明确的 System Prompt（告诉下一次生成的AI如何规避当前的问题）。否则留空字符串。"
    }}
    """
    
    logger.info("Evaluating generated questions (Self-Reflection)...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.3
        )
        
        eval_result = clean_json_output(response.choices[0].message.content)
        evaluation = json.loads(eval_result)
        logger.info(f"Evaluation Score: {evaluation.get('score')} - feedback: {evaluation.get('feedback')}")
        
        if evaluation.get('needs_refinement', False) and evaluation.get('improved_system_prompt'):
            logger.info("Score is low. Refining questions with the new improved prompt...")
            system_prompt = evaluation.get('improved_system_prompt')
            user_prompt = f"参考资料：\n{context}\n\n请直接紧跟参考资料，输出符合新要求的最严谨的JSON格式题目："
            
            refine_res = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6 # slightly lower temp for refinement
            )
            
            final_text = clean_json_output(refine_res.choices[0].message.content)
            final_qs = json.loads(final_text)
            return {"final_questions": final_qs, "evaluation": evaluation, "refined": True}
        else:
            logger.info("Questions passed evaluation. No refinement needed.")
            return {"final_questions": questions_json, "evaluation": evaluation, "refined": False}
            
    except Exception as e:
        logger.error(f"Error during evaluation/refinement: {e}")
        return {"final_questions": questions_json, "error_in_eval": str(e), "refined": False}
