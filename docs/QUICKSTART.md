# Quick Start Guide

## 1. Installation

### Clone the Repository
```bash
cd /path/to/project
git clone <repository-url>
cd AIDebator
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Other providers as needed
```

Or export as environment variables:
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## 2. Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 3. Configuring a Debate

### Step 1: Enter Topic
In the sidebar, enter your debate topic:
- "Artificial Intelligence will have a net positive impact on employment"
- "Remote work improves employee productivity"
- "Climate change requires immediate government action"

### Step 2: Select Models
Choose an LLM for each participant:

**Recommended Combinations:**
```
Organizer:  gpt-4
Supporter:  claude-3-opus-20240229
Opposer:    ollama/llama2
Judge:      gpt-4
```

**Budget-Friendly:**
```
Organizer:  gpt-3.5-turbo
Supporter:  gpt-3.5-turbo
Opposer:    gpt-3.5-turbo
Judge:      gpt-3.5-turbo
```

**Local-Only (Requires Ollama running):**
```
Organizer:  ollama/llama2
Supporter:  ollama/mistral
Opposer:    ollama/neural-chat
Judge:      ollama/llama2
```

### Step 3: Set Participant Names
Customize names for immersion:
- Organizer: "Moderator", "Dr. Smith", etc.
- Supporter: "Dr. Alice", "Pro-AI Advocate", etc.
- Opposer: "Prof. Bob", "Skeptical Reviewer", etc.
- Judge: "Judge Panel", "Evaluation Committee", etc.

### Step 4: Choose Number of Rounds
- Minimum: 1 (quick debate)
- Recommended: 3-5 (balanced)
- Maximum: 10 (comprehensive debate)

### Step 5: Start Debate
Click the **"🎬 Start Debate"** button

## 4. Interpreting Results

### Winner Announcement
Shows the debater with the highest overall score out of 10.

