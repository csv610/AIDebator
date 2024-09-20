import streamlit as st
import ollama
import json
import random
import re

OLLAMA_API_BASE = "http://localhost:11434/api"
WORD_LIMIT = 2000

st.set_page_config(layout="wide")

class Argument:
    def __init__(self, model, content, is_supporting, truncated=False):
        self.model = model
        self.content = content
        self.is_supporting = is_supporting
        self.is_winning = None
        self.truncated = truncated

def get_model_response(model, topic, opponent_argument, is_supporting, is_rebuttal=False):
    position = "supporting" if is_supporting else "opposing"
    if is_rebuttal:
        task = f"""Provide a scholarly rebuttal to the opponent's argument while {position} the topic. 
        Your response should:
        1. Critically analyze the opponent's argument, identifying strengths and weaknesses.
        2. Present counter-arguments supported by academic research and established theories.
        3. Cite relevant studies, papers, or authoritative sources (use format: (Author, Year)).
        4. Consider potential limitations or counterarguments to your own position.
        If you cannot find a rational, evidence-based counter-argument, admit that you cannot continue the debate."""
    else:
        task = f"""Provide a scholarly argument {position} the topic. 
        Your response should:
        1. Present a clear thesis statement.
        2. Develop your argument with logical reasoning and evidence from academic sources.
        3. Cite relevant studies, papers, or authoritative sources (use format: (Author, Year)).
        4. Address potential counterarguments and limitations of your position.
        Base your argument on established research and critical thinking."""

    full_prompt = f"""Topic: {topic}
Your position: {position} the topic
Opponent's argument: {opponent_argument}
Your task: {task}
IMPORTANT: 
- Limit your response to {WORD_LIMIT} words or fewer.
- Structure your response with clear introduction, body, and conclusion.
- Use formal academic language appropriate for a scholarly debate.
Your response:"""
    
    # Use the ollama package to get the model response
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': full_prompt}])
    return response['message']['content']

def truncate_to_word_limit(text, limit):
    words = text.split()
    if len(words) <= limit:
        return text, False
    return ' '.join(words[:limit]), True

def check_conclusion(response):
    conclusion_phrases = [
        "I cannot continue the debate",
        "I don't have a rational counter-argument",
        "I concede the point",
        "I admit I can't refute this argument",
        "The evidence does not support further argumentation"
    ]
    return any(phrase.lower() in response.lower() for phrase in conclusion_phrases)

def debate_round(topic, model1, model2, model1_supports, round_number, arguments):
    st.subheader(f"Round {round_number}")
    
    # Model 1's turn
    st.write(f"{model1}'s {'supporting' if model1_supports else 'opposing'} argument:")
    with st.spinner(f"Waiting for {model1}'s response..."):
        model1_argument = get_model_response(model1, topic, arguments[-1].content if arguments else "", model1_supports, bool(arguments))
    model1_argument, model1_truncated = truncate_to_word_limit(model1_argument, WORD_LIMIT)
    st.write(model1_argument)
    arguments.append(Argument(model1, model1_argument, model1_supports, model1_truncated))
    
    if model1_truncated:
        st.warning(f"{model1}'s response was truncated to {WORD_LIMIT} words.")
    if check_conclusion(model1_argument):
        st.success(f"Debate concluded: {model1} could not provide a rational, evidence-based counter-argument.")
        arguments[-1].is_winning = False
        arguments[-2].is_winning = True if len(arguments) > 1 else None
        return True
    
    # Model 2's turn
    st.write(f"{model2}'s {'opposing' if model1_supports else 'supporting'} counter-argument:")
    with st.spinner(f"Waiting for {model2}'s response..."):
        model2_argument = get_model_response(model2, topic, model1_argument, not model1_supports, True)
    model2_argument, model2_truncated = truncate_to_word_limit(model2_argument, WORD_LIMIT)
    st.write(model2_argument)
    arguments.append(Argument(model2, model2_argument, not model1_supports, model2_truncated))
    
    if model2_truncated:
        st.warning(f"{model2}'s response was truncated to {WORD_LIMIT} words.")
    if check_conclusion(model2_argument):
        st.success(f"Debate concluded: {model2} could not provide a rational, evidence-based counter-argument.")
        arguments[-1].is_winning = False
        arguments[-2].is_winning = True
        return True
    
    return False

