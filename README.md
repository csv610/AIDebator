# AI Debate 

This project is an **AI-powered debate platform** that allows users to simulate debates between different language models (LLMs), such as OpenAI's GPT and LLaMA. The platform lets users select a topic, choose AI models for the supporting and opposing sides, and even assign a model to act as the judge, providing a final judgment based on the quality of arguments.

## Features

- **Model Agnostic**: Supports multiple language models (OpenAI, LLaMA, etc.) with the flexibility to add more.
- **Customizable Arguments**: Users can control the randomness (`temperature`) and response length (`max_tokens`) for AI-generated arguments.
- **Modular Design**: Easily switch between different AI models via a factory pattern.
- **Multi-Round Debates**: Conduct debates with multiple rounds between supporting and opposing debators.
- **Judge Evaluation**: An AI judge model evaluates the arguments based on relevancy, accuracy, bias, and factual information, and provides a final decision.

## Setup

### Prerequisites

- Python 3.7 or higher
- [OpenAI API Key](https://beta.openai.com/signup/)
- [Ollama](https://ollama.ai/) for running local LLaMA models

### Install Dependencies

Clone the repository and install the required packages:

```bash
git clone https://github.com/your-username/ai-debate-platform.git
cd ai-debate-platform
pip install -r requirements.txt

### Running the App

1. **Set up OpenAI API key** (if using OpenAI models):  
   Get your OpenAI API key from [OpenAI's website](https://beta.openai.com/signup/) and enter it into the application when prompted.

2. **Start the Streamlit app**:
   ```bash
   streamlit run app.py






## Usage

1. **Select Debate Models**: You can choose different models (OpenAI, LLaMA) for the supporting and opposing debators.
2. **Input a Debate Topic**: Provide a topic for the debate, and the selected AI models will generate arguments.
3. **Adjust Parameters**: Control `temperature` and `max_tokens` to adjust the creativity and response length of the models.
4. **Conduct Debate**: The debate takes place over multiple rounds, with AI models responding to each other.
5. **Final Judgment**: After all rounds are complete, the AI judge evaluates the arguments based on multiple criteria and provides a final verdict.


## Example

Here's a brief walkthrough:

1. **Enter Topic**:  
   "The impact of AI on human jobs"

2. **Choose Models**:  
   Select OpenAI for the supporting debator and LLaMA for the opposing debator. Select another model for the judge (or use the same).

3. **Adjust Parameters**:  
   Set temperature to 0.7 for creativity, and max tokens to 1024 for detailed responses.

4. **Start the Debate**:  
   The models will generate arguments and rebuttals for multiple rounds.

5. **Judge's Decision**:  
   After the debate, the judge model will evaluate the arguments and declare a winner based on relevancy, accuracy, bias, and factual correctness.


