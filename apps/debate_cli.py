import argparse
import asyncio
import json
import sys
from typing import Any

from dotenv import load_dotenv

from src.debate import DebateConfig, DebateResult, DebateSession

load_dotenv()


# ============================================================================
# CONFIGURATION & DEFAULTS
# ============================================================================

DEFAULT_CONFIG = {
    "organizer": {"name": "Moderator", "model": "ollama/gemma3"},
    "supporter": {"name": "Debater A", "model": "ollama/gemma3"},
    "opposer": {"name": "Debater B", "model": "ollama/gemma3"},
    "judge": {"name": "Judge", "model": "ollama/gemma3"},
    "num_rounds": 3,
}


# ============================================================================
# CLI FUNCTIONS
# ============================================================================


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_section(text: str) -> None:
    """Print formatted section header."""
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}\n")


def print_argument(argument) -> None:
    """Print a single argument."""
    print(f"▶ {argument.participant_name} (Round {argument.round_number})")
    print(f"  Words: {argument.word_count}")
    print(f"  {'-'*76}")
    print(f"  {argument.content}")
    if argument.gaps_identified:
        print("\n  🎯 Gaps Identified:")
        for gap in argument.gaps_identified[:3]:
            print(f"     • {gap}")
    print()


def print_score(score) -> None:
    """Print a score."""
    print(f"\n📊 {score.debater_role.title()}")
    print(f"  {'─'*76}")
    print(f"  Argument Quality:       {score.argument_quality:5.1f}/10")
    print(f"  Evidence Quality (40%): {score.evidence_quality:5.1f}/10  ⭐ CRITICAL")
    print(f"  Logical Consistency:    {score.logical_consistency:5.1f}/10")
    print(f"  Responsiveness to Gaps: {score.responsiveness_to_gaps:5.1f}/10")
    print(f"  {'─'*76}")
    print(f"  OVERALL SCORE:          {score.overall_score:5.1f}/10")
    print("\n  📈 Evidence Metrics:")
    print(f"     • Facts & Citations:          {score.fact_count}")
    print(f"     • Evidence-Backed Arguments:  {score.irrefutable_arguments}")
    print("\n  Detailed Feedback:")
    for line in score.feedback.split("\n"):
        if line.strip():
            print(f"    {line}")


def print_baseline(baseline) -> None:
    """Print single-agent baseline."""
    print("▶ SINGLE-AGENT CONTROL GROUP ANALYSIS")
    print(f"  Words: {len(baseline.content.split())}")
    print(f"  {'-'*76}")
    print(f"  {baseline.content[:500]}...")
    print(f"\n  📊 Baseline Score: {baseline.score.overall_score:.1f}/10")
    print(f"     (Evidence: {baseline.score.evidence_quality:.1f}, Logic: {baseline.score.logical_consistency:.1f})")


def print_comparison(result: DebateResult) -> None:
    """Print scientific comparison between baseline and debate."""
    if not result.baseline:
        return

    # Find the winning score (or highest score)
    best_score = max([s.overall_score for s in result.scores])
    baseline_score = result.baseline.score.overall_score
    delta = best_score - baseline_score

    # Calculate evidence density improvement
    total_debate_facts = sum([s.fact_count for s in result.scores])
    baseline_facts = result.baseline.score.fact_count

    print_header("SCIENTIFIC IMPACT ANALYSIS")

    print("📈 REASONING IMPROVEMENT")
    print(f"   • Single-Agent Baseline Score: {baseline_score:.1f}/10")
    print(f"   • Multi-Agent Debate Score:   {best_score:.1f}/10")
    status = "IMPROVEMENT" if delta > 0 else "DECLINE"
    print(f"   • Reasoning Delta:            {delta:+.1f} points ({status})")

    print("\n📚 EVIDENCE DENSITY")
    print(f"   • Baseline Fact Count:        {baseline_facts}")
    print(f"   • Debate Total Fact Count:    {total_debate_facts}")
    if baseline_facts > 0:
        increase = ((total_debate_facts - baseline_facts) / baseline_facts) * 100
        print(f"   • Evidence Volume Increase:   {increase:+.1f}%")

    print(f"\n🔍 VERDICT: {'Debate yielded superior reasoning' if delta > 0 else 'Single-agent was sufficient'}")