def extract_citations(text):
    return re.findall(r'\((?:\w+(?:,\s\w+)*,\s\d{4}(?:;\s)?)+\)', text)

def summarize_arguments_by_model(arguments, model1, model2):
    model1_summary = [arg.content for arg in arguments if arg.model == model1]
    model2_summary = [arg.content for arg in arguments if arg.model == model2]
    
    st.subheader(f"Summary of {model1}'s Arguments")
    for i, content in enumerate(model1_summary, 1):
        st.write(f"Round {i}: {content}")

    st.subheader(f"Summary of {model2}'s Arguments")
    for i, content in enumerate(model2_summary, 1):
        st.write(f"Round {i}: {content}")

def collect_citations(arguments):
    citations = []
    for arg in arguments:
        citations += extract_citations(arg.content)
    return citations

def generate_report(arguments, model1, model2, model1_supports):
    st.title("Debate Summary Report")
    
    supporting_model = model1 if model1_supports else model2
    opposing_model = model2 if model1_supports else model1
    
    supporting_wins = sum(1 for arg in arguments if arg.model == supporting_model and arg.is_winning)
    opposing_wins = sum(1 for arg in arguments if arg.model == opposing_model and arg.is_winning)
    
    st.write(f"Total arguments presented: {len(arguments)}")
    st.write(f"Supporting side ({supporting_model}) prevailed in {supporting_wins} exchanges")
    st.write(f"Opposing side ({opposing_model}) prevailed in {opposing_wins} exchanges")
    
    if supporting_wins > opposing_wins:
        st.write(f"Overall assessment: The supporting side ({supporting_model}) presented more compelling arguments.")
    elif opposing_wins > supporting_wins:
        st.write(f"Overall assessment: The opposing side ({opposing_model}) presented more compelling arguments.")
    else:
        st.write("Overall assessment: The debate resulted in a draw, with both sides presenting equally compelling arguments.")
    
    summarize_arguments_by_model(arguments, model1, model2)
    
    st.subheader("Collected Citations")
    citations = collect_citations(arguments)
    if citations:
        for citation in citations:
            st.write(f"- {citation}")
    else:
        st.write("No citations were provided during the debate.")

def get_available_models():
    models = ollama.list()

    # Extract model names
    model_names = [model['name'] for model in models['models']]
    
    return model_names

def main():
    st.title("AI Debate")

    available_models = get_available_models()

    topic = st.text_input("Enter the academic debate topic:")
    model1 = st.selectbox("Select Model 1 (Supporting) for the debate:", available_models, index=0)
    model2 = st.selectbox("Select Model 2 (Opposing) for the debate:", available_models, index=min(1, len(available_models)-1))
    max_rounds = st.number_input("Maximum number of debate rounds:", min_value=1, max_value=10, value=5)

    if st.button("Initiate Academic Debate"):
        if topic and model1 != model2:
            model1_supports = True  # model1 will support the topic, and model2 will oppose
            st.write(f"{model1} will present arguments supporting the topic.")
            st.write(f"{model2} will present arguments opposing the topic.")

            arguments = []
            for round in range(1, max_rounds + 1):
                debate_concluded = debate_round(topic, model1, model2, model1_supports, round, arguments)
                if debate_concluded:
                    break
                st.markdown("---")
            else:
                st.info(f"The debate reached the maximum number of rounds ({max_rounds}) without a definitive conclusion.")

            generate_report(arguments, model1, model2, model1_supports)
        elif not topic:
            st.warning("Please enter an academic debate topic to initiate the discussion.")
        else:
            st.warning("Please select different models for a balanced debate.")

if __name__ == "__main__":
    main()

