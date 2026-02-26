import sys
import os
import logging
from src.debate import (
    DebateConfig,
    DebateSession,
    Organizer,
    Debater,
    Judge
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_modular_debate():
    print("\n--- TESTING MODULAR DEBATE ENGINE ---")
    
    topic = "The universal basic income is necessary for a stable society."
    supporter_persona = "A progressive economist specializing in wealth redistribution."
    opposer_persona = "A libertarian policy analyst focused on individual incentives and market efficiency."
    
    config = DebateConfig(
        topic=topic,
        organizer_model="ollama/gemma3:latest",
        supporter_model="ollama/gemma3:latest",
        supporter_persona=supporter_persona,
        opposer_model="ollama/gemma3:latest",
        opposer_persona=opposer_persona,
        judge_model="ollama/gemma3:latest",
        num_rounds=1
    )
    
    print(f"Topic: {config.topic}")
    print(f"Supporter Persona: {config.supporter_persona}")
    print(f"Opposer Persona: {config.opposer_persona}")
    
    print("\nInitializing session...")
    session = DebateSession.from_config(config)
    
    print("Running debate (1 round)...")
    result = session.run(num_rounds=1)
    
    print("\n--- DEBATE COMPLETED ---")
    print(f"Winner: {result.winner}")
    print(f"Total Arguments: {len(result.arguments)}")
    
    # Verify personas are used
    for arg in result.arguments:
        if arg.participant_role == "supporter":
            print(f"\nSupporter argument starts with: {arg.content[:100]}...")
        elif arg.participant_role == "opposer":
            print(f"\nOpposer argument starts with: {arg.content[:100]}...")

    print("\nTest finished successfully!")

if __name__ == "__main__":
    try:
        test_modular_debate()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)
