# AI Debate Platform - Architecture Documentation

## Overview

The AI Debate Platform is a modular, scalable system for orchestrating multi-participant academic debates between AI language models. The architecture separates concerns into:

1. **Core Engine** (`topic_debate.py`): Pure business logic
2. **User Interface** (`app.py`): Streamlit web interface
3. **Legacy Integration** (`sl_debate.py`): Original combined version

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                     │
│  - Configuration input                                        │
│  - Result visualization                                       │
│  - Download functionality                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Debate Engine (topic_debate.py)                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Participants (Abstract Base)                         │   │
│  │  - Participant (ABC)                                 │   │
│  │    ├── Organizer                                     │   │
│  │    ├── Debater                                       │   │
│  │    └── Judge                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Data Models                                          │   │
│  │  - Argument                                          │   │
│  │  - Score                                             │   │
│  │  - DebateResult                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Orchestration                                        │   │
│  │  - DebateSession (main controller)                   │   │
│  │    ├── run()                                         │   │
│  │    ├── _run_organizer_round()                        │   │
│  │    ├── _run_debate_round()                           │   │
│  │    ├── _run_judge_evaluation()                       │   │
│  │    └── _determine_winner()                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌────────────────────────────────┐
        │  litellm (LLM abstraction)      │
        │  Supports: OpenAI, Claude,      │
        │  Ollama, Google, etc.           │
        └────────────────────────────────┘
```

## Core Components

### 1. Participant Classes

#### Base Class: `Participant` (Abstract)

Located in `topic_debate.py:141-189`

**Responsibilities:**
- Define interface for all participants
- Handle LLM communication via litellm
- Word counting functionality

**Key Methods:**
- `generate_response(prompt, max_tokens)`: Call LLM with error handling
- `count_words(text)`: Utility method

**Features:**
- Flexible model selection via litellm
- Structured error handling with logging
- Temperature control (0.7 for consistency)

#### `Organizer` Class

Located in `topic_debate.py:195-227`

**Responsibilities:**
- Provide neutral topic overview
- Set context for debate

**Key Methods:**
- `generate_overview(topic)`: Generate 200-300 word neutral overview

**Constraints:**
- Must remain neutral
- Cannot favor any position
- Word count: 200-300 (enforced in prompt)

#### `Debater` Class

Located in `topic_debate.py:233-384`

**Responsibilities:**
- Generate arguments and rebuttals
- Track argument history (own and opponent's)
- Analyze opponent arguments for gaps
- Enforce new information per round

**Key Attributes:**
- `is_supporter`: Boolean flag for position
- `argument_history`: List of own arguments
- `opponent_argument_history`: List of opponent's arguments

**Key Methods:**
- `generate_argument(topic, round, is_initial)`: Generate argument with history context
- `add_own_argument(argument, round)`: Store own argument
- `add_opponent_argument(argument, round)`: Store opponent's argument
- `analyze_opponent_arguments(topic, arguments)`: Identify gaps in logic
- `_build_history_summary(history, label)`: Format history for prompts

**History Tracking:**
- Maintains complete argument history
- Provides history in prompts to prevent repetition
- Enables gap analysis between rounds

#### `Judge` Class

Located in `topic_debate.py:390-490`

**Responsibilities:**
- Evaluate all debate arguments
- Score on multiple criteria
- Provide detailed feedback

**Scoring Criteria:**
1. Argument Quality (0-10): Clarity, structure, persuasiveness
2. Evidence Quality (0-10): Use of facts and citations
3. Logical Consistency (0-10): Consistency and lack of contradictions
4. Responsiveness to Gaps (0-10): Addressing opponent's points
5. Overall Score (0-10): Composite score

**Key Methods:**
- `score_debate(topic, arguments)`: Score all debaters

### 2. Data Models

#### `Argument` Dataclass

Located in `topic_debate.py:63-82`

**Fields:**
```python
- round_number: int              # 0 for organizer, 1+ for debate
- participant_name: str          # Speaker's name
- participant_role: str          # "organizer", "supporter", "opposer"
- content: str                   # The actual argument text
- timestamp: str                 # ISO format timestamp
- word_count: int                # Word count of content
- gaps_identified: Optional[List[str]]  # Gaps found in opponent's arguments
```

**Methods:**
- `to_dict()`: Convert to dictionary for serialization
- `__str__()`: String representation

#### `Score` Dataclass

Located in `topic_debate.py:85-103`

**Fields:**
```python
- debater_name: str              # Who was scored
- argument_quality: float        # 0-10
- evidence_quality: float        # 0-10
- logical_consistency: float     # 0-10
- responsiveness_to_gaps: float  # 0-10
- overall_score: float           # 0-10
- feedback: str                  # Detailed evaluation
```

**Methods:**
- `to_dict()`: Convert to dictionary
- `__str__()`: String representation

#### `DebateResult` Dataclass

Located in `topic_debate.py:106-167`

**Fields:**
```python
- topic: str                     # Debate topic
- arguments: List[Argument]      # All arguments in order
- scores: List[Score]            # Judge scores
- winner: Optional[str]          # Winner name or None for tie
- timestamp: str                 # When debate completed
- num_rounds: int                # Number of rounds
- participants: Dict[str, str]   # {name: role} mapping
```

**Methods:**
- `to_dict()`: Convert to dictionary
- `to_json(indent)`: Convert to JSON string
- `save(filepath)`: Save to JSON file
- `load(filepath)`: Load from JSON file (static method)

### 3. DebateSession (Orchestrator)

Located in `topic_debate.py:496-679`

**Responsibilities:**
- Coordinate complete debate flow
- Manage participant interactions
- Generate final results

**Initialization:**
```python
session = DebateSession(
    topic="AI will improve employment",
    organizer=Organizer("Moderator", "gpt-4"),
    supporter=Debater("Alice", "gpt-4", is_supporter=True),
    opposer=Debater("Bob", "claude-3-opus-20240229", is_supporter=False),
    judge=Judge("Judge", "gpt-4")
)
```

**Main Method:**
- `run(num_rounds)`: Execute complete debate

**Private Methods:**
- `_run_organizer_round()`: Round 0 - organizer overview
- `_run_debate_round(round_num)`: Rounds 1-N - alternating debaters
- `_run_judge_evaluation()`: Final phase - scoring
- `_determine_winner(scores)`: Winner determination logic

**Utility Methods:**
- `get_arguments_by_participant(name)`: Filter by person
- `get_arguments_by_role(role)`: Filter by role
- `get_round_arguments(round_num)`: Filter by round

## Debate Flow

### Complete Execution Sequence

```
1. DebateSession.run(num_rounds)
   │
   ├─ _run_organizer_round()
   │  └─ Organizer.generate_overview()
   │     └─ Creates neutral 200-300 word overview
   │        └─ Argument stored (round_number=0)
   │
   ├─ for round_num in 1..num_rounds:
   │  └─ _run_debate_round(round_num)
   │     │
   │     ├─ if round_num == 1:
   │     │  ├─ Supporter.generate_argument(is_initial=True)
   │     │  └─ Opposer.generate_argument(is_initial=True)
   │     │
   │     └─ else:
   │        ├─ Supporter.analyze_opponent_arguments()
   │        ├─ Supporter.generate_argument(is_initial=False)
   │        │  └─ Includes full history context
   │        │
   │        ├─ Opposer.analyze_opponent_arguments()
   │        └─ Opposer.generate_argument(is_initial=False)
   │           └─ Includes full history context
   │
   │     └─ Store arguments in debater histories
   │        ├─ supporter.add_own_argument()
   │        ├─ opposer.add_own_argument()
   │        ├─ supporter.add_opponent_argument()
   │        └─ opposer.add_opponent_argument()
   │
   ├─ _run_judge_evaluation()
   │  └─ Judge.score_debate()
   │     └─ Returns List[Score]
   │
   ├─ _determine_winner(scores)
   │  └─ Returns winner name or None
   │
   └─ Return DebateResult
