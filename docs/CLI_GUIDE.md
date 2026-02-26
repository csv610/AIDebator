# Command-Line Interface Guide

## Overview

The `debate_cli.py` module provides a complete command-line interface for running debates **without Streamlit** or any other UI framework. Use this for:

- Automation and scripting
- Batch processing multiple debates
- Integration with other systems
- Headless/server deployments
- Simple testing and debugging

## Installation

```bash
pip install -r requirements.txt
# Note: Streamlit dependency can be removed if only using CLI
```

## Basic Usage

### Simplest Example

```bash
python debate_cli.py --topic "AI will improve employment"
```

This runs a 3-round debate with default models (gpt-4 for all participants).

### Specify Number of Rounds

```bash
python debate_cli.py --topic "Remote work is better" --rounds 5
```

### Use Different Models

```bash
python debate_cli.py \
  --topic "Climate change requires immediate action" \
  --organizer-model gpt-4 \
  --supporter-model claude-3-opus-20240229 \
  --opposer-model ollama/llama2 \
  --judge-model gpt-4 \
  --rounds 3
```

## Configuration Files

### Load from Configuration

```bash
python debate_cli.py --config debate_config.json
```

### Configuration File Format

```json
{
  "topic": "AI will have positive impact on employment",
  "organizer": {
    "name": "Moderator",
    "model": "gpt-4"
  },
  "supporter": {
    "name": "Dr. Alice",
    "model": "gpt-4"
  },
  "opposer": {
    "name": "Prof. Bob",
    "model": "claude-3-opus-20240229"
  },
  "judge": {
    "name": "Judge Panel",
    "model": "gpt-4"
  },
  "num_rounds": 3
}
```

### Save Configuration

```bash
python debate_cli.py \
  --topic "Your topic" \
  --organizer-model gpt-4 \
  --save-config my_debate.json
```

This saves the configuration without running the debate, so you can edit and reuse it.

## Output & Results

### Save Result to JSON

```bash
python debate_cli.py \
  --topic "AI will improve employment" \
  --save-result debate_result.json
```

### Quiet Mode (No Terminal Output)

```bash
python debate_cli.py \
  --topic "Your topic" \
  --save-result result.json \
  --quiet
```

Useful when redirecting output or running in pipelines.

### Combined Usage

```bash
python debate_cli.py \
  --config my_debate.json \
  --save-result result_$(date +%Y%m%d_%H%M%S).json \
  --quiet
```

## Examples

### Example 1: Quick Debate

```bash
python debate_cli.py --topic "Social media is harmful" --rounds 2
```

Output shows:
- Topic overview from organizer
- 2 rounds of debate
- Judge evaluation
- Final winner

### Example 2: Using Ollama (Local Models)

```bash
python debate_cli.py \
  --topic "Open source is better than proprietary software" \
  --organizer-model ollama/llama2 \
  --supporter-model ollama/mistral \
  --opposer-model ollama/neural-chat \
  --judge-model ollama/llama2 \
  --rounds 3
```

**Requires**: Ollama running (`ollama serve`)

### Example 3: Budget-Friendly Debate

```bash
python debate_cli.py \
  --topic "Universal basic income would help the economy" \
  --organizer-model gpt-3.5-turbo \
  --supporter-model gpt-3.5-turbo \
  --opposer-model gpt-3.5-turbo \
  --judge-model gpt-3.5-turbo \
  --rounds 4
```

### Example 4: Mixed Models

```bash
python debate_cli.py \
  --topic "Genetic engineering should be allowed" \
  --supporter-model gpt-4 \
  --opposer-model claude-3-opus-20240229 \
  --rounds 3
```

### Example 5: Batch Processing

```bash
# Create a script to run multiple debates
for topic in \
  "Cryptocurrency will replace traditional money" \
  "Space exploration is worth the investment" \
  "Artificial intelligence poses existential risk"
do
  python debate_cli.py \
    --topic "$topic" \
    --rounds 2 \
    --save-result "results/debate_$(echo $topic | sed 's/ /_/g').json" \
    --quiet
done
```

### Example 6: Load, Modify, and Run

