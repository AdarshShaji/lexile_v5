from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import EVALUATION_FACTORS

api_key = "AIzaSyDmf0d09V7jGsuN-kfZ6Di-bF0LbCyH7_I"
llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-1.0-pro")

content_mcq_prompt_template = """
You are an AI assistant trained to generate educational content and multiple-choice questions (MCQs) for students.
Please generate a passage of at least 100 words suitable for a {age}-year-old student on the topic of {topic}. 
Then, create 5 multiple-choice questions based on this passage. Each question should evaluate a different skill from the following list:
{evaluation_factors}

The questions should be challenging but appropriate for the age group.

Format your response as follows:
Content:
[Your generated content here]

Questions:
1. [Question 1]
   a) [Option A]
   b) [Option B]
   c) [Option C]
   d) [Option D]
   Correct Answer: [Correct option letter]
   Evaluation Factor: [Relevant evaluation factor from the list]

[Repeat for questions 2-5]

Generated Content and Questions:
"""

content_mcq_prompt = PromptTemplate(
    template=content_mcq_prompt_template,
    input_variables=["age", "topic", "evaluation_factors"]
)

content_mcq_chain = LLMChain(llm=llm, prompt=content_mcq_prompt)

# content_generation.py

def generate_content_and_mcqs(age, topic):
    result = content_mcq_chain.run(age=age, topic=topic, evaluation_factors=", ".join(EVALUATION_FACTORS))
    
    try:
        content, questions_raw = result.split("Questions:", 1)
    except ValueError:
        return None, None

    content = content.replace("Content:", "").strip()
    questions_raw = questions_raw.strip().split("\n\n")
    questions = []

    for q in questions_raw:
        lines = q.split("\n")
        if len(lines) < 6:
            continue
        
        try:
            question = {
                "text": lines[0].split(". ", 1)[1] if ". " in lines[0] else lines[0],
                "options": [line.strip()[3:] for line in lines[1:5]],  # Remove the a), b), c), d) prefixes
                "correct_answer": lines[5].split(": ")[1] if ": " in lines[5] else "",
                "evaluation_factor": lines[6].split(": ")[1] if ": " in lines[6] else ""
            }
            questions.append(question)
        except IndexError:
            continue

    if not questions:
        return None, None

    return content, questions