### Argument History
Each round displays:
- **Participant name and round number**
- **Word count** of the argument
- **Full argument text**
- **Identified gaps** (in opponent's previous arguments)

### Judge's Evaluation
For each debater, see:
- **Argument Quality** (0-10): How clear and persuasive
- **Evidence Quality** (0-10): Quality of citations and facts
- **Logical Consistency** (0-10): Consistency across arguments
- **Responsiveness** (0-10): Addressing opponent's points
- **Overall Score** (0-10): Composite evaluation
- **Detailed Feedback**: Judge's commentary

## 5. Downloading Results

After debate completes, download in:

### JSON Format
- Contains all arguments and scores
- Structured data
- Perfect for analysis or further processing

### CSV Format
- Tabular format
- Easy to open in Excel
- Good for record-keeping

## 6. Core Engine Usage (Python)

Use `topic_debate.py` directly in your own Python code:

```python
from topic_debate import (
    Organizer, Debater, Judge, DebateSession
)

# Create participants
organizer = Organizer("Moderator", "gpt-4")
supporter = Debater("Alice", "gpt-4", is_supporter=True)
opposer = Debater("Bob", "claude-3-opus-20240229", is_supporter=False)
judge = Judge("Judge", "gpt-4")

# Create session
debate = DebateSession(
    topic="AI will improve employment",
    organizer=organizer,
    supporter=supporter,
    opposer=opposer,
    judge=judge
)

# Run debate
result = debate.run(num_rounds=3)

# Access results
print(f"Winner: {result.winner}")
print(f"Score: {[s.overall_score for s in result.scores]}")

# Save to file
result.save("debate_result.json")

# Access specific arguments
supporter_args = debate.get_arguments_by_participant("Alice")
round_1_args = debate.get_round_arguments(1)
```

## 7. Model Selection Guide

### For Best Quality Debates
Use newer, more capable models:
```
gpt-4 / claude-3-opus / gemini-pro
```

### For Budget-Conscious Debates
Use efficient models:
```
gpt-3.5-turbo / claude-3-haiku
```

### For Local/Private Debates
Use Ollama models (requires Ollama running):
```
ollama/llama2 / ollama/mistral / ollama/neural-chat
```

### For Variety
Mix models for different perspectives:
```
Supporter: gpt-4 (strong reasoning)
Opposer: claude-3-sonnet (creative thinking)
Judge: gpt-4 (fair evaluation)
```

## 8. Example Debates

### Topic 1: Technology in Education
```
Topic: "Online learning is superior to traditional classroom education"
Organizer: gpt-4
Supporter: claude-3-opus-20240229 (pro-online)
Opposer: ollama/llama2 (pro-traditional)
Judge: gpt-4
Rounds: 3
```

### Topic 2: Remote Work
```
Topic: "Remote work should become the default for knowledge workers"
Organizer: gpt-3.5-turbo (budget option)
Supporter: gpt-3.5-turbo
Opposer: gpt-3.5-turbo
Judge: gpt-3.5-turbo
Rounds: 5
```

### Topic 3: AI Rights
```
Topic: "Advanced AI systems should have legal rights similar to humans"
Organizer: gpt-4
Supporter: claude-3-opus-20240229 (futuristic)
Opposer: gpt-4 (conservative)
Judge: claude-3-opus-20240229
Rounds: 4
```

## 9. Troubleshooting

### "Error: API key not configured"
**Solution**: Set environment variables before running
```bash
export OPENAI_API_KEY=your_key_here
streamlit run app.py
```

### "Error: Model not found"
**Solution**: Check spelling and availability
- Verify model name in litellm documentation
- For Ollama: ensure service is running (`ollama serve`)

### "Slow responses"
**Solution**: Use faster models
- Switch from gpt-4 to gpt-3.5-turbo
- Try local ollama models
- Check internet connection

### "Arguments are repetitive"
**Solution**: This shouldn't happen as history is enforced. If it does:
- Try a different model (some are better at reasoning)
- Increase number of rounds for more context
- Check model's context window limit

### "Judge unable to evaluate"
**Solution**: Judge model may not support JSON output
- Try a different model for judge (gpt-4 is most reliable)
- Check model documentation

## 10. Advanced Usage

### Custom Debate Flow
Extend DebateSession:
```python
class CustomDebate(DebateSession):
    def run(self, num_rounds):
        # Custom logic here
        return super().run(num_rounds)
```

### Custom Participant
Create new participant type:
```python
class Commentator(Participant):
    def get_role(self):
        return "commentator"

    def provide_commentary(self, arguments):
        # Custom implementation
        pass
```

### Batch Debates
Run multiple debates:
```python
topics = [
    "Topic 1",
    "Topic 2",
    "Topic 3"
]

results = []
for topic in topics:
    debate = DebateSession(topic, ...)
    result = debate.run(num_rounds=3)
    result.save(f"debate_{len(results)}.json")
    results.append(result)
```

## 11. Tips for Better Debates

1. **Clear Topic**: Make topic specific and debatable
   - ✅ "Remote work improves employee productivity"
   - ❌ "Work is important"

2. **Model Variety**: Use different models for different perspectives
   - GPT-4: Strong reasoning
   - Claude: Nuanced thinking
   - Llama: Creative interpretations

3. **Adequate Rounds**: 3-5 rounds usually sufficient
   - 1 round: Quick opinion
   - 3 rounds: Good depth
   - 5+ rounds: Comprehensive analysis

4. **Quality Judge**: Use capable model for judge
   - gpt-4 recommended
   - claude-3-opus backup
   - Avoid smaller models for scoring

5. **Save Results**: Always download JSON for records
   - Track debate outcomes
   - Build debate corpus
   - Analyze trends

## 12. File Structure

```
AIDebator/
├── app.py                 # Main Streamlit app
├── topic_debate.py        # Core debate engine
├── sl_debate.py          # Legacy combined version
├── requirements.txt      # Python dependencies
├── README.md             # Project overview
├── ARCHITECTURE.md       # Technical documentation
├── QUICKSTART.md         # This file
└── .env                  # Your API keys (create this)
```

## Next Steps

1. Set up your environment variables
2. Run `streamlit run app.py`
3. Create your first debate
4. Download and review the results
5. Experiment with different topics and models
6. Build custom workflows using the core engine

Enjoy your debates! 🎭
