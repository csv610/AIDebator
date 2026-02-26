"""Debate session orchestrator."""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from ..models import DebateConfig, Argument, Score, DebateTermination, DebateResult
from ..participants import Organizer, Debater, Judge

logger = logging.getLogger(__name__)


class DebateSession:
    """Orchestrates the complete debate flow."""

    def __init__(
        self,
        topic: str,
        organizer: Organizer,
        supporter: Debater,
        opposer: Debater,
        judge: Judge
    ):
        """
        Initialize debate session.

        Args:
            topic: The debate topic
            organizer: Organizer participant
            supporter: Supporting debater
            opposer: Opposing debater
            judge: Judge participant
        """
        self.topic = topic
        self.organizer = organizer
        self.supporter = supporter
        self.opposer = opposer
        self.judge = judge
        self.arguments: List[Argument] = []

    @classmethod
    def from_config(cls, config: DebateConfig) -> "DebateSession":
        """
        Create a DebateSession from a DebateConfig object.

        Args:
            config: DebateConfig object with all debate settings

        Returns:
            DebateSession instance ready to run
        """
        # Pydantic handles validation automatically on instantiation of DebateConfig,
        # but if we get a raw dict or unvalidated object, we can ensure it's valid here.
        validated_config = DebateConfig.model_validate(config)

        organizer = Organizer("Organizer", validated_config.organizer_model)
        supporter = Debater(
            "Supporter", 
            validated_config.supporter_model, 
            is_supporter=True, 
            persona=validated_config.supporter_persona
        )
        opposer = Debater(
            "Opposer", 
            validated_config.opposer_model, 
            is_supporter=False, 
            persona=validated_config.opposer_persona
        )
        judge = Judge("Judge", validated_config.judge_model)

        logger.info(f"Created DebateSession from config: {validated_config.topic}")
        return cls(
            topic=validated_config.topic,
            organizer=organizer,
            supporter=supporter,
            opposer=opposer,
            judge=judge
        )

    def run(self, num_rounds: int) -> DebateResult:
        """
        Run the complete debate.

        Args:
            num_rounds: Number of debate rounds

        Returns:
            DebateResult containing all arguments and scores
        """
        print(f"\n🚀 Starting debate on: '{self.topic}'")
        print(f"📅 Rounds: {num_rounds}")
        logger.info(f"Starting debate on '{self.topic}' with {num_rounds} rounds")

        # Round 0: Organizer overview
        print("\n🎤 Organizer is preparing the topic overview...")
        self._run_organizer_round()
        print("✅ Overview completed.")

        # Rounds 1-N: Debate rounds
        termination = None
        for round_num in range(1, num_rounds + 1):
            print(f"\n🔔 Round {round_num} of {num_rounds}...")
            termination = self._run_debate_round(round_num)
            if termination and termination.terminated:
                print(f"⚠️ Debate terminated early: {termination.reason}")
                logger.info(f"Debate terminated: {termination.reason}")
                break

        # Final: Judge evaluation
        print("\n⚖️ Judge is evaluating the debate...")
        scores = self._run_judge_evaluation()
        print("✅ Evaluation completed.")

        # Final Summaries and Reflection
        print("\n📝 Generating participant summaries and reflections...")
        participant_summaries = {
            self.supporter.name: self.supporter.generate_summary(self.topic),
            self.opposer.name: self.opposer.generate_summary(self.topic)
        }
        
        reflective_analysis = {
            self.supporter.name: self.supporter.generate_reflective_analysis(self.topic),
            self.opposer.name: self.opposer.generate_reflective_analysis(self.topic)
        }
        print("✅ Summaries and reflections generated.")

        # Determine winner
        winner = self._determine_winner(scores)

        # Create termination record if not set
        if not termination:
            termination = DebateTermination(
                terminated=False,
                reason="completed",
                round_number=num_rounds,
                message="Debate completed successfully"
            )

        result = DebateResult(
            topic=self.topic,
            arguments=self.arguments,
            scores=scores,
            winner=winner,
            timestamp=datetime.now().isoformat(),
            num_rounds=num_rounds,  # Use actual requested rounds
            participants={
                self.organizer.name: self.organizer.get_role(),
                self.supporter.name: self.supporter.get_role(),
                self.opposer.name: self.opposer.get_role(),
                self.judge.name: self.judge.get_role()
            },
            termination=termination,
            participant_summaries=participant_summaries,
            reflective_analysis=reflective_analysis
        )

        logger.info(f"Debate completed. Winner: {winner}. Termination: {termination.reason}")
        print(f"\n🏆 Debate Finished! Winner: {winner if winner else 'Tie'}")
        return result

    def _run_organizer_round(self) -> None:
        """Run organizer's overview round."""
        logger.debug("Running organizer round")

        overview = self.organizer.generate_overview(self.topic)

        arg = Argument(
            round_number=0,
            participant_name=self.organizer.name,
            participant_role="organizer",
            content=overview,
            timestamp=datetime.now().isoformat(),
            word_count=self.organizer.count_words(overview)
        )
        self.arguments.append(arg)

    def _run_debate_round(self, round_num: int) -> Optional[DebateTermination]:
        """
        Run a single debate round with both debaters.

        Returns:
            DebateTermination if debate should stop, None otherwise
        """
        logger.debug(f"Running debate round {round_num}")

        is_initial = (round_num == 1)

        # 1. Calculate intermediate scores for strategic adaptation
        supporter_score, opposer_score = self._get_intermediate_scores(round_num, is_initial)

        # 2. Supporter's turn
        termination = self._process_debater_turn(
            self.supporter,
            self.opposer,
            round_num,
            is_initial,
            supporter_score,
            opposer_score
        )
        if termination:
            return termination

        # 3. Opposer's turn
        termination = self._process_debater_turn(
            self.opposer,
            self.supporter,
            round_num,
            is_initial,
            opposer_score,
            supporter_score
        )
        if termination:
            return termination

        return None

    def _get_intermediate_scores(self, round_num: int, is_initial: bool) -> Tuple[Optional[float], Optional[float]]:
        """Calculate intermediate scores if not initial round."""
        supporter_score = None
        opposer_score = None

        if not is_initial and round_num > 1:
            try:
                intermediate_scores = self.judge.score_debate(self.topic, self.arguments)
                for score in intermediate_scores:
                    if score.debater_role == "supporter":
                        supporter_score = score.overall_score
                    elif score.debater_role == "opposer":
                        opposer_score = score.overall_score
                logger.info(f"Intermediate scores - Supporter: {supporter_score:.1f}, Opposer: {opposer_score:.1f}")
            except Exception as e:
                logger.warning(f"Could not calculate intermediate scores: {str(e)}")

        return supporter_score, opposer_score

    def _process_debater_turn(
        self,
        debater: Debater,
        opponent: Debater,
        round_num: int,
        is_initial: bool,
        own_score: Optional[float],
        opponent_score: Optional[float]
    ) -> Optional[DebateTermination]:
        """Process a single debater's turn including generation, validation, and storage."""
        
        # Generate argument
        if is_initial:
            content = debater.generate_argument(self.topic, round_num, is_initial=True)
        else:
            content = debater.generate_argument(
                self.topic,
                round_num,
                is_initial=False,
                own_score=own_score,
                opponent_score=opponent_score
            )

        # Validate quality
        if not is_initial:
            is_valid, reason = debater.validate_argument_quality(self.topic, content)
            if not is_valid:
                logger.warning(f"{debater.name} argument validation failed: {reason}")
                return DebateTermination(
                    terminated=True,
                    reason="low_quality",
                    round_number=round_num,
                    debater_name=debater.name,
                    message=reason
                )

        # Evaluate opponent's latest argument (if not initial)
        valid_points = None
        weaknesses = None
        if not is_initial:
            opponent_args = [arg for arg in self.arguments if arg.participant_role == opponent.get_role()]
            if opponent_args:
                valid_points, weaknesses = debater.evaluate_opponent_argument(
                    self.topic,
                    opponent_args[-1].content
                )

        # Create and store argument object
        arg_obj = Argument(
            round_number=round_num,
            participant_name=debater.name,
            participant_role=debater.get_role(),
            content=content,
            timestamp=datetime.now().isoformat(),
            word_count=debater.count_words(content),
            gaps_identified=debater.analyze_opponent_arguments(
                self.topic,
                [arg.content for arg in self.arguments if arg.participant_role == opponent.get_role()]
            ) if not is_initial else None,
            acknowledged_valid_points=valid_points,
            identified_weaknesses=weaknesses
        )

        # Update histories and session
        debater.add_own_argument(content, round_num)
        opponent.add_opponent_argument(content, round_num)
        self.arguments.append(arg_obj)

        return None

    def _run_judge_evaluation(self) -> List[Score]:
        """
        Run judge evaluation.

        Returns:
            List of scores
        """
        logger.debug("Running judge evaluation")
        return self.judge.score_debate(self.topic, self.arguments)

    def _determine_winner(self, scores: List[Score]) -> Optional[str]:
        """
        Determine debate winner based on scores.

        Args:
            scores: List of scores

        Returns:
            Winner role (supporter/opposer) or None if tie
        """
        if len(scores) < 2:
            return None

        scores_sorted = sorted(scores, key=lambda s: s.overall_score, reverse=True)

        if scores_sorted[0].overall_score > scores_sorted[1].overall_score:
            return scores_sorted[0].debater_role
        else:
            return None  # Tie