```

## History Tracking

### How It Works

Each Debater maintains two histories:

1. **argument_history**: Own arguments by round
   ```python
   [
       {"round": 1, "content": "Initial argument..."},
       {"round": 2, "content": "Second argument..."}
   ]
   ```

2. **opponent_argument_history**: Opponent's arguments by round
   ```python
   [
       {"round": 1, "content": "Opponent's initial..."},
       {"round": 2, "content": "Opponent's rebuttal..."}
   ]
   ```

### History in Prompts

For rounds 2+, the prompt includes:

```
DEBATE HISTORY:

Your previous arguments:
Round 1: [full argument text]
Round 2: [full argument text]
---

Opponent's arguments:
Round 1: [full argument text]
Round 2: [full argument text]
---

You must address gaps and weaknesses while introducing NEW INFORMATION
```

### Preventing Repetition

The system enforces new information through:

1. **Explicit instructions** in prompts:
   - "Do not repeat arguments you've already made"
   - "Be substantively different from all your previous arguments"

2. **History context** ensuring model sees previous points

3. **Gap analysis** forcing focus on opponent's new weaknesses

## UI Layer (app.py)

### Structure

Located in `app.py:1-359`

**Sections:**
1. Page configuration (st.set_page_config)
2. Styling
3. Display functions
4. Main application logic

### Key Functions

#### `display_argument(argument)`

Shows single argument with:
- Participant name and round
- Word count
- Content
- Identified gaps (if any)

#### `display_score(score)`

Shows expandable score with:
- 4 metric columns
- Detailed feedback

#### `display_debate_result(result)`

Shows complete result:
- Winner announcement
- Argument history by round
- Judge evaluation
- Download options (JSON, CSV)

#### `main()`

Streamlit app entry point:
- Sidebar configuration
- Session state management
- Progress tracking
- Error handling

### Configuration Input

Sidebar fields:
- **Topic**: Text area for debate topic
- **Models**: One field per participant
- **Names**: Customizable names for all participants
- **Rounds**: Slider for 1-10 rounds

### Result Display

After debate completes:
- Winner with score
- Full argument history organized by round
- Judge evaluation with feedback
- Download buttons for JSON/CSV

## Data Flow

```
User Input (UI)
    ↓
