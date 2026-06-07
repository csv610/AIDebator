import asyncio
import logging
from datetime import datetime

from ..models import Argument, Baseline, DebateConfig, DebateResult, DebateTermination, Score
from ..participants import Debater, Judge, Organizer

logger = logging.getLogger(__name__)


class DebateSession:
    """Orchestrates the complete debate flow."""

    def __init__(self, topic: str, organizer: Organizer, supporter: Debater, opposer: Debater, judge: Judge):
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
        self.arguments: list[Argument] = []

    @classmethod
    def from_config(cls, config: DebateConfig) -> "DebateSession":
        """
        Create a DebateSession from a DebateConfig object.

        Args:
            config: DebateConfig object with all debate settings

        Returns:
            DebateSession instance ready to run
        """
        if isinstance(config, dict):
            config = DebateConfig.model_validate(config)

        organizer = Organizer("Organizer", config.organizer_model)
        supporter = Debater("Supporter", config.supporter_model, is_supporter=True, persona=config.supporter_persona)
        opposer = Debater("Opposer", config.opposer_model, is_supporter=False, persona=config.opposer_persona)
        judge = Judge("Judge", config.judge_model)

        logger.info(f"Created DebateSession from config: {config.topic}")
        return cls(
            topic=config.topic,
            organizer=organizer,
            supporter=supporter,
            opposer=opposer,
            judge=judge,
        )

    async def run(self, num_rounds: int) -> DebateResult:
        """
        Run the complete debate asynchronously.

        Args:
            num_rounds: Number of debate rounds

        Returns:
            DebateResult containing all arguments and scores
        """
        print(f"\n🚀 Starting debate on: '{self.topic}'")
        print(f"📅 Rounds: {num_rounds}")
        logger.info(f"Starting debate on '{self.topic}' with {num_rounds} rounds")

        # Control Group: Single-agent baseline
        print("\n🧪 Generating control group baseline (single-agent response)...")
        baseline_content = await self.judge.generate_baseline(self.topic)
        baseline_score = await self.judge.evaluate_baseline_score(self.topic, baseline_content)
        baseline = Baseline(content=baseline_content, score=baseline_score)
        print(f"✅ Baseline established (Score: {baseline_score.overall_score:.1f}/10)")

        # Round 0: Organizer overview
        print("\n🎤 Organizer is preparing the topic overview...")
        await self._run_organizer_round()
        print("✅ Overview completed.")

        # Rounds 1-N: Debate rounds
        termination_record = None
        for round_num in range(1, num_rounds + 1):
            is_first_round = round_num == 1
            print(f"\n🔔 Round {round_num} of {num_rounds}...")
            termination_record = await self._run_debate_round(round_num, is_first_round)
            if termination_record and termination_record.terminated:
                print(f"⚠️ Debate terminated early: {termination_record.reason}")
                logger.info(f"Debate terminated: {termination_record.reason}")
                break

        # Final: Judge evaluation
        print("\n⚖️ Judge is evaluating the debate...")
        scores = await self._run_judge_evaluation()
        print("✅ Evaluation completed.")

        # Final Summaries and Reflection
        print("\n📝 Generating participant summaries and reflections...")

        # Run summaries and reflections in parallel
        summary_tasks = [
            self.supporter.generate_summary(self.topic),
            self.opposer.generate_summary(self.topic),
        ]
        reflection_tasks = [
            self.supporter.generate_reflective_analysis(self.topic),
            self.opposer.generate_reflective_analysis(self.topic),
        ]

        summaries = await asyncio.gather(*summary_tasks)
        reflections = await asyncio.gather(*reflection_tasks)

        participant_summaries = {self.supporter.name: summaries[0], self.opposer.name: summaries[1]}

        reflective_analysis = {
            self.supporter.name: reflections[0],
            self.opposer.name: reflections[1],
        }
        print("✅ Summaries and reflections generated.")

        # Determine winner
        winner = self._determine_winner(scores)

        # Create final termination record if not already set (successful completion)
        if not termination_record:
            termination_record = DebateTermination(
                terminated=False,
                reason="completed",
                round_number=num_rounds,
                message="Debate completed successfully",
            )

        result = DebateResult(
            topic=self.topic,
            arguments=self.arguments,
            scores=scores,
            winner=winner,
            timestamp=datetime.now().isoformat(),
            num_rounds=termination_record.round_number,
            participants={
                self.organizer.name: self.organizer.get_role(),
                self.supporter.name: self.supporter.get_role(),
                self.opposer.name: self.opposer.get_role(),
                self.judge.name: self.judge.get_role(),
            },
            termination=termination_record,
            participant_summaries=participant_summaries,
            reflective_analysis=reflective_analysis,
            baseline=baseline,
        )

        logger.info(f"Debate completed. Winner: {winner}. Termination: {termination_record.reason}")
        print(f"\n🏆 Debate Finished! Winner: {winner if winner else 'Tie'}")
        return result

    async def _run_organizer_round(self) -> None:
        """Run organizer's overview round asynchronously."""
        logger.debug("Running organizer round")

        overview = await self.organizer.generate_overview(self.topic)

        arg = Argument(
            round_number=0,
            participant_name=self.organizer.name,
            participant_role="organizer",
            content=overview,
            timestamp=datetime.now().isoformat(),
            word_count=self.organizer.count_words(overview),
        )
        self.arguments.append(arg)

    async def _run_debate_round(self, round_num: int, is_first_round: bool) -> DebateTermination | None:
        """
        Run a single debate round with both debaters asynchronously.

        Returns:
            DebateTermination if debate should stop, None otherwise
        """
        logger.debug(f"Running debate round {round_num}")

        # 1. Calculate intermediate scores for strategic adaptation
        # For scoring purposes, we consider it 'initial' if it's the first round
        supporter_score, opposer_score = await self._get_intermediate_scores(round_num, is_first_round)

        # 2. Supporter's turn (Truly initial ONLY in round 1)
        termination = await self._process_debater_turn(
            self.supporter, self.opposer, round_num, is_first_round, supporter_score, opposer_score
        )
        if termination:
            return termination

        # 3. Opposer's turn (NEVER initial, always a rebuttal to supporter)
        termination = await self._process_debater_turn(
            self.opposer, self.supporter, round_num, False, opposer_score, supporter_score
        )
        if termination:
            return termination

        return None

    async def _get_intermediate_scores(self, round_num: int, is_initial: bool) -> tuple[float | None, float | None]:
        supporter_score = None
        opposer_score = None

        if not is_initial and round_num > 1:
            try:
                intermediate_scores = await self.judge.score_debate(self.topic, self.arguments)
                for score in intermediate_scores:
                    if score.debater_role == "supporter":
                        supporter_score = score.overall_score
                    elif score.debater_role == "opposer":
                        opposer_score = score.overall_score
                logger.info(f"Intermediate scores - Supporter: {supporter_score:.1f}, Opposer: {opposer_score:.1f}")
            except Exception:
                logger.exception("Failed to calculate intermediate scores")

        return supporter_score, opposer_score

    async def _process_debater_turn(
        self,
        debater: Debater,
        opponent: Debater,
        round_num: int,
        is_initial: bool,
        own_score: float | None,
        opponent_score: float | None,
    ) -> DebateTermination | None:
        """Process a single debater's turn including generation, validation, and storage asynchronously."""

        # Generate argument
        if is_initial:
            content = await debater.generate_argument(self.topic, round_num, is_initial=True)
        else:
            content = await debater.generate_argument(
                self.topic,
                round_num,
                is_initial=False,
                own_score=own_score,
                opponent_score=opponent_score,
            )

        # Validate quality
        if not is_initial:
            is_valid, reason = await debater.validate_argument_quality(self.topic, content)
            if not is_valid:
                logger.warning(f"{debater.name} argument validation failed: {reason}")
                termination = DebateTermination(
                    terminated=True,
                    reason="low_quality",
                    round_number=round_num,
                    debater_name=debater.name,
                    message=reason,
                )
                return termination

        # Evaluate opponent's latest argument (if not initial)
        valid_points = None
        weaknesses = None
        if not is_initial:
            opponent_args = [arg for arg in self.arguments if arg.participant_role == opponent.get_role()]
            if opponent_args:
                valid_points, weaknesses = await debater.evaluate_opponent_argument(
                    self.topic, opponent_args[-1].content
                )

        # Create and store argument object
        # Parallelize gap analysis with other tasks if needed, but for now just await
        gaps = None
        if not is_initial:
            gaps = await debater.analyze_opponent_arguments(
                self.topic,
                [arg.content for arg in self.arguments if arg.participant_role == opponent.get_role()],
            )

        arg_obj = Argument(
            round_number=round_num,
            participant_name=debater.name,
            participant_role=debater.get_role(),
            content=content,
            timestamp=datetime.now().isoformat(),
            word_count=debater.count_words(content),
            gaps_identified=gaps,
            acknowledged_valid_points=valid_points,
            identified_weaknesses=weaknesses,
        )

        # Update histories and session
        debater.add_own_argument(content, round_num)
        opponent.add_opponent_argument(content, round_num)
        self.arguments.append(arg_obj)

        return None

    async def _run_judge_evaluation(self) -> list[Score]:
        """
        Run judge evaluation asynchronously.

        Returns:
            List of scores
        """
        logger.debug("Running judge evaluation")
        return await self.judge.score_debate(self.topic, self.arguments)

    def _determine_winner(self, scores: list[Score]) -> str | None:
        if len(scores) < 2:
            return None

        best = max(scores, key=lambda s: s.overall_score)
        runner_up = min(scores, key=lambda s: s.overall_score)

        if best.overall_score > runner_up.overall_score:
            return best.debater_role
        return None
