# Multi-Participant AI Debate Platform

A software platform for orchestrating debates between Large Language Models (LLMs). The system includes logic for argument validation, evidence-based scoring, and multi-round interactions. It supports various LLM providers through the **litellm** library.

## Architecture

### Visual Overview

```mermaid
graph TD
    %% Execution Flow
    Start(Start Debate) --> SessionRun[Session.run]
    SessionRun --> OrgRound[Organizer Round]
    OrgRound --> LoopStart{Round Loop}
    LoopStart --> IntermediateScores[Judge Intermediate Scoring]
    IntermediateScores --> DebaterTurn[Debater Turn]
    DebaterTurn --> Val{Quality Validation}
    Val -- Fail --> Terminate[Early Termination]
    Val -- Pass --> NextDebater[Opponent Turn]
    NextDebater --> LoopEnd{More Rounds?}
    LoopEnd -- Yes --> LoopStart
    LoopEnd -- No --> FinalJudge[Final Judge Evaluation]
    FinalJudge --> WinDet[Determine Winner]
    WinDet --> End(Generate DebateResult)
    Terminate --> FinalJudge
```

### Participant Roles

1. **Organizer**: Generates a neutral topic overview (200-300 words).
2. **Supporter**: Argues in favor of the topic.
3. **Opposer**: Argues against the topic.
4. **Judge**: Evaluates arguments based on defined metrics and provides a final score.

Participants can be configured with different LLM models.

## Why Debating Can Help LLMs?

Debating provides an adversarial environment to evaluate reasoning capabilities, identify subtle nuances, and detect differences in how models process information and construct arguments. It requires models to analyze, refute, and adapt to external logic.

### (1) Between Two Different Models
Debating between models from different providers (e.g., GPT-4 vs. Claude-3) allows for the identification of provider-specific biases and knowledge gaps. It serves as a cross-validation mechanism where the strengths of one architecture can be used to expose the logical inconsistencies or factual errors of another, highlighting subtle differences in their training and refinement.

### (2) Between the Same Models
Assigning different roles (Supporter vs. Opposer) to the same model facilitates internal consistency testing. This configuration requires the model to explore conflicting perspectives within its own training data, which can be used to evaluate its ability to follow complex personas and identify self-contradictions in its reasoning processes, revealing how it handles nuances within a single knowledge base.

### Debate Flow

- **Round 0**: Topic introduction by the Organizer.
- **Rounds 1-N**: Alternating arguments between Supporter and Opposer.
  - Models receive context including previous arguments from both sides.
  - Models are prompted to identify logical gaps and rebut opponent claims.
- **Evaluation**: The Judge scores the debate using the following criteria:
  - Argument Quality (0-10)
  - Evidence Quality (0-10)
  - Logical Consistency (0-10)
  - Responsiveness to Gaps (0-10)
  - Overall Score (0-10)

## Design Characteristics

The platform implements the following logic:

- **Validation Logic**: Automated checks to terminate debates if argument quality falls below a threshold or becomes repetitive.
- **Weighted Scoring**: Evidence quality is assigned a 40% weight in the final evaluation.
- **Dynamic Adjustments**: Scoring includes bonuses for acknowledging valid opponent points and penalties for unaddressed weaknesses.
- **Orchestration**: A core engine (`src/debate`) manages the state machine and participant interactions independently of the interface.

## Core Features

- **Automated Termination**: Ends the session if arguments lack novelty or fail to address the topic.
- **Evidence Weighting**: Prioritizes factual citations in the scoring rubric.
- **Strategy Adaptation**: Debaters receive intermediate scores to adjust their argumentation in subsequent rounds.
- **Multi-Model Integration**: Compatible with 20+ LLM providers via litellm.
- **Deployment Interfaces**: Includes a Streamlit web UI, a CLI, and a Python API.
- **Data Export**: Debate transcripts are available in JSON format with metadata.

## Setup

### Prerequisites

