# DebateConfig - Configuration Management

## Overview

The `DebateConfig` dataclass provides a structured, reusable way to configure debates. It encapsulates all debate settings in a single object that can be:

- Created programmatically
- Loaded from JSON files
- Validated before use
- Serialized for storage/sharing
- Used to create DebateSession instances

---

## DebateConfig Dataclass

### Definition

```python
@dataclass
class DebateConfig:
    """Configuration for a debate session."""
    topic: str                          # The debate topic
    organizer_model: str                # LLM model for organizer
    supporter_model: str                # LLM model for supporter
    opposer_model: str                  # LLM model for opposer
    judge_model: str                    # LLM model for judge
    num_rounds: int = 3                 # Number of debate rounds (1-10)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def validate(self) -> Tuple[bool, str]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| topic | str | Yes | - | The debate topic (any length) |
| organizer_model | str | Yes | - | LLM model for organizer (e.g., "gpt-4") |
| supporter_model | str | Yes | - | LLM model for supporter |
| opposer_model | str | Yes | - | LLM model for opposer |
| judge_model | str | Yes | - | LLM model for judge |
| num_rounds | int | No | 3 | Number of debate rounds (1-10) |

**Note**: Participant names are now fixed to standard values:
- Organizer: "Organizer"
- Supporter: "Supporter"
- Opposer: "Opposer"
- Judge: "Judge"

---

## Creating DebateConfig

### Method 1: Direct Instantiation

```python
from src.debate import DebateConfig

config = DebateConfig(
    topic="AI will improve employment",
    organizer_model="gpt-4",
    supporter_model="claude-3-opus-20240229",
    opposer_model="gpt-3.5-turbo",
    judge_model="gpt-4",
    num_rounds=3
)
```

### Method 2: From Dictionary

```python
config_dict = {
    "topic": "Remote work is better than office",
    "organizer_model": "gpt-4",
    "supporter_model": "gpt-4",
    "opposer_model": "claude-3-opus-20240229",
    "judge_model": "gpt-4",
    "num_rounds": 5
}

from src.debate import DebateConfig
config = DebateConfig(**config_dict)
```

### Method 3: From JSON File

```python
import json
from src.debate import DebateConfig

# Load from JSON
with open("debate_config.json") as f:
    data = json.load(f)
    config = DebateConfig(**data)

# Or with validation
config_dict = json.load(open("debate_config.json"))
config = DebateConfig(**config_dict)
is_valid, error = config.validate()
if not is_valid:
    print(f"Configuration error: {error}")
```

---

## Configuration Validation

### validate() Method

```python
is_valid, error_message = config.validate()

if not is_valid:
    print(f"Configuration error: {error_message}")
else:
    print("Configuration is valid")
```

### Validation Rules

1. **Topic**: Cannot be empty or whitespace-only
   - Error: "Topic cannot be empty"

2. **Num Rounds**: Must be between 1 and 10
   - Error: "Number of rounds must be between 1 and 10"

3. **Participant Models**: All four models must be specified and non-empty
   - Error: "All participant models must be specified"

### Validation Example

```python
config = DebateConfig(
    topic="",  # Invalid!
    organizer_model="gpt-4",
    supporter_model="gpt-4",
    opposer_model="gpt-4",
    judge_model="gpt-4",
    num_rounds=3
)

is_valid, msg = config.validate()
print(is_valid)  # False
print(msg)       # "Topic cannot be empty"
```

---

## Creating DebateSession from Config

### Using from_config() Class Method

```python
from src.debate import DebateConfig, DebateSession

# Create config
config = DebateConfig(
    topic="AI will improve employment",
    organizer_model="gpt-4",
    supporter_model="claude-3-opus-20240229",
    opposer_model="gpt-3.5-turbo",
    judge_model="gpt-4",
    num_rounds=3
)

# Create DebateSession from config
try:
    debate = DebateSession.from_config(config)
    result = debate.run(num_rounds=config.num_rounds)
except ValueError as e:
    print(f"Error: {e}")
```

### from_config() Method Details

```python
@classmethod
def from_config(cls, config: DebateConfig) -> "DebateSession":
    """
    Create a DebateSession from a DebateConfig object.

    Args:
        config: DebateConfig object with all debate settings

    Returns:
        DebateSession instance ready to run

    Raises:
        ValueError: If configuration is invalid
    """
```

**Behavior**:
1. Validates config with `config.validate()`
2. Raises `ValueError` if invalid
3. Creates Organizer, Debater, Judge instances with standard names
4. Returns DebateSession ready to call `run()`

---

## Use Cases

### Use Case 1: Programmatic Debate Creation

```python
from src.debate import DebateConfig, DebateSession

