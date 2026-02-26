# Multi-Participant AI Debate Platform

An **advanced, production-ready AI debate platform** that orchestrates academic debates between AI models with built-in quality control and evidence-based scoring. Features automatic debate termination when argument quality drops, dynamic scoring that rewards substantive engagement, and multi-LLM support via **litellm** (20+ providers: OpenAI, Anthropic, Ollama, Google, etc.).

## Architecture

### Four Participants

1. **Organizer**: Provides a neutral 200-300 word overview of the topic without favoring any side
2. **Supporter**: Debater arguing in favor of the topic
3. **Opposer**: Debater arguing against the topic
4. **Judge**: Evaluates all arguments and provides detailed scoring

Each participant can use a **different LLM model** configured via litellm.

### Debate Flow

- **Round 0**: Organizer sets up the topic with neutral overview
- **Rounds 1-N**: Debaters alternate presenting arguments
  - Each debater receives the complete draft of the opponent's previous arguments
  - Debaters identify gaps, inconsistencies, logical fallacies, and unsupported claims
  - Rebuttals address specific weaknesses in opponent's arguments
- **Final Phase**: Judge evaluates all N arguments using a structured rubric:
  - Argument Quality (0-10)
  - Evidence Quality (0-10)
  - Logical Consistency (0-10)
  - Responsiveness to Gaps (0-10)
  - Overall Score (0-10)
  - Detailed Feedback

## Why This Matters

The AI Debate Platform addresses the need for **rigorous evaluation of AI reasoning and argumentation**:

- **Quality Assurance**: Automatic termination ensures debates don't degrade with low-quality arguments
- **Evidence-Based Evaluation**: 40% of scoring weight on evidence/citations incentivizes factual arguments
- **Fair Competition**: Dynamic scoring (+0.15 for acknowledged valid points, -0.10 for weaknesses) rewards objectivity
- **Flexibility**: Run without Streamlit (CLI), as reusable library (Python API), or via web interface
- **Production Ready**: 100% type hints, comprehensive error handling, full logging

Perfect for: **Academic research, AI model evaluation, educational demonstrations, argument analysis, debate corpus generation**

## Core Features

✅ **Quality Control**: Automatic debate termination when arguments lack novelty or fail to refute opponent
✅ **Evidence-Based Scoring**: 40% weight on evidence quality—facts and citations determine winners
✅ **Dynamic Scoring**: +0.15 bonus per acknowledged valid point, -0.10 penalty per identified weakness
✅ **Score Tracking**: Debaters adapt strategy based on intermediate scores between rounds
✅ **Multi-Model Support**: Use different LLM models for each participant via litellm (20+ providers)
✅ **Intelligent Analysis**: Gap detection, consistency checking, logical fallacy identification
✅ **Configuration System**: Structured DebateConfig with validation and JSON serialization
✅ **Three Deployment Options**: Streamlit UI, CLI interface, Python API
✅ **Complete Transcripts**: Download debates in JSON format with full metadata
✅ **Configurable Rounds**: Support 1-10 debate rounds

## Setup

### Prerequisites

