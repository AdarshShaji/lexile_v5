# config.py

# Evaluation factors for assessing reading skills
EVALUATION_FACTORS = [
    "Reading Comprehension", "Vocabulary", "Inference Skills", "Main Idea Identification",
    "Detail Identification", "Author's Purpose", "Text Structure", "Literary Elements",
    "Summarization", "Comparing and Contrasting", "Fact vs. Opinion", "Cause and Effect",
    "Figurative Language", "Point of View", "Critical Thinking", "Context Clues",
    "Sequential Order", "Paraphrasing", "Identifying Supporting Details", "Understanding Dialogue",
    "Making Predictions", "Analyzing Tone and Mood", "Interpreting Graphical Information",
    "Recognizing Themes", "Analyzing Arguments", "Synthesizing Information"
]

# Available topics for content generation
TOPICS = [
    "Science and Technology", "History and Culture", "Nature and Environment",
    "Sports and Fitness", "Arts and Literature", "Space and Astronomy",
    "Animals and Wildlife", "World Geography", "Famous People and Biographies",
    "Mythology and Folklore", "Inventions and Discoveries", "Music and Entertainment",
    "Food and Nutrition", "Human Body and Health", "Computers and Coding"
]

# Age to initial Lexile level mapping
AGE_TO_LEXILE = {
    range(5, 8): (200, 500),
    range(8, 10): (400, 700),
    range(10, 12): (600, 900),
    range(12, 14): (800, 1100),
    range(14, 16): (1000, 1300),
    range(16, 19): (1200, 1600)
}

# Predefined Lexile scales
LEXILE_SCALES = [
    "200L-400L", "400L-600L", "600L-800L", "800L-1000L",
    "1000L-1200L", "1200L-1400L", "1400L-1600L"
]

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "lexile-database",
    "user": "postgres",
    "password": "adarsh123"
}

# API configuration
API_KEY = "AIzaSyDmf0d09V7jGsuN-kfZ6Di-bF0LbCyH7_I"
MODEL_NAME = "gemini-1.0-pro"

# Content generation settings
MIN_CONTENT_WORDS = 100
NUM_QUESTIONS = 5

# Lexile adjustment settings
LEXILE_INCREASE = 25
LEXILE_DECREASE = 25
CORRECT_ANSWERS_THRESHOLD = 3