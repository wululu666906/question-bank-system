# Dify Workflow Design V2: Reasoning-Expert Synthesis

This document outlines a new architecture for the "Question Factory" that replaces external search and crawling nodes with a multi-agent reasoning flow. This approach leverages high-parameter reasoning models (e.g., DeepSeek-R1) to synthesize internal knowledge, providing a more stable and focused generation experience.

## 1. Design Philosophy: "Synthetic Wisdom"
Instead of retrieving noise from the web (which often contains irrelevant data), we utilize a **Reasoning Expert Agent** to synthesize a "Virtual Reference Dossier". 
- **Consistency**: No network failures or anti-crawl issues.
- **Depth**: Reasoning models can connect disparate concepts more deeply than a simple scraper.
- **Relevance**: 100% focused on the user's specific topic and profession.

## 2. Architecture Diagram (Conceptual)
`Start` -> `[Knowledge Specialist (R1)]` -> `[Business Architect (V3)]` -> `[Task Splitter]` -> `[JSON Parser]` -> `[Iteration Loop (Parallel Generation)]` -> `[End]`

## 3. Detailed Node Specifications

### Node A: Knowledge Specialist (Model: DeepSeek-R1)
- **Role**: Senior Research Fellow.
- **Task**: Generate a highly detailed (2500+ word) "Subject Dossier".
- **Prompt Logic**: 
  - Trace the logic of the `topic` from fundamentals to edge cases.
  - Formulate "Hidden Knowledge" that isn't easily found in basic textbooks but exists in professional practice.
  - Output format: Structured MarkDown Dossier.

### Node B: Business Architect (Model: DeepSeek-V3)
- **Role**: Industry Veteran.
- **Input**: Dossier from Node A.
- **Task**: Transform the abstract knowledge into **10+ Professional Scenarios**.
- **Constraint**: Scenarios must be 100% relevant to the `profession` variable.

### Node C: Task Splitter & Parser (Code + LLM)
- **Splitting**: Convert Scenarios into a valid JSON array of `N` items (where `N` = `question_count`).
- **Parsing**: A Python bit to ensure Dify sees an `Array`, not a `String`.

### Node D: Parallel Generator (Iteration)
- **Inner Node (V3)**: Focused on 1 item + relevant context from Node A. 
- **Prompt**: Optimized for zero-waste, high-precision question generation with deep analysis.

## 4. Why this Surpasses Version 1 (Search-Based)
1. **Zero Latency/Failure**: No waiting for Google or Firecrawl timeouts.
2. **Infinite Detail**: Reasoning models don't "copy" text; they "synthesize" it, allowing for endless customization of the background material.
3. **Structured Control**: By separating "Knowledge Base" (Dossier) from "Scenario Design", the resulting questions are significantly more professional and diverse.
