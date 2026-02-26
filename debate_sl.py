"""
Streamlit UI for Multi-Participant AI Debate Platform.

This module provides the web interface for the debate platform, allowing users
to configure and run debates with different LLM models.

The core debate logic is imported from src.debate module.
"""

import streamlit as st
from src.debate import (
    Organizer,
    Debater,
    Judge,
    DebateSession,
    DebateResult,
    DebateConfig
)
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Debate Platform",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .debate-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# UI FUNCTIONS
# ============================================================================

def display_argument(argument) -> None:
    """Display a single argument."""
    with st.container():
        col1, col2 = st.columns([1, 4])

        with col1:
            st.caption(f"**{argument.participant_name}**")
            st.caption(f"Round {argument.round_number}")
            st.caption(f"📝 {argument.word_count} words")

        with col2:
            st.write(argument.content)

        # Display gaps identified
        if argument.gaps_identified:
            with st.expander("🎯 Gaps Identified in Opponent"):
                for gap in argument.gaps_identified:
                    st.write(f"• {gap}")

        # Display acknowledged valid points
        if argument.acknowledged_valid_points:
            with st.expander("✅ Valid Points Acknowledged from Opponent"):
                for point in argument.acknowledged_valid_points:
                    st.write(f"• {point}")

        # Display identified weaknesses
        if argument.identified_weaknesses:
            with st.expander("⚠️  Weaknesses Identified in Opponent"):
                for weakness in argument.identified_weaknesses:
                    st.write(f"• {weakness}")

        st.divider()


def display_score(score) -> None:
    """Display a single score."""
    with st.expander(f"**{score.debater_role.title()}** - Score: {score.overall_score:.1f}/10"):
        # Main metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Argument Quality", f"{score.argument_quality:.1f}")
        with col2:
            st.metric("Evidence Quality", f"{score.evidence_quality:.1f}", delta="CRITICAL")
        with col3:
            st.metric("Logical Consistency", f"{score.logical_consistency:.1f}")
        with col4:
            st.metric("Responsiveness", f"{score.responsiveness_to_gaps:.1f}")
        with col5:
            st.metric("Overall Score", f"{score.overall_score:.1f}")

        # Evidence and facts summary
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"📊 **Facts & Citations**: {score.fact_count}")
        with col_b:
            st.info(f"✓ **Evidence-Backed Arguments**: {score.irrefutable_arguments}")

        st.write("**Judge's Feedback:**")
        st.write(score.feedback)


