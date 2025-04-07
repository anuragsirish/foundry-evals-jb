# genai-evals

Evaluating Gen AI responses for quality and consistency.

![Azure AI Foundry Evaluations](images/ai-foundry-evals.jpg)

## Overview

This project demonstrates how to evaluate responses from Generative AI models using various evaluators, such as content safety, relevance, and friendliness. The evaluations are powered by Azure AI services and follow best practices for secure configuration and deployment.

## Setup

1. **Environment Variables**:  
   Ensure you have a `.env` file in the project root containing all required keys and endpoints (e.g., `AZURE_OPENAI_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, etc.). This file is used to securely store sensitive credentials.

2. **Dependencies**:  
   Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Evaluations**:  
   Open the provided Jupyter notebooks in Visual Studio Code to run the evaluation examples. The notebooks include step-by-step instructions on configuring and executing the evaluations.

## Project Structure

- **genai_evals.ipynb**: Main notebook for Azure OpenAI configuration and evaluation setup.  
- **custom_evaluator (1).ipynb**: Example custom evaluation (e.g., friendliness evaluation).  
- **.env**: Environment file containing all sensitive configuration information.  
- **images/**: Folder containing project-related images and diagrams.

## Business Use Cases

- **Quality Assurance**: Verify that AI-generated responses meet business standards.  
- **Compliance**: Ensure all responses follow regulatory and ethical guidelines.  
- **Customer Engagement**: Enhance customer experience by analyzing and improving AI interactions.

For further details, refer to the inline documentation within the notebooks.

## License

[Add your license details here]

## Contact

For support or inquiries, please contact [Your Name](mailto:your.email@example.com).