```bash
# Create initial config
python debate_cli.py \
  --topic "My topic" \
  --organizer-model gpt-4 \
  --save-config base_config.json

# Edit base_config.json manually to customize

# Run debate with config
python debate_cli.py --config base_config.json --rounds 5
```

## Command Reference

### Required Arguments

One of these is required:
- `--config FILE`: Load configuration from JSON
- `--topic TEXT`: Debate topic

### Optional Arguments

**Models:**
- `--organizer-model MODEL`: Model for organizer (default: gpt-4)
- `--supporter-model MODEL`: Model for supporter (default: gpt-4)
- `--opposer-model MODEL`: Model for opposer (default: gpt-4)
- `--judge-model MODEL`: Model for judge (default: gpt-4)

**Debate:**
- `--rounds N`: Number of rounds 1-10 (default: 3)

**Configuration:**
- `--save-config FILE`: Save configuration to JSON
- `--config FILE`: Load configuration from JSON

**Output:**
- `--save-result FILE`: Save debate result to JSON
- `--quiet`: Don't display result in terminal
- `--example`: Show example configuration file

**Help:**
- `-h, --help`: Show help message

## Output Format

### Terminal Output

```
================================================================================
  STARTING DEBATE: AI will have positive impact on employment
================================================================================

Participants:
  🎤 Organizer: Moderator (gpt-4)
  ✓ Supporter: Debater A (gpt-4)
  ✗ Opposer: Debater B (claude-3-opus-20240229)
  🏛️  Judge: Judge (gpt-4)

Rounds: 3

[Running debate...]

────────────────────────────────────────────────────────────────────────────────
  Round 0: Topic Overview
────────────────────────────────────────────────────────────────────────────────

▶ Moderator (Round 0)
  Words: 245
  [Full argument text...]

────────────────────────────────────────────────────────────────────────────────
  Round 1
────────────────────────────────────────────────────────────────────────────────

▶ Debater A (Round 1)
  Words: 380
  [Full argument text...]

[More rounds...]

────────────────────────────────────────────────────────────────────────────────
  Judge's Evaluation
────────────────────────────────────────────────────────────────────────────────

📊 Debater A
  ────────────────────────────────────────────────────────────────────────────
  Argument Quality:       8.5/10
  Evidence Quality:       8.2/10
  Logical Consistency:    8.8/10
  Responsiveness to Gaps: 8.6/10
  ────────────────────────────────────────────────────────────────────────────
  OVERALL SCORE:          8.5/10

  Feedback:
    Strong arguments with good evidence. Addressed opponent's points well...

[Judge evaluation for other debater...]

================================================================================
Final Result
================================================================================

🏆 WINNER: Debater A
   Score: 8.5/10
```

### JSON Output

When saved with `--save-result`, creates a JSON file with:

```json
{
  "topic": "AI will improve employment",
  "arguments": [
    {
      "round_number": 0,
      "participant_name": "Moderator",
      "participant_role": "organizer",
      "content": "...",
      "timestamp": "2024-11-24T18:42:00",
      "word_count": 245,
      "gaps_identified": null
    },
    ...
  ],
  "scores": [
    {
      "debater_name": "Debater A",
      "argument_quality": 8.5,
      "evidence_quality": 8.2,
      "logical_consistency": 8.8,
      "responsiveness_to_gaps": 8.6,
      "overall_score": 8.5,
      "feedback": "..."
    },
    ...
  ],
  "winner": "Debater A",
  "timestamp": "2024-11-24T18:42:30",
  "num_rounds": 3,
  "participants": {
    "Moderator": "organizer",
    "Debater A": "supporter",
    "Debater B": "opposer",
    "Judge": "judge"
  }
}
```

## Advanced Usage

### Programmatic Usage (Python)

```python
import subprocess
import json

# Run debate from Python
result = subprocess.run([
    'python', 'debate_cli.py',
    '--topic', 'Your topic',
    '--save-result', 'result.json',
    '--quiet'
], capture_output=True, text=True)

# Load result
with open('result.json', 'r') as f:
    debate_result = json.load(f)

# Analyze
print(f"Winner: {debate_result['winner']}")
print(f"Rounds: {debate_result['num_rounds']}")
```

