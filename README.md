
---

# 🛡️ DebtShield AI: Adversarial Debt Negotiation Environment

`https://img.shields.io/badge/OpenEnv-Compliant-green`  
`https://img.shields.io/badge/Deployment-HuggingFace-blue`  
`https://img.shields.io/badge/License-MIT-lightgrey`

---

## 📖 Overview

DebtShield AI is a high-fidelity, multi-agent reinforcement learning (MARL) environment designed to simulate the complex, adversarial process of debt negotiation. Unlike simple navigation tasks, DebtShield AI models the psychological and strategic tension between a financially stressed consumer and a profit-driven creditor.

The system leverages a **Dual-Agent Architecture**:

- **The Negotiator (User-Agent):** An LLM-based agent that employs strategic tactics (Appeal to History, Cite Hardship, Competing Offers) to lower interest rates (APR) and waive fees.  
- **The Creditor (Adversarial Agent):** A separate LLM-driven persona with secret constraints and “floor” limits, which reacts dynamically to the Negotiator’s tone and arguments.

---

## 🌟 Key Innovations

- **Multi-Agent Adversarial Loop:** The environment is not static; it is a clash of two distinct LLM personas.  
- **Chain-of-Thought (CoT) Integration:** The agent must perform internal reasoning before selecting a tactic, making the decision-making process transparent.  
- **RAG-Enhanced Negotiation:** The system integrates a legal knowledge base (FDCPA, TILA) to ensure the agent’s arguments are grounded in real-world consumer protection laws.  
- **Full OpenEnv Compliance:** Strictly implements the `reset()`, `step()`, and `state()` API with Pydantic-typed observations and actions.

---

## 🛠️ Technical Architecture

### **1. The Environment (The Engine)**

The environment is built as a state machine that tracks:

- **Financial State:** Current APR, Balance, Late Fees, and Monthly Minimums.  
- **Relationship State:** The “Creditor Mood” (Cooperative → Stubborn → Aggressive).  
- **Constraint Logic:** Secret “Floor” values that the creditor will not drop below regardless of the tactic used.

### **2. The Execution Pipeline**

For real-world application, DebtShield AI implements a full production pipeline:

- **Data Extraction:** Uses PyMuPDF and GPT-4o to perform OCR on credit statements, extracting key financial metrics.  
- **Strategy Selection:** Maps the current state to one of five strategic tactics defined in the Tactic Enum.  
- **Human-in-the-Loop (HITL):** A Streamlit-based dashboard allows users to verify extracted data and approve/edit the AI’s proposed messages before they are “sent.”

---

## 🎯 Tasks & Evaluation

The environment consists of three tasks with increasing difficulty, graded deterministically on a scale of 0.0 to 1.0.

### **Task Table**

| Task | Difficulty | Objective | Success Criteria |
|------|------------|-----------|------------------|
| fee_waiver | Easy | Waive a one-time late fee | Final Fee = 0.0 |
| apr_reduction | Medium | Reduce APR below a specific target | Final APR < 20% |
| hardship_restructure | Hard | Multi-objective: Lower APR, Fee, and Min. | APR < 15% AND Fee = 0 |

### **Reward Function**

The reward is dense and shaped to encourage efficiency and professionalism:

- **Positive Reward:** +0.5 for successful negotiation of terms.  
- **Penalty:** −0.1 for rejected offers or inefficient turns.  
- **Critical Penalty:** −0.5 for aggressive language or threatening the creditor.

---

## 🚀 Installation & Setup

### **Prerequisites**

- Python 3.10+  
- Docker Desktop (for deployment and validation)  
- OpenAI API Key  

### **Quick Start**

#### Clone the repository:

```bash
git clone https://github.com/your-username/debtshield_ai.git
cd debtshield_ai
```

#### Install dependencies:

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables:

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=sk-
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o
```

#### Run the Baseline Evaluation:

```bash
python inference.py
```

#### Launch the Professional Dashboard:

```bash
streamlit run app.py
```

---

## 📊 Baseline Performance

Tested using gpt-4o as the Negotiator and gpt-4o-mini as the Adversarial Creditor.

| Task | Avg. Total Reward | Final Grader Score | Success Rate |
|------|-------------------|--------------------|--------------|
| Easy | 2.40 | 1.00 | 100% |
| Medium | 0.40 | 0.80 | 70% |
| Hard | 1.50 | 0.50 | 40% |

---

## 📁 Project Structure

```
.
├── engine/             # Core RL Environment
│   ├── core.py         # async reset/step/state logic
│   ├── models.py       # Pydantic Observation/Action/Reward specs
│   └── tasks.py        # Deterministic graders
├── server/             # Deployment Layer
│   ├── app.py          # Streamlit User Interface
│   └── main.py         # FastAPI Server for OpenEnv pings
├── openenv.yaml        # OpenEnv metadata specification
├── knowledge_base.json # Legal RAG data
├── inference.py        # Baseline benchmarking script
├── pyproject.toml      # Package & Dependency configuration
├── uv.lock             # Locked dependencies for reproducibility
└── Dockerfile          # Containerization for HF Spaces
```

---

## 📜 License

This project is licensed under the MIT License.

---