- Python 3.8 or higher
- API keys for your chosen LLM providers (OpenAI, Claude, etc.)
- For local models: [Ollama](https://ollama.ai/) installed and running

### Install Dependencies

```bash
git clone https://github.com/csv610/AIDebator.git
cd AIDebator
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# Add other provider keys as needed
```

### Running the Platform

Choose your preferred interface:

**Option 1: Web UI (Streamlit)**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501` with graphical configuration

**Option 2: Command Line (No Streamlit required)**
```bash
python debate_cli.py --topic "AI will improve employment" --rounds 3
```
Simple text-based interface, great for automation

**Option 3: Python API (Reusable library)**
```python
from src.debate import DebateConfig, DebateSession

config = DebateConfig(
    topic="Your topic",
    organizer_model="gpt-4",
    supporter_model="gpt-4",
    opposer_model="claude-3-opus-20240229",
    judge_model="gpt-4",
    num_rounds=3
)

debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)
```

**Option 4: JSON Configuration File**
```bash
python debate_cli.py --config debate_config.json
```

## Usage

1. **Enter the Debate Topic**: Provide the academic topic for debate
2. **Select LLM Models**: Choose a model for each participant (examples: `gpt-4`, `claude-3-opus`, `ollama/llama2`)
3. **Set Number of Rounds**: Choose how many debate rounds (1-10)
4. **Start the Debate**: Click "Start Debate" to begin
5. **Review Results**: See scoring and detailed feedback from the judge
6. **Download Transcript**: Export the complete debate as JSON

## Model Configuration Examples

| Provider | Model Format | Example |
|----------|--------------|---------|
| OpenAI | `gpt-3.5-turbo`, `gpt-4` | `gpt-4` |
| Anthropic | `claude-3-opus`, `claude-3-sonnet` | `claude-3-opus-20240229` |
| Ollama | `ollama/<model_name>` | `ollama/llama2` |
| Google | `gemini-pro` | `gemini-pro` |

## Example Debate

**Topic**: "Artificial Intelligence will have a net positive impact on employment"

1. **Moderator** provides balanced overview of AI and employment
2. **Debater A (GPT-4)** argues AI creates more jobs than it displaces
3. **Debater B (Claude)** counters with concerns about job displacement
4. Rounds continue with gap analysis and rebuttals
5. **Judge (Llama)** evaluates both sides comprehensively
6. Winner determined by overall score

## Strengths & Limitations

### Strengths ✅

- **Production-Ready Code**: 100% type hints, comprehensive error handling, full logging
- **Modular Architecture**: Core engine works independently from UI—use CLI, API, or web interface
- **No UI Dependencies**: Core engine in `src.debate` has zero Streamlit dependencies
- **Flexible Deployment**: Web UI, CLI, Python API, or JSON configuration
- **Quality Control**: Automatic debate termination prevents low-quality continuation
- **Evidence-Based**: 40% scoring weight on evidence incentivizes factual arguments
- **Comprehensive Documentation**: Detailed guides covering all features and use cases
- **Multi-LLM Support**: Works with 20+ providers via litellm
- **Extensible**: Easy to add custom participants, scoring criteria, or analysis

### Limitations & Design Choices ⚠️

- **LLM-Based Validation**: Argument quality validation depends on judge model's capability
- **No Human Override**: System automatically terminates low-quality arguments (by design)
- **First Round Exemption**: Round 1 arguments bypass validation (to allow opening statements)
- **Single Judge**: One judge evaluates all arguments (can be extended to multiple judges)
- **No Real-Time Interaction**: Debates run to completion; no real-time user intervention
- **Model Dependency**: Quality heavily depends on selected LLM models' instruction-following
- **Cost**: Multiple LLM API calls = potential cost (depends on provider and model)
- **Context Windows**: Very long debates may exceed LLM context limits (depends on model)

### When to Use

✅ **Good for**:
- Academic research on AI argumentation
- Evaluating LLM reasoning capabilities
- Educational demonstrations of debate structure
- Generating debate corpora for training
- Testing different models' abilities
- Comparing argumentation quality

❌ **Not ideal for**:
- Real-time human-AI debates
- Debates requiring live human judging
- Systems requiring human intervention during execution
- Low-latency/real-time applications
- Training on confidential data (uses external APIs)

## Documentation

Complete documentation is available in the `docs/` folder:

- **[Quick Start](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Debate Termination](docs/DEBATE_TERMINATION.md)** - Quality control system
- **[DebateConfig](docs/DEBATE_CONFIG.md)** - Configuration management
- **[Scoring Guide](docs/SCORING_GUIDE.md)** - Detailed scoring methodology
- **[CLI Guide](docs/CLI_GUIDE.md)** - Command-line usage
- **[File Index](docs/INDEX.md)** - Navigation guide for all files

## Data Models

### DebateConfig
- `topic`: The debate topic (string)
- `organizer_model`: LLM model for organizer
- `supporter_model`: LLM model for supporter
- `opposer_model`: LLM model for opposer
- `judge_model`: LLM model for judge
- `num_rounds`: Number of debate rounds (1-10, default 3)

### Argument
- `round_number`: Which round (0 for organizer, 1+ for debate rounds)
- `participant_name`: Name of the speaker
- `participant_role`: "organizer", "supporter", "opposer"
- `content`: The actual argument text
- `timestamp`: When the argument was generated
- `word_count`: Number of words
- `gaps_identified`: Gaps and inconsistencies found in opponent's arguments
- `acknowledged_valid_points`: Valid points acknowledged from opponent (dynamic scoring)
- `identified_weaknesses`: Weaknesses identified in opponent (dynamic scoring)

### Score
- `debater_role`: Role of evaluated debater ("supporter" or "opposer")
- `argument_quality`: 0-10 rating
- `evidence_quality`: 0-10 rating (weighted 40% of overall score)
- `logical_consistency`: 0-10 rating
- `responsiveness_to_gaps`: 0-10 rating
- `overall_score`: 0-10 rating (before dynamic adjustments)
- `fact_count`: Number of citations/facts presented
- `irrefutable_arguments`: Count of evidence-backed arguments
- `feedback`: Detailed evaluation feedback

### DebateTermination
- `terminated`: Boolean - whether debate ended early
- `reason`: "completed" or "low_quality"
- `round_number`: Which round termination occurred
- `debater_name`: Which debater failed (if applicable)
- `message`: Specific reason for termination

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Areas for contribution:

- Additional participant types (mediator, audience representative, etc.)
- Custom scoring rubrics
- New LLM provider integrations
- Debate analysis tools
- Educational enhancements
- Performance optimizations

## Support & Questions

- 📖 **Documentation**: See `docs/` folder for comprehensive guides
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Discussions**: Start discussions for feature requests
- 📧 **Contact**: Reach out with questions

## Citation

If you use this platform in research, please cite:

```
CSV610. (2025). AI Debate Platform: Multi-Participant AI Debate
with Quality Control and Evidence-Based Scoring.
https://github.com/csv610/AIDebator
```

---

**Status**: ✅ Production Ready | **Version**: 1.0 | **Last Updated**: November 2025