Configuration → Sidebar
    ↓
Start Button → DebateSession.run()
    ↓
Core Engine processes:
    ├─ Organizer overview
    ├─ N debate rounds
    │  ├─ Argument generation
    │  ├─ History tracking
    │  └─ Gap analysis
    └─ Judge evaluation
    ↓
DebateResult object
    ↓
UI Display
    ├─ Results visualization
    ├─ Argument history
    ├─ Score breakdown
    └─ Download options
```

## Error Handling

### Three Levels of Error Handling

1. **Participant Level** (`generate_response`):
   - Try-catch around litellm calls
   - Logging of errors
   - Fallback return of empty string

2. **Analysis Level** (`analyze_opponent_arguments`):
   - JSON parse error handling
   - Returns empty list if parsing fails
   - Logs warnings

3. **UI Level** (`app.py main()`):
   - Try-catch around debate.run()
   - User-friendly error messages
   - Progress indicator cleanup

## Logging

All components use Python logging:
```python
logger = logging.getLogger(__name__)
logger.info("Starting debate...")
logger.debug("Running organizer round")
logger.warning("Failed to parse JSON")
logger.error("Error generating response")
```

## Model Support

Via litellm, supports:

| Provider | Format | Example |
|----------|--------|---------|
| OpenAI | Direct name | `gpt-4`, `gpt-3.5-turbo` |
| Anthropic | Full version | `claude-3-opus-20240229` |
| Ollama | `ollama/<model>` | `ollama/llama2` |
| Google | Direct name | `gemini-pro` |
| Others | Provider prefixed | `bedrock/claude-3` |

## Extension Points

### Adding New Participant Types

```python
class Commentator(Participant):
    def get_role(self) -> str:
        return "commentator"

    def provide_commentary(self, topic, arguments):
        # Custom logic
        pass
```

### Custom Scoring Criteria

Modify Judge.score_debate() to add new criteria or adjust weights.

### Custom Result Processing

Extend DebateResult with additional methods:
```python
def get_debate_summary(self) -> str:
    # Custom summary generation
    pass
```

## File Organization

```
AIDebator/
├── topic_debate.py      # Core engine (768 lines)
├── app.py               # Streamlit UI (359 lines)
├── sl_debate.py         # Legacy combined version (530 lines)
├── requirements.txt     # Dependencies
├── README.md            # User documentation
├── ARCHITECTURE.md      # This file
└── .git/                # Version control
```

## Dependencies

```
streamlit>=1.28.0       # Web framework
litellm>=1.0.0          # LLM abstraction
python-dotenv>=1.0.0    # Environment variables
pandas>=1.3.0           # Data manipulation (for CSV export)
```

## Performance Considerations

### API Calls
- Round 0: 1 call (organizer)
- Round N: 2 calls per round (both debaters)
- Final: 2 calls (judge, one per debater)
- Total: 2N + 3 calls for N rounds

### Memory Usage
- Argument history stored in memory
- Complete debate fits in RAM for 10+ rounds
- Large prompts due to history inclusion

### Execution Time
- Depends on LLM provider
- Typical: 30 seconds to 5 minutes per debate
- Bottleneck: LLM response time

## Future Enhancements

1. **Persistent Storage**: Database for debate history
2. **Audience Voting**: Incorporate external feedback
3. **Multi-Language**: Translate debates
4. **Live Streaming**: Real-time debate broadcasting
5. **Debate Templates**: Pre-made argument structures
6. **Analytics**: Debate statistics and trends
7. **Comparison**: Side-by-side debater analysis
8. **Custom Judges**: User-defined scoring criteria

## Troubleshooting

### Common Issues

**Issue**: "Error with {name}: API key not configured"
- **Solution**: Set environment variables for your LLM provider

**Issue**: "Failed to parse judge response"
- **Solution**: Judge model may not support JSON; try different model

**Issue**: Repetitive arguments in later rounds
- **Solution**: History context not being included; check model's context window

**Issue**: Slow execution
- **Solution**: Using large models or slow provider; switch to faster model