- Python 3.8+
- API keys for LLM providers (e.g., OpenAI, Anthropic, Google).
- [Ollama](https://ollama.ai/) for local model execution (optional).

### Installation

```bash
git clone https://github.com/csv610/AIDebator.git
cd AIDebator
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Usage

### Interfaces

**Web Interface**
```bash
streamlit run app.py
```

**Command Line**
```bash
python debate_cli.py --topic "Subject" --rounds 3
```

**Python API**
```python
from src.debate import DebateConfig, DebateSession

config = DebateConfig(
    topic="Topic",
    organizer_model="gpt-4",
    supporter_model="gpt-4",
    opposer_model="claude-3",
    judge_model="gpt-4",
    num_rounds=3
)

debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)
```

## Implementation Details & Limitations

### Implementation Features

- **Type Safety**: Uses Python type hints across the codebase.
- **Modular Design**: Separation of engine logic, data models, and participant behavior.
- **State Serialization**: Support for JSON-based configuration and result persistence.

### Constraints

- **LLM-Dependent Validation**: The accuracy of quality validation is tied to the performance of the judge model.
- **Synchronous Execution**: API calls are made sequentially, which impacts total execution time.
- **Context Window Limits**: Long debates may be constrained by the token limits of the selected models.
- **Fixed Roles**: The current version is designed for a four-participant structure (1 Organizer, 2 Debaters, 1 Judge).

## Project Analysis vs. Current Research

Based on the research cited in the References section, the platform's implementation aligns with several established findings while maintaining specific architectural gaps.

### Alignment with Research
- **Multi-Round Convergence**: Following *Du et al. (2024)*, the platform uses a multi-round debate structure to reduce hallucinations and improve reasoning through iterative critiquing.
- **Strategic Adaptation**: In line with *Zhu et al. (2025)*, the use of intermediate scoring allows for strategic pivots, enabling models to adapt their argumentation based on "milestone-based" feedback.
- **Novelty Enforcement**: The **Early Termination** logic addresses the "stall" effect noted in *Duckworth et al. (2024)*, where multi-agent debates often become repetitive after initial rounds.
- **Adversarial Persona Constraints**: By enforcing strict "Supporter" vs. "Opposer" roles, the system minimizes the "consensus bias" identified in *Wu et al. (2025)*.

### Current Gaps and Limitations
- **Fine-Grained Logic Validation**: Current evaluation is performed on the entire argument. Research by *Zhang & Xiong (2025)* suggests that step-wise (paragraph-by-paragraph) validation is more effective for complex reasoning.
- **Group Dynamics**: The platform is restricted to one agent per side. It cannot currently simulate "majority pressure" or "peer correction" within a team, as explored in *Wu et al. (2025)*.
- **Baseline Benchmarking**: The system lacks an automated "control group" comparison (e.g., comparing debate results vs. single-agent self-consistency) as recommended by *Duckworth et al. (2024)*.
- **Concurrency**: The orchestration is synchronous. To scale to the "larger societies" discussed in research, the architecture would require transition to an asynchronous execution model.

## Documentation

- **[Quick Start](docs/QUICKSTART.md)**
- **[Architecture](docs/ARCHITECTURE.md)**
- **[Scoring Methodology](docs/SCORING_GUIDE.md)**
- **[CLI Guide](docs/CLI_GUIDE.md)**
- **[File Index](docs/INDEX.md)**

## Data Models

- **DebateConfig**: Configuration parameters for the session.
- **Argument**: Metadata and content for individual turns.
- **Score**: Quantitative and qualitative evaluation data.
- **DebateTermination**: Records the reason and timing of session end.

## License

MIT License

## Citation

```
CSV610. (2025). AI Debate Platform: Multi-Participant AI Debate
with Quality Control and Evidence-Based Scoring.
https://github.com/csv610/AIDebator
```

## Reference Research Papers

### Foundational & Performance Research
- **Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2024).** *Improving Factuality and Reasoning in Language Models through Multiagent Debate.* Proceedings of the 41st International Conference on Machine Learning (ICML), PMLR 235. [arXiv:2305.14325](https://arxiv.org/abs/2305.14325)
- **Smit, A., Duckworth, P., Grinsztajn, N., Barrett, T. D., & Pretorius, A. (2024).** *Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs.* Proceedings of the 41st International Conference on Machine Learning (ICML), PMLR 235:45883-45905. [arXiv:2311.17371](https://arxiv.org/abs/2311.17371)

### Logic & Mathematical Reasoning
- **Wu, H., Li, Z., & Li, L. (2025).** *Can LLM agents really debate? A controlled study of multi-agent debate in logical reasoning.* arXiv preprint arXiv:2511.07784. [https://arxiv.org/abs/2511.07784](https://arxiv.org/abs/2511.07784)
- **Zhang, S., & Xiong, D. (2025).** *Debate4MATH: Multi-Agent Debate for Fine-Grained Reasoning in Math.* Findings of the Association for Computational Linguistics: ACL 2025, pages 16810–16824. [https://aclanthology.org/2025.findings-acl.862/](https://aclanthology.org/2025.findings-acl.862/)

### Benchmarks & System Evaluation
- **Zhu, K., Du, H., Hong, Z., Yang, X., Guo, S., Wang, Z., Wang, Z., Qian, C., Tang, R., Ji, H., & You, J. (2025).** *MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents.* Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 8580–8622. [https://aclanthology.org/2025.acl-long.421](https://aclanthology.org/2025.acl-long.421)

### Safety & Security
- **Lin, D., Shen, G., Yang, Z., Liu, T., Zhao, D., & Zeng, Y. (2025).** *Efficient LLM Safety Evaluation through Multi-Agent Debate.* arXiv preprint arXiv:2511.06396. [https://arxiv.org/abs/2511.06396](https://arxiv.org/abs/2511.06396)