# Create multiple debates with different configurations
topics = [
    "AI will improve employment",
    "Remote work is better than office",
    "Social media is harmful"
]

for topic in topics:
    config = DebateConfig(
        topic=topic,
        organizer_model="gpt-4",
        supporter_model="gpt-4",
        opposer_model="claude-3-opus-20240229",
        judge_model="gpt-4",
        num_rounds=3
    )

    debate = DebateSession.from_config(config)
    result = debate.run(num_rounds=config.num_rounds)
    print(f"Topic: {topic}, Winner: {result.winner}")
```

### Use Case 2: Loading from JSON Configuration

```python
import json
from src.debate import DebateConfig, DebateSession

# Load configuration from file
with open("config.json") as f:
    data = json.load(f)
    config = DebateConfig(**data)

# Validate
is_valid, msg = config.validate()
if not is_valid:
    print(f"Error: {msg}")
    exit(1)

# Run debate
debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)
```

### Use Case 3: Building a Debate Manager

```python
from src.debate import DebateConfig, DebateSession
from typing import List

class DebateManager:
    def __init__(self, configs: List[DebateConfig]):
        self.configs = configs
        self.results = []

    def run_all(self):
        for config in self.configs:
            is_valid, msg = config.validate()
            if not is_valid:
                print(f"Skipping invalid config: {msg}")
                continue

            debate = DebateSession.from_config(config)
            result = debate.run(num_rounds=config.num_rounds)
            self.results.append(result)

    def get_winners(self):
        return [(r.topic, r.winner) for r in self.results]

# Usage
configs = [
    DebateConfig(...),
    DebateConfig(...),
]
manager = DebateManager(configs)
manager.run_all()
```

### Use Case 4: Integration with External Systems

```python
import requests
from src.debate import DebateConfig, DebateSession

# Fetch debate configuration from API
response = requests.get("https://api.example.com/debate-config")
config_data = response.json()
config = DebateConfig(**config_data)

# Run debate
debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)

# Send results back to API
requests.post("https://api.example.com/debate-result", json=result.to_dict())
```

---

## JSON Configuration Format

### Example: debate_config.json

```json
{
  "topic": "AI will have a net positive impact on employment",
  "organizer_model": "gpt-4",
  "supporter_model": "claude-3-opus-20240229",
  "opposer_model": "gpt-3.5-turbo",
  "judge_model": "gpt-4",
  "num_rounds": 3
}
```

### Loading and Using

```python
import json
from src.debate import DebateConfig, DebateSession

# Load from file
with open("debate_config.json") as f:
    config = DebateConfig(**json.load(f))

# Validate
is_valid, msg = config.validate()
assert is_valid, msg

# Run
debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)