### Integration with Scheduling

Run debates on a schedule using cron (Linux/Mac):

```bash
# Run debate every day at 2 PM
0 14 * * * cd /path/to/AIDebator && python debate_cli.py --config daily_debate.json --save-result "results/debate_$(date +\%Y\%m\%d).json" --quiet
```

Or Windows Task Scheduler:
```batch
python C:\path\to\AIDebator\debate_cli.py --config daily_debate.json --save-result results\debate_%date:~10,4%%date:~4,2%%date:~7,2%.json --quiet
```

### Pipeline Integration

```bash
# Generate debates and process results
python debate_cli.py --topic "Topic 1" --save-result result1.json --quiet && \
python debate_cli.py --topic "Topic 2" --save-result result2.json --quiet && \
python process_results.py result1.json result2.json
```

## Error Handling

### Common Errors

**Error**: `API key not configured`
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
python debate_cli.py --topic "..."
```

**Error**: `Model not found`
- Check spelling of model name
- For Ollama: ensure service is running (`ollama serve`)
- Check model availability with your provider

**Error**: `Topic is required`
```bash
python debate_cli.py --config config.json  # Config must include topic
# OR
python debate_cli.py --topic "Your topic"
```

## Performance Tips

1. **Use faster models** for quick testing:
   ```bash
   python debate_cli.py --topic "..." \
     --organizer-model gpt-3.5-turbo \
     --supporter-model gpt-3.5-turbo \
     --opposer-model gpt-3.5-turbo \
     --judge-model gpt-3.5-turbo
   ```

2. **Use fewer rounds** for quick iteration:
   ```bash
   python debate_cli.py --topic "..." --rounds 1
   ```

3. **Use local models** (Ollama) to avoid API calls:
   ```bash
   python debate_cli.py --topic "..." \
     --organizer-model ollama/llama2 \
     --supporter-model ollama/llama2 \
     --opposer-model ollama/llama2 \
     --judge-model ollama/llama2
   ```

4. **Run in quiet mode** to skip terminal rendering:
   ```bash
   python debate_cli.py --topic "..." --quiet --save-result result.json
   ```

## Integration Examples

### With Web Framework

```python
# FastAPI example
from fastapi import FastAPI, BackgroundTasks
import subprocess

app = FastAPI()

@app.post("/debate")
async def run_debate(topic: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        subprocess.run, [
            'python', 'debate_cli.py',
            '--topic', topic,
            '--save-result', f'results/{topic}.json',
            '--quiet'
        ]
    )
    return {"status": "Debate queued"}
```

### With Database

```python
import sqlite3
import json
import subprocess

def save_debate_to_db(topic):
    # Run debate
    result = subprocess.run([
        'python', 'debate_cli.py',
        '--topic', topic,
        '--save-result', 'temp.json',
        '--quiet'
    ], capture_output=True)

    # Load result
    with open('temp.json', 'r') as f:
        debate_data = json.load(f)

    # Save to database
    conn = sqlite3.connect('debates.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO debates (topic, result, winner)
        VALUES (?, ?, ?)
    """, (topic, json.dumps(debate_data), debate_data['winner']))
    conn.commit()
```

## Troubleshooting

### Debate Takes Too Long

**Cause**: Using large models with many rounds
**Solution**:
```bash
python debate_cli.py --topic "..." --rounds 1 --judge-model gpt-3.5-turbo
```

### Out of Memory

**Cause**: Very long debates or large context windows
**Solution**: Use smaller models or fewer rounds

### Inconsistent Results

**Cause**: LLM randomness
**Solution**: This is expected. Run multiple debates and average results.

### JSON Parse Error

**Cause**: Judge model doesn't support JSON output
**Solution**: Use GPT-4 or Claude which reliably output JSON

## See Also

- `topic_debate.py`: Core debate engine
- `app.py`: Streamlit web interface
- `README.md`: Project overview
- `ARCHITECTURE.md`: Technical details

## License

Same as main project

---

**Created**: November 24, 2025
**Status**: Production Ready
**Version**: 1.0
