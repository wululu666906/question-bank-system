import argparse
import logging
import json
import os
from dotenv import load_dotenv

from search_module import search_web
from crawler_module import fetch_and_clean_url
from extractor_module import extract_relevant_chunks
from llm_generator import generate_questions_initial, evaluate_and_refine

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(topic: str, output_file: str):
    logger.info(f"Starting question generation pipeline for topic: '{topic}'")
    
    # Step 1: Search the web
    search_results = search_web(topic, max_results=3)
    if not search_results:
        logger.error("No search results found. Exiting.")
        return

    # Step 2: Crawl content from URLs
    combined_raw_text = ""
    for idx, result in enumerate(search_results):
        url = result.get('href')
        if not url:
            continue
        logger.info(f"Processing URL {idx+1}/{len(search_results)}: {url}")
        content = fetch_and_clean_url(url)
        if content:
            combined_raw_text += f"\n--- 来源 {idx+1}: {url} ---\n{content}\n"

    if not combined_raw_text.strip():
        logger.error("Failed to extract any text from the search results. Exiting.")
        return

    # Step 3: Extract the most relevant chunks
    logger.info("Extracting the most relevant information from the crawled text...")
    relevant_context = extract_relevant_chunks(combined_raw_text, topic, max_chars=4000)
    
    logger.info(f"Context prepared (length: {len(relevant_context)} chars).")
    if not relevant_context:
        logger.warning("No relevant context could be extracted from the texts.")

    # Step 4: Initial LLM Question Generation
    logger.info("Calling LLM to generate initial questions...")
    initial_questions = generate_questions_initial(context=relevant_context, topic=topic)
    
    if "error" in initial_questions:
        logger.error(f"Failed to generate questions: {initial_questions.get('error')}")
        logger.debug(f"Raw Output: {initial_questions.get('raw_output')}")
        return

    # Step 5: Evaluate and Iteratively Refine (Self-Reflection)
    logger.info("Evaluating and refining generated questions...")
    final_result = evaluate_and_refine(initial_questions, context=relevant_context, topic=topic)
    
    final_questions = final_result.get("final_questions", {})
    evaluation = final_result.get("evaluation", {})
    was_refined = final_result.get("refined", False)

    # Output results
    logger.info("Pipeline completed successfully.")
    print("\n" + "="*50)
    print(f"主题: {topic}")
    print(f"题目已生成! 最终评价得分: {evaluation.get('score', 'N/A')}/100")
    if was_refined:
        print("注意: 本次生成经历了一趟自我评估后的提示词(Prompt)增强和重新生成，质量得到提升。")
        print(f"自我反思改进前反馈: {evaluation.get('feedback', '')}")
    else:
        print("题目的初始生成质量优异，未触发自动重写。")
    print("="*50 + "\n")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_questions, f, ensure_ascii=False, indent=2)
        logger.info(f"Final questions saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save output to {output_file}: {e}")
        # Print to console as fallback
        print(json.dumps(final_questions, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Question Generator Agent Pipeline")
    parser.add_argument("--topic", type=str, required=True, help="Topic to generate questions for")
    parser.add_argument("--output", type=str, default="questions_output.json", help="Path to save the generated JSON questions")
    
    args = parser.parse_args()
    main(args.topic, args.output)