def display_debate_result(result: DebateResult) -> None:
    """Display complete debate result."""
    st.header("📊 Debate Result")

    # Winner announcement
    if result.winner:
        winner_score = [s.overall_score for s in result.scores if s.debater_role == result.winner][0]
        st.success(f"🏆 **Winner: {result.winner.title()}** with score {winner_score:.1f}/10")
    else:
        st.info("⚖️ **Debate Result: TIE** - Both debaters presented equally compelling arguments")

    # Termination status
    if result.termination:
        if result.termination.terminated and result.termination.reason != "completed":
            st.warning(f"⛔ **Debate Terminated** (Round {result.termination.round_number})")
            st.write(f"**Reason**: {result.termination.reason.replace('_', ' ').title()}")
            if result.termination.debater_name:
                st.write(f"**Debater**: {result.termination.debater_name}")
            if result.termination.message:
                st.write(f"**Details**: {result.termination.message}")
        else:
            st.info(f"✅ **Debate Status**: Completed successfully ({result.num_rounds} rounds)")

    st.divider()

    # Argument history
    st.header("📚 Argument History")

    # Organizer's overview
    organizer_arg = [arg for arg in result.arguments if arg.participant_role == "organizer"]
    if organizer_arg:
        st.subheader("🎤 Organizer's Overview")
        display_argument(organizer_arg[0])

    # Debate rounds
    for round_num in range(1, result.num_rounds + 1):
        st.subheader(f"Round {round_num}")

        round_args = [arg for arg in result.arguments if arg.round_number == round_num]
        for arg in round_args:
            display_argument(arg)

    st.divider()

    # Judge's evaluation
    st.header("🏛️ Judge's Evaluation")

    for score in result.scores:
        display_score(score)

    st.divider()

    # Download transcript
    st.header("📥 Download Transcript")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📋 Download as JSON",
            data=result.to_json(indent=2),
            file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    with col2:
        # CSV export
        csv_data = []
        for arg in result.arguments:
            csv_data.append({
                "Round": arg.round_number,
                "Participant": arg.participant_name,
                "Role": arg.participant_role,
                "Word Count": arg.word_count,
                "Content": arg.content[:100] + "..."
            })

        import pandas as pd
        df = pd.DataFrame(csv_data)

        st.download_button(
            label="📊 Download as CSV",
            data=df.to_csv(index=False),
            file_name=f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function."""
    st.title("🎭 Multi-Participant AI Debate Platform")

    # Initialize session state
    if "debate_result" not in st.session_state:
        st.session_state.debate_result = None
    if "debate_running" not in st.session_state:
        st.session_state.debate_running = False

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Debate Configuration")

        # Topic
        topic = st.text_area(
            "📌 Debate Topic",
            height=100,
            placeholder="Enter the topic for debate..."
        )

        st.subheader("🤖 LLM Model Selection")

        organizer_model = st.text_input(
            "Organizer's Model",
            value="ollama/gemma3:latest",
            help="Examples: gpt-4o, claude-3-opus-20240229, ollama/llama2"
        )

        supporter_model = st.text_input(
            "Supporter's Model",
            value="ollama/gemma3:latest"
        )

        supporter_persona = st.text_area(
            "Supporter's Persona",
            value="An expert in the field with a positive outlook on the topic.",
            help="Describe the expert perspective this debater should take."
        )

        opposer_model = st.text_input(
            "Opposer's Model",
            value="ollama/gemma3:latest"
        )

        opposer_persona = st.text_area(
            "Opposer's Persona",
            value="A critical analyst focusing on risks and potential downsides.",
            help="Describe the expert perspective this debater should take."
        )

        judge_model = st.text_input(
            "Judge's Model",
            value="ollama/gemma3:latest"
        )

        st.subheader("📊 Debate Settings")

        num_rounds = st.slider(
            "Number of Rounds",
            min_value=1,
            max_value=10,
            value=3
        )

        st.divider()

        # Start debate button
        start_button = st.button(
            "🎬 Start Debate",
            type="primary",
            use_container_width=True
        )

        if start_button:
            if not topic:
                st.error("❌ Please enter a debate topic")
            else:
                st.session_state.debate_running = True

                # Create debate session
                config = DebateConfig(
                    topic=topic,
                    organizer_model=organizer_model,
                    supporter_model=supporter_model,
                    supporter_persona=supporter_persona,
                    opposer_model=opposer_model,
                    opposer_persona=opposer_persona,
                    judge_model=judge_model,
                    num_rounds=num_rounds
                )
                debate = DebateSession.from_config(config)

                # Run debate with progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.info("Starting debate...")
                    progress_bar.progress(10)

                    status_text.info("Generating organizer overview...")
                    progress_bar.progress(20)

                    result = debate.run(num_rounds=num_rounds)

                    progress_bar.progress(100)
                    status_text.success("✅ Debate completed!")

                    st.session_state.debate_result = result
                    st.session_state.debate_running = False

                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Error during debate: {str(e)}")
                    st.session_state.debate_running = False

    # Main content area
    if st.session_state.debate_result:
        display_debate_result(st.session_state.debate_result)
    else:
        st.info(
            "👈 Configure your debate in the sidebar and click 'Start Debate' to begin. "
            "Make sure you have set up your API keys in the environment variables."
        )

        # Display example configuration
        with st.expander("📖 Example Configuration"):
            st.write("""
            **Topic:** "Artificial Intelligence will have a net positive impact on employment"

            **Models:**
            - Organizer: gpt-4
            - Supporter: claude-3-opus-20240229
            - Opposer: ollama/llama2
            - Judge: gpt-4

            **Names:**
            - Organizer: Moderator
            - Supporter: Dr. Alice (Pro-AI)
            - Opposer: Prof. Bob (Skeptical)
            - Judge: Judge Panel

            **Rounds:** 3
            """)

        # Display setup instructions
        with st.expander("🔧 Setup Instructions"):
            st.write("""
            ### Prerequisites
            1. Python 3.8+ installed
            2. Required packages: `pip install -r requirements.txt`
            3. API keys configured as environment variables:
               - `OPENAI_API_KEY` for OpenAI models
               - `ANTHROPIC_API_KEY` for Claude models
               - Or any other LLM provider supported by litellm

            ### Environment Setup
            Create a `.env` file in the project root:
            ```
            OPENAI_API_KEY=your_key_here
            ANTHROPIC_API_KEY=your_key_here
            ```

            ### Running the App
            ```bash
            streamlit run app.py
            ```

            ### Model Examples
            - **OpenAI:** gpt-4, gpt-3.5-turbo
            - **Anthropic:** claude-3-opus-20240229, claude-3-sonnet-20240229
            - **Ollama:** ollama/llama2, ollama/mistral
            - **Google:** gemini-pro
            """)


if __name__ == "__main__":
    main()
