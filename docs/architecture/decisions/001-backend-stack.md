# ADR-001: Backend Technology Stack Selection

## Status
Proposed

## Context
The project "Secure Personal Agentic Platform" (MyAgent) requires a backend to handle:
1.  **LLM Orchestration**: Interfacing with Ollama, Anthropic, etc.
2.  **Tool Execution**: Running local functions (skills) safely.
3.  **Memory Management**: Vector embeddings and retrieval.
4.  **API Serving**: REST/WebSockets for the frontend.

The user questioned whether Python and FastAPI are the right choice, potentially implying interest in Node.js (used in their "other systems") or compiled languages like Go/Rust.

## Analysis

### Option 1: Python + FastAPI (Current)
**Pros:**
*   **Native AI Ecosystem**: PyTorch, HuggingFace, LangChain, LlamaIndex, and vector DB clients are native to Python.
*   **Tooling Synergy**: The requirement "Enable Ollama to invoke local Python functions" is trivial if the host is also Python.
*   **Data Science**: If the agent needs to analyze CSVs, plot graphs, or process audio, Python's libraries (Pandas, Numpy, Librosa) are unmatched.
*   **FastAPI**: Provides async concurrency (handling multiple requests) and automatic OpenAPI documentation.

**Cons:**
*   **Performance**: Slower raw CPU execution than Go/Rust.
*   **Deployment**: Heavier Docker images and dependency management (venv/poetry) can be fragile compared to compiled binaries.

### Option 2: Node.js / TypeScript
**Pros:**
*   **Tech stack consistency**: Shares language with the Next.js frontend.
*   **IO Performance**: Excellent for "glue code" agents that mostly just call other APIs.

**Cons:**
*   **AI Friction**: While JS AI libraries exist (LangChain.js), they often lag behind Python versions.
*   **Data Tooling**: Performing data analysis or running complex local algorithms is significantly harder/slower than in Python.
*   **Context Switching**: Invoking a "local python skill" requires spawning reliable child processes, handling serialization/deserialization, and error handling across process boundaries.

### Option 3: Go / Rust
**Pros:**
*   **Performance**: Single binary, instant startup, low memory footprint.
*   **Concurrency**: Best in class.

**Cons:**
*   **Development Velocity**: significantly slower for "neuro-supportive" rapid prototyping.
*   **Ecosystem**: AI libraries are immature. You end up writing a wrapper around a Python sidecar anyway.

## Decision
**We will stick with Python and FastAPI.**

**Rationale:**
For an "Agentic Platform" intended to have *local capabilities* (skills, memory, data processing), Python is the industry standard. The friction of "fighting the ecosystem" in Node.js or Go outweighs the performance benefits for a *personal* agent.

If the agent was purely a high-throughput router for thousands of users, Go would be better. But for a personal agent that needs to *think* and *do* (execute code), Python is superior.

## Consequences
*   We must implement robust Python tooling (Ruff, Mypy, Pytest) to maintain code quality (as addressed in the Tooling Review).
*   We accept the trade-off of slightly slower raw execution for vastly superior AI capability.
