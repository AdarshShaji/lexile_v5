# main.py

import streamlit as st
from database import initialize_database, create_user, get_user, save_session_and_questions, update_user_answers_and_factors, get_evaluation_scores, update_user_lexile_level
from lexile import get_initial_lexile, adjust_lexile_level, display_lexile_scale, evaluate_answers
from content_generation import generate_content_and_mcqs
from config import TOPICS, LEXILE_SCALES

def main():
    st.title("Lexile Evaluation App")

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'current_lexile' not in st.session_state:
        st.session_state.current_lexile = None
    if 'content' not in st.session_state:
        st.session_state.content = None
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'age' not in st.session_state:
        st.session_state.age = None

    # Login Page
    if st.session_state.page == 'login':
        st.header("Student Login")
        user_id = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if user_id and password:
                user = get_user(user_id, password)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.age = user['age']
                    st.session_state.current_lexile = user['lexile_level']
                    st.session_state.page = 'main'
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid ID or password. Please try again.")
            else:
                st.error("Please fill in all fields.")
        
        if st.button("Create New Account"):
            st.session_state.page = 'create_account'
            st.experimental_rerun()
    
    # Create Account Page
    elif st.session_state.page == 'create_account':
        st.header("Create New Account")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=5, max_value=18, value=10)
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Create Account"):
            if name and age and password and confirm_password:
                if password == confirm_password:
                    user_id, lexile_level = create_user(name, age, password)
                    st.session_state.user_id = user_id
                    st.session_state.age = age
                    st.session_state.current_lexile = lexile_level
                    st.session_state.page = 'main'
                    st.success("Account created successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Passwords do not match. Please try again.")
            else:
                st.error("Please fill in all fields.")
        
        if st.button("Back to Login"):
            st.session_state.page = 'login'
            st.experimental_rerun()

    # Main Page
    elif st.session_state.page == 'main':
        tab1, tab2 = st.tabs(["Dashboard", "Lexile Test"])

        with tab1:
            st.header("Dashboard")
            st.write(f"Current Lexile Level: {st.session_state.current_lexile}L")
            st.text(display_lexile_scale(st.session_state.current_lexile))
            
            st.subheader("Evaluation Scores:")
            scores = get_evaluation_scores(st.session_state.user_id)
            for factor, score in scores.items():
                st.write(f"{factor}: {score}")

        with tab2:
            st.header("Lexile Test")
            
            # Topic selection
            topic = st.selectbox("Select a topic", TOPICS)
            
            # Lexile scale selection
            lexile_scale = st.selectbox("Select Lexile Scale", LEXILE_SCALES)

            # Generate new content and questions
            if st.button("Generate New Content and Questions"):
                with st.spinner("Generating content and questions..."):
                    st.session_state.content, st.session_state.questions = generate_content_and_mcqs(st.session_state.age, topic)
                
                    if st.session_state.content is None or st.session_state.questions is None:
                        st.error("Failed to generate content and questions. Please try again.")
                    else:
                        # Save session and questions to database
                        if st.session_state.user_id:
                            st.session_state.session_id = save_session_and_questions(
                                st.session_state.user_id,
                                topic,
                                st.session_state.current_lexile,
                                st.session_state.content,
                                st.session_state.questions
                            )

            if st.session_state.content and st.session_state.questions:
                st.subheader("Generated Content:")
                st.write(st.session_state.content)

                st.subheader("Multiple Choice Questions:")
                user_answers = []
                for i, q in enumerate(st.session_state.questions, 1):
                    st.write(f"\n{i}. {q['text']}")
                    options = [f"{j+1}. {opt}" for j, opt in enumerate(q['options'])]
                    answer = st.radio(f"Question {i}", options=options, key=f"q{i}")
                    user_answers.append(str(options.index(answer) + 1))  # Store the number (1, 2, 3, or 4)
                
                if st.button("Submit Answers"):
                    scores = evaluate_answers(st.session_state.questions, user_answers)
                    
                    # Update user answers and evaluation factors in database
                    if st.session_state.user_id and st.session_state.session_id:
                        update_user_answers_and_factors(
                            st.session_state.user_id,
                            st.session_state.session_id,
                            user_answers
                        )
                    
                    new_lexile = adjust_lexile_level(st.session_state.current_lexile, scores)
                    if new_lexile > st.session_state.current_lexile:
                        st.success(f"Congratulations! Your Lexile Level has increased to {new_lexile}L")
                    elif new_lexile < st.session_state.current_lexile:
                        st.warning(f"Your Lexile Level has decreased to {new_lexile}L. Keep practicing!")
                    else:
                        st.info("Your Lexile Level remains the same. Keep up the good work!")

                    st.session_state.current_lexile = new_lexile
                    update_user_lexile_level(st.session_state.user_id, new_lexile)
                    st.write(f"Updated Lexile Level: {st.session_state.current_lexile}L")
                    st.text(display_lexile_scale(st.session_state.current_lexile))

                    st.subheader("Updated Evaluation Scores:")
                    updated_scores = get_evaluation_scores(st.session_state.user_id)
                    for factor, score in updated_scores.items():
                        st.write(f"{factor}: {score}")

        # Logout button
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

if __name__ == "__main__":
    initialize_database()
    main()