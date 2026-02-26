# Score Tracking & Strategic Adaptation Feature

## Overview

Each debater now **tracks their probable score** and adapts their strategy in subsequent rounds. This creates a dynamic debate where participants make sound arguments based on:

1. Current score performance
2. Opponent's score comparison
3. Strategic guidance for improvement
4. Real-time feedback on effectiveness

## How It Works

### Intermediate Scoring

Between rounds (starting from Round 2), the system:

1. **Calculates Intermediate Scores**
   - Judge evaluates all arguments so far
   - Both debaters receive scores
   - Metrics tracked: argument quality, evidence quality, logical consistency, responsiveness

2. **Provides Score Context**
   - Each debater sees their own score
   - Each debater sees opponent's score
   - Score difference calculated
   - Strategic guidance provided

3. **Debater Adaptation**
   - Next argument generated with score context
   - Prompts include specific strategic guidance
   - Models adapt arguments based on performance

## Strategic Guidance by Score Position

### When Leading (Own Score > Opponent's + 1.5)

```
YOUR CURRENT POSITION:
- Your score: [score]/10 (Leading by [difference] points)
- Maintain your approach: strong evidence and citations are working well
- Continue presenting facts, studies, and irrefutable arguments
```

**Action**: Maintain current strategy while continuing to present evidence-backed arguments.

### When Behind (Own Score < Opponent's - 1.5)

```
YOUR CURRENT POSITION:
- Your score: [score]/10 (Behind by [difference] points)
- Critical: Increase use of citations, peer-reviewed research, and specific data
- Focus on evidence-backed arguments to close the gap
- Provide facts and verifiable sources for all major claims
```

**Action**: Urgently improve evidence quality, focus on citations, add specific data points.

### When Close (Score Difference ≤ 1.5)

```
YOUR CURRENT POSITION:
- Your score: [score]/10 (Close match with opponent at [opponent_score]/10)
- Strategy: Both sides are presenting compelling arguments
- Win by superior evidence: Use more citations, specific data, and research
- Improve on evidence quality - this will be decisive
```

**Action**: Differentiate through evidence quality, the deciding factor.

## Implementation Details

### Code Changes

#### 1. Debater.generate_argument() Updated

```python
def generate_argument(
    self,
    topic: str,
    round_number: int,
    is_initial: bool = False,
    own_score: Optional[float] = None,
    opponent_score: Optional[float] = None
) -> str:
```

**New Parameters**:
- `own_score`: Debater's current score (if available)
- `opponent_score`: Opponent's current score (if available)

#### 2. DebateSession._run_debate_round() Updated

```python
# Calculate intermediate scores if not initial round
if not is_initial and round_num > 1:
    intermediate_scores = self.judge.score_debate(self.topic, self.arguments)
    # Extract and pass scores to debaters
```

**Flow**:
1. Evaluate arguments so far
2. Calculate intermediate scores
3. Pass scores to generate_argument()
4. Generate next argument with strategic context

## Benefits

### For Debaters
- **Adaptive Strategy**: Change approach based on performance
- **Focused Improvement**: Know exactly what to fix
- **Competitive Drive**: React to opponent's performance
- **Evidence Emphasis**: Clear guidance on what matters (40% evidence quality)

### For Debates
- **Dynamic Flow**: Debates evolve based on performance
- **Strategic Depth**: Arguments become more sophisticated
- **Higher Quality**: Pressure to improve weak areas
- **Realistic**: Models adapt like human debaters would

### For Analysis
- **Performance Tracking**: See how scores influence strategy
- **Strategic Decisions**: Understand what prompts better arguments
- **Learning**: Study how models respond to feedback
- **Improvement Path**: Track progression through rounds

## Example: Round-by-Round Evolution

### Round 1: Initial Arguments
**No scores yet** - Both debaters present opening arguments with equal preparation.

```
Supporter: Presents initial thesis-based argument
Opposer:   Presents counter-thesis-based argument
```

### Round 2: First Strategic Adjustment
**Scores calculated from Round 1**

**Scenario A: Supporter ahead (7.5 vs 6.5)**
```
Score Context for Supporter:
"Your score: 7.5/10 (Leading by 1.0 points)
- Maintain your approach: strong evidence and citations are working well
- Continue presenting facts, studies, and irrefutable arguments"

Result: Supporter continues evidence-focused strategy
```

**Scenario B: Opposer ahead (6.2 vs 5.8)**
```
Score Context for Supporter:
"Your score: 5.8/10 (Behind by 0.4 points)
- Strategy: Both sides are presenting compelling arguments
- Win by superior evidence: Use more citations, specific data, and research"

Result: Supporter intensifies evidence collection in next argument
```

### Round 3: Refined Strategy
Based on Round 2 scores, both debaters further refine approach.

## Real-Time Impact

### What Debaters See (in Prompt Context)

**Example - Round 2 Prompt for Supporter when Leading:**