def print_reflection(name: str, summary: str, reflection) -> None:
    """Print participant summary and reflection."""
    print(f"\n👤 Participant: {name}")
    print(f"  {'─'*76}")
    print("  📝 FINAL SUMMARY:")
    for line in summary.split("\n"):
        if line.strip():
            print(f"    {line}")

    if reflection:
        print("\n  🧠 REFLECTIVE ANALYSIS:")

        # Learned
        print("     💡 Learned from opponent:")
        if reflection.learned:
            for item in reflection.learned:
                print(f"        • {item}")
        else:
            print("        (No specific learning points identified)")

        # Weaknesses
        print("\n     📉 Self-identified weaknesses:")
        if reflection.weaknesses:
            for item in reflection.weaknesses:
                print(f"        • {item}")
        else:
            print("        (No weaknesses identified)")

        # Corrections
        print("\n     🛠️  Corrections made:")
        if reflection.corrections:
            for item in reflection.corrections:
                print(f"        • {item}")
        else:
            print("        (No corrections needed)")


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in configuration file: {config_path}")
        sys.exit(1)


def save_config(config: dict[str, Any], output_path: str) -> None:
    """Save configuration to JSON file."""
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to {output_path}")


async def run_debate_from_args(args) -> DebateResult:
    """Run debate using command-line arguments asynchronously."""

    # Load or build configuration dictionary
    if args.config:
        config_dict = load_config(args.config)
    else:
        # Map flat DEFAULT_CONFIG to expected DebateConfig structure if needed
        # but here we'll just build it directly to match DebateConfig
        config_dict = {
            "topic": args.topic or "",
            "organizer_model": args.organizer_model or DEFAULT_CONFIG["organizer"]["model"],
            "supporter_model": args.supporter_model or DEFAULT_CONFIG["supporter"]["model"],
            "supporter_persona": args.supporter_persona,
            "opposer_model": args.opposer_model or DEFAULT_CONFIG["opposer"]["model"],
            "opposer_persona": args.opposer_persona,
            "judge_model": args.judge_model or DEFAULT_CONFIG["judge"]["model"],
            "num_rounds": args.rounds or DEFAULT_CONFIG["num_rounds"],
        }

    try:
        # Validate using Pydantic
        config = DebateConfig.model_validate(config_dict)

        # Create and run debate
        print_header(f"STARTING DEBATE: {config.topic}")

        print("Participants:")
        print(f"  🎤 Organizer Model: {config.organizer_model}")
        print(f"  ✓ Supporter Model: {config.supporter_model}")
        print(f"  ✗ Opposer Model: {config.opposer_model}")
        print(f"  🏛️  Judge Model: {config.judge_model}")
        print(f"\nRounds: {config.num_rounds}")

        debate = DebateSession.from_config(config)
        result = await debate.run(num_rounds=config.num_rounds)
        return result
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


def display_result(result: DebateResult) -> None:
    """Display debate result in terminal."""

    # Baseline (Control Group)
    if result.baseline:
        print_section("Control Group: Single-Agent Baseline")
        print_baseline(result.baseline)

    # Organizer overview
    print_section("Round 0: Topic Overview")
    organizer_arg = [arg for arg in result.arguments if arg.participant_role == "organizer"]
    if organizer_arg:
        print_argument(organizer_arg[0])

    # Debate rounds
    for round_num in range(1, result.num_rounds + 1):
        print_section(f"Round {round_num}")
        round_args = [arg for arg in result.arguments if arg.round_number == round_num]
        for arg in round_args:
            print_argument(arg)

    # Judge evaluation
    print_section("Judge's Evaluation")

    for score in result.scores:
        print_score(score)

    # Participant Summaries and Reflections
    if result.participant_summaries or result.reflective_analysis:
        print_section("Participant Summaries & Reflections")
        for name in result.participants:
            if result.participants[name] in ["supporter", "opposer"]:
                summary = result.participant_summaries.get(name, "No summary available")
                reflection = result.reflective_analysis.get(name) if result.reflective_analysis else None
                print_reflection(name, summary, reflection)

    # Winner
    print_section("Final Result")
    if result.winner:
        scores_dict = {s.debater_role: s.overall_score for s in result.scores}
        winner_score = scores_dict[result.winner]
        print(f"🏆 WINNER: {result.winner.title()}")
        print(f"   Score: {winner_score:.1f}/10")
    else:
        print("⚖️  RESULT: TIE")
        print("   Both debaters presented equally compelling arguments")

    # Termination status
    if result.termination:
        if result.termination.terminated and result.termination.reason != "completed":
            print()
            print("⛔  DEBATE TERMINATED")
            print(f"   Round: {result.termination.round_number}")
            print(f"   Reason: {result.termination.reason.replace('_', ' ').title()}")
            if result.termination.debater_name:
                print(f"   Debater: {result.termination.debater_name}")
            if result.termination.message:
                print(f"   Details: {result.termination.message}")
        else:
            print()
            print(f"✅  DEBATE STATUS: Completed successfully ({result.num_rounds} rounds)")

    # Final Scientific Comparison
    if result.baseline:
        print_comparison(result)

    print()


