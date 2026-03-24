# Dify Workflow Design V3: Extreme Quality & Performance

This design focuses on the four pillars requested: **Quality (Expert Grade)**, **Speed (Low Latency)**, **Stability (Robust Schema)**, and **Uniqueness (Anti-Repetition)**.

## 1. Core Architecture: "Dimension-Scenario-Question" (DSQ)

To achieve high speed and zero repetition, we move away from a single "Knowledge Blueprint" and instead use a **Topic Decomposition** strategy.

### Level 1: Topic Decomposition (Node: Topic Specialist - V3)
- **Goal**: Split the `topic` into exactly `question_count` distinct **Dimensions**.
- **Logic**: If the topic is "Quantum Computing" and count is 3, it generates:
  1. Dimension: Superposition (Focus: Mathematical Proof)
  2. Dimension: Decoherence (Focus: Hardware Challenges)
  3. Dimension: Shor's Algorithm (Focus: Cryptographic Impact)
- **Benefit**: Ensures each question focuses on a different sub-topic (No Repetition).

### Level 2: Scenario Mapping (Node: Scenario Architect - V3)
- **Goal**: For each Dimension, create a specific professional scenario.
- **Benefit**: Speed. V3 can generate this list in < 3 seconds.

### Level 3: Parallel Generation (Iteration Node)
- **Goal**: Generate the actual questions.
- **Strategy**: Each iteration receives:
  - 1 Dimension + 1 Scenario.
  - Global Strict Rules.
- **Benefit**: Parallelism ensures the total time doesn't increase with the number of questions.

---

## 2. Performance & Quality Optimization

### A. Model Tiering (The Speed Secret)
- **Blueprint/Splitter**: Use **DeepSeek-V3**. It is nearly instantaneous and highly capable at structured planning.
- **Question Generation**:
  - For `Difficulty = Easy/Medium`: Use **DeepSeek-V3** (Fast).
  - For `Difficulty = Hard/Expert`: Use **DeepSeek-R1** (Deep Reasoning) for the first node (Knowledge) and V3 for the rest, OR use R1 for the final generation to ensure "Interference points" are logically sound.

### B. Anti-Repetition Mechanism
The **Topic Specialist** node is instructed to perform "Mutual Exclusion". It generates a JSON where each item has a `UUID` and a `unique_concept_lock`. The generator node must strictly adhere to this "Lock".

### C. Stability (JSON-First)
- Every node except the final generator outputs strictly formatted JSON.
- A "Validation Code Node" sits after the Splitter to prune any malformed tasks before they enter the Iteration loop.

---

## 3. Node Specifications (Polished Chinese)

### Node 1: 知识维度拆解 (V3)
- **Prompt**: "你是一位教育学家。请将主题【{{topic}}】拆解为 {{count}} 个互不重叠的专业维度。每个维度必须包含：维度名称、核心考核点、以及一个与【{{profession}}】相关的独一无二的操作情境。确保这些维度覆盖该主题的不同深度。"

### Node 2: JSON安全网 (Code)
- **Logic**: Python script to validate the array and inject dynamic "Difficulty Constraints" based on the user's input.

### Node 3: 专业级并行命题 (Iteration -> LLM)
- **Prompt**: "你是一位命题组长。{{strict_rules}}\n\n考核维度：{{dimension}}\n业务情境：{{scenario}}\n难度级别：{{difficulty}}\n\n请生成 1 道极致专业的题目。解析部分必须采用‘剥洋葱法’：1. 核心逻辑，2. 选项陷阱分析，3. 知识延伸。确保输入输出均为专业中文。"

---

## 4. Expected Results
- **First Result**: < 10 seconds.
- **Quality**: Professional examiner level.
- **Redundancy**: 0%.
