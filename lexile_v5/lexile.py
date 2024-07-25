import random
from config import AGE_TO_LEXILE, EVALUATION_FACTORS

def get_initial_lexile(age):
    for age_range, lexile_range in AGE_TO_LEXILE.items():
        if age in age_range:
            return random.randint(lexile_range[0], lexile_range[1])
    return 500  # Default value if age is out of all ranges

def adjust_lexile_level(current_lexile, scores):
    correct_answers = sum(1 for score in scores.values() if score > 0)
    if correct_answers >= 3:
        return current_lexile + 25
    elif correct_answers <= 2:
        return max(0, current_lexile - 25)
    return current_lexile

def display_lexile_scale(current_lexile):
    scale = list(range(max(0, current_lexile - 500), current_lexile + 50, 50))
    scale_str = " ".join([f"[{level}L]" if level == current_lexile else f"{level}L" for level in scale])
    return scale_str

def evaluate_answers(questions, user_answers):
    scores = {factor: 0 for factor in EVALUATION_FACTORS}
    for q, answer in zip(questions, user_answers):
        factor = q["evaluation_factor"]
        if factor in scores:
            scores[factor] += 1 if answer == q["correct_answer"] else -1
    return scores