def main():
    """Sync CLI entry point (wraps async main)."""
    asyncio.run(_async_main())


async def _async_main():
    """Async CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Run AI debates from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple debate with default models
  python debate_cli.py --topic "AI will improve employment" --rounds 3

  # Specify different models for each participant
  python debate_cli.py \\
    --topic "Remote work is better than office" \\
    --organizer-model gpt-4 \\
    --supporter-model claude-3-opus-20240229 \\
    --opposer-model ollama/llama2 \\
    --judge-model gpt-4 \\
    --rounds 5

  # Load from configuration file
  python debate_cli.py --config debate_config.json

  # Save configuration for later use
  python debate_cli.py --topic "..." --save-config my_debate.json

  # Run and save result
  python debate_cli.py --topic "..." --save-result debate_result.json
        """,
    )

    # Configuration
    parser.add_argument("--config", help="Load debate configuration from JSON file")
    parser.add_argument("--save-config", help="Save debate configuration to JSON file")

    # Debate parameters
    parser.add_argument("--topic", help="Debate topic")
    parser.add_argument("--rounds", type=int, help="Number of debate rounds (1-10)")

    # Model selection
    parser.add_argument("--organizer-model", help="Model for organizer (e.g., gpt-4)")
    parser.add_argument("--supporter-model", help="Model for supporter (e.g., gpt-3.5-turbo)")
    parser.add_argument("--supporter-persona", help="Expert persona for the supporter")
    parser.add_argument("--opposer-model", help="Model for opposer (e.g., claude-3-opus-20240229)")
    parser.add_argument("--opposer-persona", help="Expert persona for the opposer")
    parser.add_argument("--judge-model", help="Model for judge (e.g., gpt-4)")

    # Output options
    parser.add_argument("--save-result", help="Save debate result to JSON file")
    parser.add_argument("--quiet", action="store_true", help="Don't display result in terminal")

    # Help
    parser.add_argument("--example", action="store_true", help="Show example configuration")

    args = parser.parse_args()

    # Show example configuration
    if args.example:
        print_header("EXAMPLE CONFIGURATION")
        print(json.dumps(DEFAULT_CONFIG, indent=2))
        print("\nSave this as a .json file and use with --config flag")
        return

    # Run debate
    result = await run_debate_from_args(args)

    # Save configuration if requested
    if args.save_config:
        config = DEFAULT_CONFIG.copy()
        config["topic"] = result.topic
        config["num_rounds"] = result.num_rounds
        save_config(config, args.save_config)

    # Save result if requested
    if args.save_result:
        result.save(args.save_result)
        print(f"✅ Debate result saved to {args.save_result}")

    # Display result
    if not args.quiet:
        display_result(result)

    # Summary
    print_header("DEBATE STATISTICS")
    print(f"Topic: {result.topic}")
    print(f"Rounds: {result.num_rounds}")
    print(f"Total Arguments: {len(result.arguments)}")
    print(f"Participants: {len(result.participants)}")
    print(f"Winner: {result.winner if result.winner else 'TIE'}")


if __name__ == "__main__":
    main()