# Save results
with open("debate_result.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2)
```

---

## Serialization

### to_dict() Method

```python
config = DebateConfig(
    topic="AI will improve employment",
    organizer_model="gpt-4",
    supporter_model="gpt-4",
    opposer_model="claude-3-opus-20240229",
    judge_model="gpt-4",
    num_rounds=3
)

config_dict = config.to_dict()
# Returns:
# {
#     "topic": "AI will improve employment",
#     "organizer_model": "gpt-4",
#     "supporter_model": "gpt-4",
#     "opposer_model": "claude-3-opus-20240229",
#     "judge_model": "gpt-4",
#     "num_rounds": 3
# }

# Save to JSON
import json
with open("config.json", "w") as f:
    json.dump(config_dict, f, indent=2)
```

---

## Integration with CLI and Web UI

### In CLI (debate_cli.py)

```python
from src.debate import DebateConfig

# Load from JSON file
config = DebateConfig(**json.load(open("config.json")))

# Or build from command-line arguments
config = DebateConfig(
    topic=args.topic,
    organizer_model=args.organizer_model,
    supporter_model=args.supporter_model,
    opposer_model=args.opposer_model,
    judge_model=args.judge_model,
    num_rounds=args.rounds
)

debate = DebateSession.from_config(config)
result = debate.run(num_rounds=config.num_rounds)
```

### In Web UI (app.py)

```python
from src.debate import DebateConfig

# Build from Streamlit inputs
config = DebateConfig(
    topic=st.sidebar.text_area("Debate Topic"),
    organizer_model=st.sidebar.text_input("Organizer Model"),
    supporter_model=st.sidebar.text_input("Supporter Model"),
    opposer_model=st.sidebar.text_input("Opposer Model"),
    judge_model=st.sidebar.text_input("Judge Model"),
    num_rounds=st.sidebar.slider("Number of Rounds", 1, 10, 3)
)

# Validate
is_valid, msg = config.validate()
if not is_valid:
    st.error(f"Configuration error: {msg}")
else:
    debate = DebateSession.from_config(config)
    result = debate.run(num_rounds=config.num_rounds)
```

---

## Error Handling

### Validation Errors

```python
from src.debate import DebateConfig

config = DebateConfig(
    topic="Valid topic",
    organizer_model="",  # Empty!
    supporter_model="gpt-4",
    opposer_model="gpt-4",
    judge_model="gpt-4"
)

is_valid, msg = config.validate()
if not is_valid:
    print(f"Error: {msg}")
    # Output: "Error: All participant models must be specified"
```

### Creation Errors

```python
from src.debate import DebateConfig, DebateSession

config = DebateConfig(...)
is_valid, msg = config.validate()
if not is_valid:
    raise ValueError(msg)

try:
    debate = DebateSession.from_config(config)
except ValueError as e:
    print(f"Failed to create debate: {e}")
```

---

## Advanced Examples

### Example 1: Batch Debate Runner

```python
import json
from src.debate import DebateConfig, DebateSession

def run_debates_from_file(filename: str):
    """Run multiple debates from a JSON file."""
    with open(filename) as f:
        configs_data = json.load(f)

    results = []
    for config_data in configs_data:
        config = DebateConfig(**config_data)
        is_valid, msg = config.validate()

        if not is_valid:
            print(f"Skipping: {msg}")
            continue

        debate = DebateSession.from_config(config)
        result = debate.run(num_rounds=config.num_rounds)
        results.append(result)

    return results
```

### Example 2: Configuration Template System

```python
from src.debate import DebateConfig

class DebateConfigTemplate:
    @staticmethod
    def quick_3_round(topic: str) -> DebateConfig:
        """Quick 3-round debate configuration."""
        return DebateConfig(
            topic=topic,
            organizer_model="gpt-4",
            supporter_model="gpt-4",
            opposer_model="gpt-3.5-turbo",
            judge_model="gpt-4",
            num_rounds=3
        )

    @staticmethod
    def thorough_5_round(topic: str) -> DebateConfig:
        """Thorough 5-round debate with diverse models."""
        return DebateConfig(
            topic=topic,
            organizer_model="gpt-4",
            supporter_model="claude-3-opus-20240229",
            opposer_model="gemini-pro",
            judge_model="gpt-4",
            num_rounds=5
        )

# Usage
config = DebateConfigTemplate.quick_3_round("AI will improve employment")
debate = DebateSession.from_config(config)
```

### Example 3: Configuration Validation with Detailed Feedback

```python
from src.debate import DebateConfig

def validate_and_report(config: DebateConfig) -> bool:
    """Validate config and provide detailed feedback."""
    is_valid, msg = config.validate()

    if not is_valid:
        print(f"❌ Configuration Error: {msg}")
        return False

    print(f"✅ Configuration Valid")
    print(f"   Topic: {config.topic}")
    print(f"   Organizer Model: {config.organizer_model}")
    print(f"   Supporter Model: {config.supporter_model}")
    print(f"   Opposer Model: {config.opposer_model}")
    print(f"   Judge Model: {config.judge_model}")
    print(f"   Rounds: {config.num_rounds}")
    return True

# Usage
config = DebateConfig(...)
if validate_and_report(config):
    debate = DebateSession.from_config(config)
```

---

## Best Practices

1. **Always Validate Before Use**
   ```python
   config = DebateConfig(...)
   is_valid, msg = config.validate()
   if not is_valid:
       raise ValueError(msg)
   ```

2. **Store Configurations in JSON**
   ```python
   # Save
   json.dump(config.to_dict(), open("config.json", "w"))
   # Load
   config = DebateConfig(**json.load(open("config.json")))
   ```

3. **Use Templates for Common Scenarios**
   ```python
   config = DebateConfigTemplate.quick_3_round(topic)
   ```

4. **Handle Errors Gracefully**
   ```python
   try:
       debate = DebateSession.from_config(config)
   except ValueError as e:
       log.error(f"Debate creation failed: {e}")
   ```

5. **Provide Clear Feedback**
   ```python
   is_valid, msg = config.validate()
   if not is_valid:
       print(f"Configuration error: {msg}")
   ```

---

## Summary

The `DebateConfig` class provides a structured, reusable way to:

✅ **Define debate configurations** with topic and LLM models
✅ **Validate configurations** before creating debates
✅ **Serialize/deserialize** configurations to/from JSON
✅ **Create DebateSession** instances easily
✅ **Reuse configurations** across multiple debates
✅ **Integrate with external systems** through JSON

This makes the platform more flexible, maintainable, and suitable for automation.

---

**Version**: 2.0
**Updated**: November 24, 2025
**Status**: Production Ready
