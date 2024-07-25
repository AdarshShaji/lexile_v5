import psycopg2
from psycopg2.extras import Json
from config import EVALUATION_FACTORS, DB_CONFIG
from lexile import get_initial_lexile

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="lexile-database",
        user="postgres",
        password="adarsh123"
    )

def initialize_database():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Drop existing tables
        #cur.execute("DROP TABLE IF EXISTS evaluation_factors, questions, sessions, users CASCADE")
        
        # Create users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INTEGER,
            password VARCHAR(255),
            lexile_level INTEGER
        )
        """)
        
        # Create sessions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            topic VARCHAR(100),
            lexile_level INTEGER,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create questions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES sessions(id),
            question_text TEXT,
            options JSONB,
            correct_answer CHAR(1),
            evaluation_factor VARCHAR(100),
            user_answer CHAR(1)
        )
        """)
        
        # Create evaluation_factors table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_factors (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            factor VARCHAR(100),
            score INTEGER DEFAULT 0
        )
        """)
        
        conn.commit()
        print("Database initialized successfully.")
        
        # Verify tables were created
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cur.fetchall()
        print("Tables in the database:", [table[0] for table in tables])
        
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")

def get_user(user_id, password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, name, age, lexile_level FROM users WHERE id = %s AND password = %s", (user_id, password))
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if user:
        return {"id": user[0], "name": user[1], "age": user[2], "lexile_level": user[3]}
    return None

def create_user(name, age, password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    lexile_level = get_initial_lexile(age)
    cur.execute("INSERT INTO users (name, age, password, lexile_level) VALUES (%s, %s, %s, %s) RETURNING id", (name, age, password, lexile_level))
    user_id = cur.fetchone()[0]
    
    for factor in EVALUATION_FACTORS:
        cur.execute("INSERT INTO evaluation_factors (user_id, factor) VALUES (%s, %s)", (user_id, factor))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return user_id, lexile_level

# def get_or_create_user(name, age, student_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
    
#     cur.execute("SELECT id, lexile_level FROM users WHERE student_id = %s", (student_id,))
#     user = cur.fetchone()
    
#     if user:
#         user_id, lexile_level = user
#         cur.execute("UPDATE users SET name = %s, age = %s WHERE id = %s", (name, age, user_id))
#         created = False
#     else:
#         lexile_level = get_initial_lexile(age)
#         cur.execute("INSERT INTO users (name, age, student_id, lexile_level) VALUES (%s, %s, %s, %s) RETURNING id", (name, age, student_id, lexile_level))
#         user_id = cur.fetchone()[0]
#         created = True
        
#         for factor in EVALUATION_FACTORS:
#             cur.execute("INSERT INTO evaluation_factors (user_id, factor) VALUES (%s, %s)", (user_id, factor))
    
#     conn.commit()
#     cur.close()
#     conn.close()
    
#     return user_id, created, lexile_level

def save_session_and_questions(user_id, topic, lexile_level, content, questions):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if the user exists
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise ValueError(f"User with id {user_id} does not exist")
    
    cur.execute("INSERT INTO sessions (user_id, topic, lexile_level, content) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, topic, lexile_level, content))
    session_id = cur.fetchone()[0]
    
    for q in questions:
        cur.execute("INSERT INTO questions (session_id, question_text, options, correct_answer, evaluation_factor) VALUES (%s, %s, %s, %s, %s)",
                    (session_id, q['text'], Json(q['options']), q['correct_answer'], q['evaluation_factor']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return session_id

def update_user_answers_and_factors(user_id, session_id, user_answers):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, correct_answer, evaluation_factor FROM questions WHERE session_id = %s", (session_id,))
    questions = cur.fetchall()
    
    for (question_id, correct_answer, factor), user_answer in zip(questions, user_answers):
        cur.execute("UPDATE questions SET user_answer = %s WHERE id = %s", (user_answer, question_id))
        
        score_change = 1 if user_answer == correct_answer else -1
        cur.execute("UPDATE evaluation_factors SET score = score + %s WHERE user_id = %s AND factor = %s",
                    (score_change, user_id, factor))
    
    conn.commit()
    cur.close()
    conn.close()

def update_user_lexile_level(user_id, lexile_level):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE users SET lexile_level = %s WHERE id = %s", (lexile_level, user_id))
    
    conn.commit()
    cur.close()
    conn.close()

def get_evaluation_scores(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT factor, score FROM evaluation_factors WHERE user_id = %s", (user_id,))
    scores = dict(cur.fetchall())
    
    cur.close()
    conn.close()
    
    return scores