```
DEBATE HISTORY:
[Full history of arguments...]

YOUR CURRENT POSITION:
- Your score: 7.8/10 (Leading by 1.5 points)
- Maintain your approach: strong evidence and citations are working well
- Continue presenting facts, studies, and irrefutable arguments

Task: Present your supporting rebuttal with NEW ARGUMENTS and NEW INFORMATION.
IMPORTANT: Do not repeat arguments you've already made. Focus on:
1. Addressing specific weaknesses in the opponent's latest arguments
2. Introducing completely new evidence, examples, or logical arguments
3. Building on previous points with deeper analysis
4. Challenging any new claims the opponent has introduced
5. STRENGTHEN YOUR EVIDENCE: The judge heavily weights factual claims and citations (40% of score)
```

## Score Calculation for Intermediate Scoring

Uses the same weighted formula:

```
Overall Score = (Evidence Quality × 0.4)
              + (Argument Quality × 0.2)
              + (Logical Consistency × 0.2)
              + (Responsiveness to Gaps × 0.2)
```

Each round's scores are based on all arguments presented up to that point.

## Error Handling

If intermediate scoring fails:
- System logs warning but continues
- Debaters generate next argument without score context
- Debate proceeds normally
- Final scoring still occurs

```python
try:
    intermediate_scores = self.judge.score_debate(self.topic, self.arguments)
    # Extract scores
except Exception as e:
    logger.warning(f"Could not calculate intermediate scores: {str(e)}")
    # Continue without scores
```

## Logging

All score-tracking is logged:

```
INFO: Intermediate scores - Debater A: 7.5, Debater B: 6.2
INFO: Debater A generating rebuttal argument for round 2 (own_score=7.5, opponent_score=6.2)
```

Enables analysis of how models respond to score context.

## Strategic Implications

### Model Behavior
Different models may:
- Increase citations when behind
- Maintain quality when leading
- Focus on addressing gaps when close
- Adjust tone based on performance

### Debate Characteristics
Debates with this feature:
- Have stronger evidence in later rounds
- Show clearer strategic shifts
- Respond to scoring incentives
- Demonstrate adaptive reasoning

### Competitive Dynamics
- Leading debaters maintain consistency
- Trailing debaters increase effort
- Close matches drive differentiation
- Evidence quality becomes decisive

## Configuration

This feature is **automatically enabled**:
- Starts in Round 2
- Uses same judge for scoring
- Calculates every round after Round 1
- No user configuration needed

## API Usage

For users implementing custom debates:

```python
from topic_debate import DebateSession, Organizer, Debater, Judge

# Create participants and session
debate = DebateSession(...)

# Run debate - score tracking happens automatically
result = debate.run(num_rounds=3)

# Results include intermediate progression
for argument in result.arguments:
    print(f"Round {argument.round_number}: {argument.participant_name}")
```

## Monitoring Score Progress

In the UI (app.py), after each round:

```
Round 2:
  [Debater A's argument with score context...]
  [Debater B's argument with score context...]

[Between rounds, optional: Show intermediate scores]

Round 3:
  [Debater A's argument adapting to Round 2 scores...]
  [Debater B's argument adapting to Round 2 scores...]
```

## Limitations

1. **First Round**: No intermediate scores available, arguments are initial
2. **Calculation Cost**: Each intermediate score requires judge evaluation
3. **Model Variations**: Different models may respond differently to score context
4. **Strategy Unpredictability**: Models may not always use feedback optimally

## Future Enhancements

1. **Score History**: Show complete score progression
2. **Confidence Levels**: Include confidence in scores
3. **Specific Feedback**: Detailed guidance on what to improve
4. **Historical Comparison**: Compare to previous debates
5. **Momentum Tracking**: Show score trends

## Validation & Testing

To verify score-tracking is working:

1. **Check Logs**: Look for "Intermediate scores" messages
2. **Review Arguments**: See if later arguments cite more sources
3. **Analyze Prompts**: Confirm score context in generation prompts
4. **Compare Scores**: Verify intermediate scores differ from final scores

## Example Output

When running a debate with score tracking:

```
Running debate round 2...
Calculating intermediate scores...
INFO: Intermediate scores - Alice: 7.2, Bob: 6.8

Alice (Supporter) generating argument round 2:
- Score context: Leading by 0.4 points, maintain evidence approach
- Argument generated with focus on maintaining evidence quality

Bob (Opposer) generating argument round 2:
- Score context: Behind by 0.4 points, need more citations
- Argument generated with emphasis on evidence and citations

Running debate round 3...
Calculating intermediate scores...
INFO: Intermediate scores - Alice: 7.5, Bob: 7.2

[Bob's score improved, showing effect of evidence focus]
```

## Summary

This feature creates **dynamic, adaptive debates** where:
- Debaters see their performance
- Strategies evolve based on results
- Evidence quality becomes decisive
- Debates demonstrate realistic competition
- Models respond to feedback and incentives

**Result**: More engaging, strategic, and evidence-focused debates.

---

**Version**: 1.0
**Added**: November 24, 2025
**Status**: Production Ready
