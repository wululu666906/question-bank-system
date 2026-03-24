import re
import logging

logger = logging.getLogger(__name__)

def extract_relevant_chunks(text: str, query: str, max_chars: int = 4000) -> str:
    """
    Extract the most relevant chunks of text based on keyword overlap with the query.
    Splits text into paragraphs, scores them based on query terms, and returns top chunks.
    """
    logger.info(f"Extracting relevant chunks for query: '{query}'")
    if not text:
        return ""
        
    # Split text roughly by sentence delimiters
    sentences = re.split(r'([。！？.!?\n])', text)
    
    # Reconstruct sentences with their punctuation
    chunks = []
    current_chunk = ""
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i] + sentences[i+1]
        if len(current_chunk) + len(sentence) > 300: # chunk size roughly 300 chars
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence
    if current_chunk:
        chunks.append(current_chunk)
        
    # Fallback if no punctuation
    if not chunks:
        chunks = [text[i:i+300] for i in range(0, len(text), 300)]
        
    # Generate bigrams from the query to simulate keyword matching for Chinese
    keywords = set()
    cleaned_query = re.sub(r'[^\w\u4e00-\u9fa5]', '', query)
    for i in range(len(cleaned_query)):
        # Bi-grams
        if i < len(cleaned_query) - 1:
            keywords.add(cleaned_query[i:i+2])
        # Individual characters
        keywords.add(cleaned_query[i])
        
    if not keywords:
        keywords = set(query.lower().split())

    # Score chunks
    scored_chunks = []
    for idx, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        score = sum(1 for kw in keywords if kw in chunk_lower)
        # Slight penalty for chunks too far down the page (idx) to prefer intro text
        weight = 1.0 - (idx / max(len(chunks), 1)) * 0.2
        final_score = score * weight
        scored_chunks.append((final_score, idx, chunk))
        
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Select top chunks until max_chars is reached
    selected_text = ""
    for score, idx, chunk in scored_chunks:
        if len(selected_text) + len(chunk) <= max_chars:
            selected_text += chunk + "\n"
        else:
            break
            
    logger.info(f"Extracted {len(selected_text)} characters from {len(text)} original characters.")
    return selected_text.strip()
