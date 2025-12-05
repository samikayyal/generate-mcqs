"""
Flask app to display MCQ quiz and show correct answers.
"""

import random
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "mcq-quiz-secret-key-change-in-production"


def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect("mcqs.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_all_questions():
    """Fetch all questions with their options from the database."""
    conn = get_db_connection()

    questions = conn.execute("SELECT * FROM questions ORDER BY question_id").fetchall()

    result = []
    for q in questions:
        options = conn.execute(
            "SELECT * FROM options WHERE question_id = ? ORDER BY option_id",
            (q["question_id"],),
        ).fetchall()
        result.append(
            {
                "question_id": q["question_id"],
                "text": q["text"],
                "options": [dict(o) for o in options],
            }
        )

    conn.close()
    return result


@app.route("/")
def index():
    """Start the quiz - redirect to first question."""
    session.clear()
    session["current_question"] = 0
    session["answers"] = {}
    session["wrong_questions"] = []
    # Shuffle all question IDs for initial quiz
    all_questions = get_all_questions()
    shuffled_ids = [q["question_id"] for q in all_questions]
    random.shuffle(shuffled_ids)
    session["question_ids"] = shuffled_ids
    return redirect(url_for("question"))


@app.route("/question", methods=["GET", "POST"])
def question():
    """Display current question and handle answer submission."""
    all_questions = get_all_questions()

    if not all_questions:
        return render_template("no_questions.html")

    # Filter questions if retrying wrong ones
    question_ids = session.get("question_ids")
    if question_ids:
        # Create a map for quick lookup and preserve order from question_ids
        q_map = {q["question_id"]: q for q in all_questions}
        questions = [q_map[qid] for qid in question_ids if qid in q_map]
    else:
        questions = all_questions

    if not questions:
        return render_template("no_questions.html")

    current_idx = session.get("current_question", 0)

    if current_idx >= len(questions):
        return redirect(url_for("results"))

    current_q = questions[current_idx]
    show_answer = session.get("show_answer", False)
    selected_option = session.get("selected_option")

    # Find correct option early so it's available in POST handling
    correct_option = None
    for opt in current_q["options"]:
        if opt["is_correct"]:
            correct_option = opt["option_id"]
            break

    if request.method == "POST":
        action = request.form.get("action")

        if action == "submit":
            # User submitted an answer
            selected = request.form.get("answer")
            if selected:
                session["selected_option"] = int(selected)
                session["show_answer"] = True
                # Store the answer
                answers = session.get("answers", {})
                answers[str(current_q["question_id"])] = int(selected)
                session["answers"] = answers
                # Update local variables to reflect the new state
                selected_option = int(selected)
                show_answer = True

        elif action == "next":
            # Track wrong answer before moving on
            if selected_option and selected_option != correct_option:
                wrong_questions = session.get("wrong_questions", [])
                if current_q["question_id"] not in wrong_questions:
                    wrong_questions.append(current_q["question_id"])
                    session["wrong_questions"] = wrong_questions
            # Move to next question
            session["current_question"] = current_idx + 1
            session["show_answer"] = False
            session["selected_option"] = None
            return redirect(url_for("question"))

    return render_template(
        "question.html",
        question=current_q,
        question_num=current_idx + 1,
        total_questions=len(questions),
        show_answer=show_answer,
        selected_option=selected_option,
        correct_option=correct_option,
    )


@app.route("/retry-wrong")
def retry_wrong():
    """Start a quiz with only the questions the user got wrong."""
    wrong_questions = session.get("wrong_questions", [])
    if not wrong_questions:
        return redirect(url_for("index"))

    # Keep wrong_questions for potential nested retries, reset other state
    session["current_question"] = 0
    session["answers"] = {}
    session["question_ids"] = wrong_questions
    session["wrong_questions"] = []  # Reset for this new attempt
    return redirect(url_for("question"))


@app.route("/results")
def results():
    """Show final quiz results."""
    all_questions = get_all_questions()
    answers = session.get("answers", {})
    wrong_questions = session.get("wrong_questions", [])

    # Filter questions if we were doing a retry
    question_ids = session.get("question_ids")
    if question_ids:
        # Create a map for quick lookup and preserve order from question_ids
        q_map = {q["question_id"]: q for q in all_questions}
        questions = [q_map[qid] for qid in question_ids if qid in q_map]
    else:
        questions = all_questions

    correct_count = 0
    question_results = []

    for q in questions:
        selected_id = answers.get(str(q["question_id"]))
        correct_option = None
        selected_option = None

        for opt in q["options"]:
            if opt["is_correct"]:
                correct_option = opt
            if opt["option_id"] == selected_id:
                selected_option = opt

        is_correct = selected_option and selected_option["is_correct"]
        if is_correct:
            correct_count += 1

        question_results.append(
            {
                "question": q,
                "selected": selected_option,
                "correct": correct_option,
                "is_correct": is_correct,
            }
        )

    return render_template(
        "results.html",
        results=question_results,
        correct_count=correct_count,
        total=len(questions),
        has_wrong_answers=len(wrong_questions) > 0,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
