# 🧠 Agentic Workflow — ASCII to PowerPoint Automation

## 📘 Overview
This project demonstrates an **agentic AI workflow** that mimics human-like reasoning and execution.  
The agent receives a natural-language instruction:

> “Find ASCII values of characters in **AMERICA**, calculate sum of exponentials, and add result to `input.pptx`.”

It then breaks this into distinct **cognitive layers** — perception, decision, memory, and action — before performing the task end-to-end.

---

## 🧩 Architecture

| Layer | File | Description |
|-------|------|-------------|
| 🧠 **Perception** | `perception.py` | Uses an LLM (e.g., Gemini) to extract key **facts or intentions** from the user query. Example output: “Calculate sum of exponentials”, “Add result to PowerPoint.” |
| 💾 **Memory** | `memory.py` | Stores the agent’s **preferences and persistent context** — like favorite colors, fonts, or formatting preferences for PowerPoint slides. |
| ⚖️ **Decision** | `decision.py` | Acts as the **reasoning layer**, interpreting perceived facts and deciding which functions or tools to invoke next. Prevents unnecessary recursion and ensures ordered execution. |
| ⚙️ **Action** | `action.py` | Executes real **tools and APIs**, such as calculating mathematical expressions or editing PowerPoint files. |
| 🚀 **Main** | `main.py` | The orchestrator. Initializes all components, passes data between layers, and executes the full loop (Perceive → Decide → Act). |

---

## 🔁 Flow of Execution
User Query → Perception → Decision → Action → Output File
↘
Memory (Preferences)


### Example Flow
1. **User Query**: “Find ASCII values of characters in AMERICA, calculate sum of exponentials, and add result to input.pptx.”
2. **Perception**: Extracts:
   - “Find ASCII values”
   - “Calculate sum of exponentials”
   - “Add result to PowerPoint”
3. **Decision**: Determines correct tool sequence:
   - Call `get_ascii_values("AMERICA")`
   - Pass results to `calculate_exponential_sum()`
   - Use `add_rectangle_to_ppt()` to insert result into `input.pptx`
4. **Action**: Executes tools and saves `output.pptx`
5. **Main**: Logs steps and ensures graceful termination after task completion.

---


**Generated PowerPoint:**
A new slide (or rectangle) containing the computed exponential sum appears in `output.pptx`.

---

## 🧠 Agentic Design Principles

| Cognitive Layer | Description |
|------------------|-------------|
| **Perception** | Converts unstructured input into structured understanding. |
| **Memory** | Supplies contextual preferences (“I like blue fonts in PowerPoint”). |
| **Decision** | Chooses the next logical step based on perceived facts and memory. |
| **Action** | Executes the real-world tasks through functions or APIs. |

This modular setup makes it easy to **extend** — for example, adding a *verification layer* or a *feedback loop*.

---

## 🧰 Tools & Dependencies

- `google-generativeai` — Gemini API integration  
- `python-pptx` — PowerPoint manipulation  
- `pydantic` — Structured data validation  
- `dotenv` — Environment variable management  
- `re`, `math`, `os`, `logging` — Standard Python libraries  
- `uv` — Lightweight virtual environment manager  

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/nzalpha/ascii-agent.git
   cd ascii-agent

2. **Create and activate a virtual environment** 
uv venv
source .venv/bin/activate

3. **Install dependencies**
uv pip install -r requirements.txt

4. **Add your Gemini API key to a .env file**
GEMINI_API_KEY=your_api_key_here

5. **Run the main file**
uv run main.py

6. **Check output**
Logs will appear in the terminal
Updated PowerPoint file saved as output.pptx
