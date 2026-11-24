from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "change-this-to-a-long-random-secret"

import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
            )
    """)

    conn.commit()
    conn.close()


init_db()
QUESTIONS = [
    {
        "question": "What is 25% of 200?",
        "options": ["25", "40", "50", "75"],
        "answer": "50"
    },
    {
        "question": "Find the next number: 2, 4, 8, 16, ?",
        "options": ["20", "24", "30", "32"],
        "answer": "32"
    },
    {
        "question": "If 5 pens cost ₹50, what is the cost of 1 pen?",
        "options": ["₹5", "₹10", "₹15", "₹20"],
        "answer": "₹10"
    },
    {
        "question": "Which data structure follows FIFO?",
        "options": ["Stack", "Queue", "Tree", "Graph"],
        "answer": "Queue"
    },
    {
        "question": "What is 12 × 8?",
        "options": ["84", "92", "96", "108"],
        "answer": "96"
    }
]



@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
            content="width=device-width, initial-scale=1.0">
        <title>PrepPath - Placement Preparation</title>

        <link rel="stylesheet"
            href="{{ url_for('static', filename='css/style.css') }}">
    </head>

    <body>
        <nav class="navbar">
            <h2>PrepPath</h2>
            <div>
                <a href="/">Home</a>
                <a href="/dashboard">Dashboard</a>
                <a href="/quiz">Aptitude Quiz</a>
                <a href="/coding">Coding Resources</a>
                <a href="/technical">Technical Interview</a>
                <a href="/hr">HR Interview</a>
                <a href="/logout">Logout</a>
            </div>
        </nav>

        <section class="hero" id="home">
            <h1>Your journey to placement success starts here.</h1>

            <p>
                Practise aptitude, explore coding resources, and prepare
                for technical and HR interviews — all in one place.
            </p>

            <a class="btn" href="/quiz">Start Aptitude Quiz →</a>
        </section>

        <section class="section" id="features">
            <h2>Prepare for Your Dream Job</h2>
            <p class="subtitle">
                Build your skills one step at a time.
            </p>

            <div class="cards">

                <div class="card">
                    <div class="emoji">🧠</div>
                    <h3>Aptitude Practice</h3>
                    <p>Test your maths and logical reasoning skills.</p>
                    <a href="/quiz">Take the quiz →</a>
                </div>

                <div class="card">
                    <div class="emoji">💻</div>
                    <h3>Coding Resources</h3>
                    <p>Explore programming practice resources.</p>
                    <a href="/coding">Start coding →</a>
                </div>

                <div class="card">
                    <div class="emoji">⚙️</div>
                    <h3>Technical Interviews</h3>
                    <p>Review programming and computer science topics.</p>
                    <a href="/technical">Explore questions →</a>
                </div>

                <div class="card">
                    <div class="emoji">🤝</div>
                    <h3>HR Interviews</h3>
                    <p>Prepare for common HR interview questions.</p>
                    <a href="/hr">Prepare now →</a>
                </div>

                <div class="card">
                    <div class="emoji">📊</div>
                    <h3>Student Dashboard</h3>
                    <p>View your quiz scores and preparation progress.</p>
                    <a href="/dashboard">View Dashboard →</a>
                </div>

            </div>
        </section>

        <section class="section" id="about">
            <h2>Learn. Practise. Improve.</h2>
            <p class="subtitle">
                Your placement preparation journey starts here.
            </p>
        </section>

        <footer>
            <p>
                PrepPath — Placement Preparation Portal | Student Project 2026
            </p>
        </footer>
    </body>
    </html>
    """)


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session:
        return redirect(url_for("login"))

    score = None
    answers = {}
    results = []

    if request.method == "POST":
        for i, question in enumerate(QUESTIONS):
            answers[i] = request.form.get(str(i), "")

        score = sum(
            1 for i, question in enumerate(QUESTIONS)
            if answers.get(i) == question["answer"]
        )

        results = [
            {
                "question": question["question"],
                "selected": answers.get(i, ""),
                "correct": question["answer"],
                "is_correct": answers.get(i) == question["answer"]
            }
            for i, question in enumerate(QUESTIONS)
        ]

        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT INTO quiz_scores
                   (user_id, score, total_questions)
                   VALUES (?, ?, ?)""",
                (session["user_id"], score, len(QUESTIONS))
            )
            conn.commit()
        finally:
            conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aptitude Quiz | PrepPath</title>
        <link rel="stylesheet"
              href="{{ url_for('static', filename='css/style.css') }}">
        <style>
            .quiz-container {
                max-width: 800px;
                margin: auto;
            }
            .question-card {
                background: white;
                padding: 24px;
                margin: 20px 0;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            .option {
                display: block;
                padding: 9px 0;
                cursor: pointer;
            }
            .submit-btn {
                border: 0;
                cursor: pointer;
                font-size: 16px;
                margin-top: 12px;
            }
            .result {
                background: #dbeafe;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h2>PrepPath</h2>
            <div>
                <a href="/">Home</a>
                <a href="/quiz">Aptitude Quiz</a>
                <a href="/coding">Coding Resources</a>
            </div>
        </nav>

        <section class="section">
            <div class="quiz-container">
                <h1>Aptitude Practice Quiz</h1>
                <p class="subtitle">
                    Answer all 5 questions and submit to see your score.
                </p>

                {% if score is not none %}
                    <div class="result">
                        <h2>Your Score: {{ score }} / {{ questions|length }}</h2>
                        <p>You answered {{ score }} questions correctly.</p>
                    </div>

                    {% for r in results %}
                        <div class="question-card">
                            <h3>{{ loop.index }}. {{ r.question }}</h3>
                            <p>Your answer: {{ r.selected or "No answer" }}</p>
                            {% if r.is_correct %}
                                <p style="color: green;">Correct answer! ✓</p>
                            {% else %}
                                <p style="color: red;">Incorrect answer ✗</p>
                                <p>Correct answer: {{ r.correct }}</p>
                            {% endif %}
                        </div>
                    {% endfor %}
                    <p><a href="/quiz">Try Again →</a></p>
                {% endif %}

                <form method="POST">
                    {% for q in questions %}
                        {% set question_index = loop.index0 %}
                        <div class="question-card">
                            <h3>{{ question_index + 1 }}. {{ q.question }}</h3>

                            {% for option in q.options %}
                                <label class="option">
                                    <input type="radio"
                                           name="{{ question_index }}"
                                           value="{{ option }}"
                                           {% if answers.get(question_index) == option %}checked{% endif %}
                                           required>
                                    <span>{{ option }}</span>
                                </label>
                            {% endfor %}
                        </div>
                    {% endfor %}

                    <button class="btn submit-btn" type="submit">
                        Submit Answers
                    </button>
                </form>
            </div>
        </section>

        <footer>
            <p>PrepPath — Keep learning, keep improving!</p>
        </footer>
    </body>
    </html>
    """, questions=QUESTIONS, score=score, answers=answers, results=results)



@app.route("/coding")
def coding():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Coding Resources | PrepPath</title>

        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

        <style>
            .coding-container {
                max-width: 1100px;
                margin: auto;
            }

            .learning-level {
                background: white;
                padding: 25px;
                margin-top: 25px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }

            .learning-level h2 {
                color: #1e293b;
                margin-bottom: 12px;
            }

            .learning-level p {
                color: #64748b;
                line-height: 1.6;
            }

            .topic-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 12px;
                margin-top: 18px;
            }

            .topic-item {
                background: #f1f5f9;
                padding: 14px;
                border-radius: 8px;
                color: #334155;
            }

            .coding-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
                gap: 22px;
                margin-top: 25px;
            }

            .coding-card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .coding-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 18px rgba(0, 0, 0, 0.1);
            }

            .coding-emoji {
                font-size: 38px;
                margin-bottom: 10px;
            }

            .coding-card h3 {
                margin-bottom: 10px;
                color: #1e293b;
            }

            .coding-card p {
                color: #64748b;
                line-height: 1.6;
                min-height: 50px;
            }

            .coding-card a {
                display: inline-block;
                margin-top: 12px;
                color: #2563eb;
                text-decoration: none;
                font-weight: bold;
            }

            .coding-card a:hover {
                text-decoration: underline;
            }
        </style>
    </head>

    <body>
        <nav class="navbar">
            <h2>PrepPath</h2>
            <div>
                <a href="/">Home</a>
                <a href="/quiz">Aptitude Quiz</a>
                <a href="/coding">Coding Resources</a>
                <a href="/#about">About</a>
            </div>
        </nav>

        <section class="section">
            <div class="coding-container">

                <h1>Coding Resources</h1>
                <p class="subtitle">
                    Learn programming, practise problems, and prepare
                    for your dream placement.
                </p>

                <!-- LEVEL 1: BEGINNER PROGRAMMING -->
                <div class="learning-level">
                    <h2>🌱 Level 1 – Beginner Programming</h2>
                    <p>
                        Start your coding journey by understanding the
                        fundamental concepts of programming. This level
                        is suitable for students who are new to coding.
                    </p>

                    <div class="topic-list">
                        <div class="topic-item">📌 Variables and Data Types</div>
                        <div class="topic-item">➕ Operators and Expressions</div>
                        <div class="topic-item">🔀 If-Else Statements</div>
                        <div class="topic-item">🔁 Loops – For and While</div>
                        <div class="topic-item">⚙️ Functions and Methods</div>
                        <div class="topic-item">🧮 Basic Number Programs</div>
                        <div class="topic-item">🔤 Strings and Arrays Basics</div>
                        <div class="topic-item">💡 Basic Python, Java and C Programs</div>
                    </div>
                </div>

                <!-- LEVEL 2: PLACEMENT PREPARATION -->
                <div class="learning-level">
                    <h2>🚀 Level 2 – Placement Preparation</h2>
                    <p>
                        Improve your problem-solving skills and prepare
                        for technical placement rounds through important
                        coding concepts and practice problems.
                    </p>

                    <div class="topic-list">
                        <div class="topic-item">📚 Arrays and Strings</div>
                        <div class="topic-item">🔍 Searching Algorithms</div>
                        <div class="topic-item">📊 Sorting Algorithms</div>
                        <div class="topic-item">🔗 Linked Lists</div>
                        <div class="topic-item">📦 Stacks and Queues</div>
                        <div class="topic-item">🌳 Trees and Graph Basics</div>
                        <div class="topic-item">🧠 Logical Coding Problems</div>
                        <div class="topic-item">🏆 Common Interview Programs</div>
                    </div>
                </div>

                <!-- EXTERNAL LEARNING RESOURCES -->
                <h2 style="margin-top: 35px;">
                    📖 Learning Resources
                </h2>
                <p class="subtitle">
                    Explore these websites to learn concepts and practise coding.
                </p>

                <div class="coding-grid">

                    <div class="coding-card">
                        <div class="coding-emoji">🐍</div>
                        <h3>Python Programming</h3>
                        <p>
                            Learn Python basics, functions, loops,
                            and object-oriented programming.
                        </p>
                        <a href="https://www.learnpython.org/"
                           target="_blank" rel="noopener noreferrer">
                            Learn Python →
                        </a>
                    </div>

                    <div class="coding-card">
                        <div class="coding-emoji">☕</div>
                        <h3>Java Programming</h3>
                        <p>
                            Understand Java syntax, classes,
                            objects, and essential programming concepts.
                        </p>
                        <a href="https://dev.java/learn/"
                           target="_blank" rel="noopener noreferrer">
                            Learn Java →
                        </a>
                    </div>

                    <div class="coding-card">
                        <div class="coding-emoji">💻</div>
                        <h3>C Programming</h3>
                        <p>
                            Practise variables, arrays, pointers,
                            functions, and memory concepts.
                        </p>
                        <a href="https://www.learn-c.org/"
                           target="_blank" rel="noopener noreferrer">
                            Learn C →
                        </a>
                    </div>

                    <div class="coding-card">
                        <div class="coding-emoji">🌐</div>
                        <h3>Web Development</h3>
                        <p>
                            Learn HTML, CSS, and JavaScript to
                            create interactive websites.
                        </p>
                        <a href="https://developer.mozilla.org/en-US/docs/Learn_web_development"
                           target="_blank" rel="noopener noreferrer">
                            Learn Web Development →
                        </a>
                    </div>

                    <div class="coding-card">
                        <div class="coding-emoji">🧩</div>
                        <h3>Coding Practice</h3>
                        <p>
                            Solve programming problems and improve
                            your coding skills for placements.
                        </p>
                        <a href="https://www.hackerrank.com/"
                           target="_blank" rel="noopener noreferrer">
                            Practise on HackerRank →
                        </a>
                    </div>

                    <div class="coding-card">
                        <div class="coding-emoji">🏆</div>
                        <h3>Data Structures & Algorithms</h3>
                        <p>
                            Study arrays, linked lists, stacks,
                            queues, trees, and algorithms.
                        </p>
                        <a href="https://www.geeksforgeeks.org/"
                           target="_blank" rel="noopener noreferrer">
                            Explore DSA →
                        </a>
                    </div>

                </div>

                <div style="margin-top: 30px;">
                    <a class="btn" href="/">← Back to Home</a>
                </div>

            </div>
        </section>

        <footer>
            <p>PrepPath — Learn. Practise. Improve.</p>
        </footer>
    </body>
    </html>
    """)





@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            message = "Please fill in all fields."
        elif password != confirm_password:
            message = "Passwords do not match."
        elif len(password) < 8:
            message = "Password must be at least 8 characters."
        else:
            conn = get_db_connection()

            try:
                conn.execute(
                    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password))
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                conn.close()
                message = "This email is already registered."

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - PrepPath</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f4ff;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 12px;
                width: 320px;
                box-shadow: 0 4px 15px #ccd3e0;
            }
            input, button {
                box-sizing: border-box;
                width: 100%;
                padding: 11px;
                margin-top: 12px;
                border-radius: 6px;
            }
            input { border: 1px solid #ccc; }
            button {
                background: #3157d5;
                color: white;
                border: none;
                cursor: pointer;
            }
            .message { color: #c62828; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Create Your PrepPath Account</h2>
            <p>Register to start your placement preparation.</p>
            <p class="message">{{ message }}</p>

            <form method="POST">
                <input type="text" name="name"
                    placeholder="Full Name" required>
                <input type="email" name="email"
                    placeholder="Email Address" required>
                <input type="password" name="password"
                    placeholder="Password (8+ characters)"
                    minlength="8" required>
                <input type="password" name="confirm_password"
                    placeholder="Confirm Password" required>
                <button type="submit">Register</button>
            </form>

            <p>Already registered?
                <a href="/login">Login here</a>
            </p>
            <a href="/">Back to Home</a>
        </div>
    </body>
    </html>
    """, message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid email or password. Please try again."

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - PrepPath</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f4ff;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 12px;
                width: 320px;
                box-shadow: 0 4px 15px #ccd3e0;
            }
            input, button {
                box-sizing: border-box;
                width: 100%;
                padding: 11px;
                margin-top: 12px;
                border-radius: 6px;
            }
            input { border: 1px solid #ccc; }
            button {
                background: #3157d5;
                color: white;
                border: none;
                cursor: pointer;
            }
            .message { color: #c62828; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Welcome Back!</h2>
            <p>Login to your PrepPath account.</p>
            <p class="message">{{ message }}</p>

            <form method="POST">
                <input type="email" name="email"
                    placeholder="Email Address" required>
                <input type="password" name="password"
                    placeholder="Password" required>
                <button type="submit">Login</button>
            </form>

            <p>New student?
                <a href="/register">Create an account</a>
            </p>
            <a href="/">Back to Home</a>
        </div>
    </body>
    </html>
    """, message=message)



@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    student_name = session.get("user_name", "Student")

    # Get this student's previous quiz scores
    conn = get_db_connection()
    quiz_scores = conn.execute(
        """
        SELECT score, total_questions, created_at
        FROM quiz_scores
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard - PrepPath</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f4ff;
                margin: 0;
                color: #24304a;
            }
            header {
                background: #243b80;
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
            }
            header a { color: white; }
            main {
                max-width: 900px;
                margin: 30px auto;
                padding: 20px;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 18px;
            }
            .card {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 3px 12px #dce2f0;
            }
            .card a {
                display: inline-block;
                background: #3157d5;
                color: white;
                padding: 10px 14px;
                border-radius: 6px;
                text-decoration: none;
            }
            .history {
                background: white;
                padding: 24px;
                margin-top: 25px;
                border-radius: 12px;
                box-shadow: 0 3px 12px #dce2f0;
            }
            .score-row {
                padding: 14px 0;
                border-bottom: 1px solid #e2e8f0;
            }
        </style>
    </head>
    <body>
        <header>
            <h2>PrepPath Student Dashboard</h2>
            <a href="/logout">Logout</a>
        </header>

        <main>
            <h1>Welcome, {{ student_name }}! 👋</h1>
            <p>Your placement preparation journey starts here.</p>

            <div class="cards">
                <div class="card">
                    <h3>📝 Aptitude Quiz</h3>
                    <p>Practice questions to improve your aptitude skills.</p>
                    <a href="/quiz">Start Quiz</a>
                </div>

                <div class="card">
                    <h3>💻 Coding Practice</h3>
                    <p>Explore coding preparation resources.</p>
                    <a href="/coding">Explore Coding</a>
                </div>

                <div class="card">
                    <h3>🏠 Homepage</h3>
                    <p>Return to the PrepPath home page.</p>
                    <a href="/">Go Home</a>
                </div>
            </div>

            <div class="history">
                <h2>📊 Previous Quiz Scores</h2>

                {% if quiz_scores %}
                    {% for quiz in quiz_scores %}
                        <div class="score-row">
                            <strong>Quiz {{ loop.index }}</strong>
                            <p>
                                Score: {{ quiz["score"] }} /
                                {{ quiz["total_questions"] }}
                            </p>
                            <small>
                                Submitted on: {{ quiz["created_at"] }}
                            </small>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>You haven't attempted any quizzes yet.</p>
                    <p>Start your first aptitude quiz to see your scores here!</p>
                {% endif %}
            </div>
        </main>
    </body>
    </html>
    """, student_name=student_name, quiz_scores=quiz_scores)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/technical")
def technical():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template_string("""
    <html>
    <head>
        <title>Technical Interview | PrepPath</title>
        <link rel="stylesheet"
              href="{{ url_for('static', filename='css/style.css') }}">
    </head>

    <body>
        <nav class="navbar">
            <h2>PrepPath</h2>
            <div>
                <a href="/">Home</a>
                <a href="/quiz">Aptitude Quiz</a>
                <a href="/coding">Coding Resources</a>
            </div>
        </nav>

        <section class="section">
            <h1>Technical Interview Preparation</h1>
            <p class="subtitle">
                Prepare for technical interviews with important
                questions and answers.
            </p>

            <h2>Python Programming</h2>

            <div class="coding-card">
                <h3>1. What is Python?</h3>
                <p>
                    Python is a high-level, interpreted programming
                    language known for its simple and readable syntax.
                </p>
            </div>

            <div class="coding-card">
                <h3>2. What are variables in Python?</h3>
                <p>
                    Variables are names used to store data values.
                    For example: name = "Meghana".
                </p>
            </div>

            <div class="coding-card">
                <h3>3. What is a list in Python?</h3>
                <p>
                    A list is a collection that stores multiple items
                    in a single variable. Example: numbers = [10, 20, 30].
                </p>
            </div>
            
            <h2 style="margin-top: 30px;">Java Programming</h2>

            <div class="coding-card">
                <h3>1. What is Java?</h3>
                <p>
                    Java is a high-level, object-oriented programming
                    language used to develop applications.
                </p>
            </div>

            <div class="coding-card">
                <h3>2. What is JVM?</h3>
                <p>
                    JVM stands for Java Virtual Machine. It executes
                    Java bytecode and allows Java programs to run
                    on different platforms.
                </p>
            </div>

            <div class="coding-card">
                <h3>3. What is inheritance in Java?</h3>
                <p>
                    Inheritance is an object-oriented programming
                    concept where one class can acquire the properties
                    and methods of another class.
                </p>
            </div>
            
            <h2 style="margin-top: 30px;">C Programming</h2>

            <div class="coding-card">
                <h3>1. What is C programming?</h3>
                <p>
                    C is a general-purpose procedural programming
                    language used to develop system software and
                    applications.
                </p>
            </div>

            <div class="coding-card">
                <h3>2. What is a pointer in C?</h3>
                <p>
                    A pointer is a variable that stores the memory
                    address of another variable.
                </p>
            </div>

            <div class="coding-card">
                <h3>3. What is an array in C?</h3>
                <p>
                    An array is a collection of elements of the same
                    data type stored in continuous memory locations.
                </p>
            </div>
            
            <h2 style="margin-top: 30px;">DBMS (Database Management System)</h2>

            <div class="coding-card">
                <h3>1. What is DBMS?</h3>
                <p>
                    DBMS stands for Database Management System.
                    It is software used to store, manage, retrieve,
                    and organise data in a database.
                </p>
            </div>

            <div class="coding-card">
                <h3>2. What is a primary key?</h3>
                <p>
                    A primary key is a column or combination of columns
                    that uniquely identifies each record in a table.
                </p>
            </div>

            <div class="coding-card">
                <h3>3. What is SQL?</h3>
                <p>
                    SQL stands for Structured Query Language.
                    It is used to create, retrieve, update, and delete
                    data in relational databases.
                </p>
            </div>
            
            <h2 style="margin-top: 30px;">HTML, CSS and JavaScript</h2>

            <div class="coding-card">
                <h3>1. What is HTML?</h3>
                <p>
                    HTML stands for HyperText Markup Language.
                    It is used to create the structure and content
                    of web pages.
                </p>
            </div>

            <div class="coding-card">
                <h3>2. What is CSS?</h3>
                <p>
                    CSS stands for Cascading Style Sheets.
                    It is used to style web pages by controlling
                    colours, fonts, spacing, and layouts.
                </p>
            </div>

            <div class="coding-card">
                <h3>3. What is JavaScript?</h3>
                <p>
                    JavaScript is a programming language used to
                    make web pages interactive and dynamic.
                </p>
            </div>




            <div style="margin-top: 25px;">
                <a class="btn" href="/">← Back to Home</a>
            </div>
        </section>

        <footer>
            <p>PrepPath — Learn. Practise. Improve.</p>
        </footer>
    </body>
    </html>
    """)


@app.route("/hr")
def hr():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HR Interview | PrepPath</title>

        <link rel="stylesheet"
              href="{{ url_for('static', filename='css/style.css') }}">

        <style>
            .hr-container {
                max-width: 1000px;
                margin: auto;
            }

            .hr-card {
                background: white;
                padding: 22px;
                margin-top: 20px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }

            .hr-card h3 {
                color: #1e293b;
                margin-bottom: 12px;
            }

            .hr-card p {
                color: #64748b;
                line-height: 1.7;
            }

            .sample-answer {
                background: #f1f5f9;
                padding: 15px;
                border-radius: 8px;
            }
        </style>
    </head>

    <body>
        <nav class="navbar">
            <h2>PrepPath</h2>
            <div>
                <a href="/">Home</a>
                <a href="/quiz">Aptitude Quiz</a>
                <a href="/coding">Coding Resources</a>
                <a href="/technical">Technical Interview</a>
            </div>
        </nav>

        <section class="section">
            <div class="hr-container">

                <h1>HR Interview Preparation</h1>

                <p class="subtitle">
                    Build confidence and prepare for your HR interviews
                    with common questions and sample answers.
                </p>

                <div class="hr-card">
                    <h3>1. Tell me about yourself.</h3>
                    <div class="sample-answer">
                        <p>
                            I am a student with an interest in technology
                            and software development. I enjoy learning
                            new skills and improving my problem-solving
                            abilities. I am looking forward to starting
                            my career and contributing to an organisation.
                        </p>
                    </div>
                </div>

                <div class="hr-card">
                    <h3>2. What are your strengths?</h3>
                    <div class="sample-answer">
                        <p>
                            My strengths are quick learning, dedication,
                            teamwork, and a willingness to accept
                            challenges. I always try to improve myself.
                        </p>
                    </div>
                </div>

                <div class="hr-card">
                    <h3>3. What is your weakness?</h3>
                    <div class="sample-answer">
                        <p>
                            Sometimes I spend extra time checking my work
                            because I want it to be accurate. I am learning
                            to manage my time better while maintaining quality.
                        </p>
                    </div>
                </div>

                <div class="hr-card">
                    <h3>4. Why should we hire you?</h3>
                    <div class="sample-answer">
                        <p>
                            I am eager to learn, adaptable, and committed
                            to my responsibilities. I will work hard,
                            improve my skills, and contribute positively
                            to the team.
                        </p>
                    </div>
                </div>

                <div class="hr-card">
                    <h3>5. Where do you see yourself in five years?</h3>
                    <div class="sample-answer">
                        <p>
                            I see myself as a skilled professional with
                            strong technical knowledge, greater
                            responsibilities, and the ability to
                            contribute to important projects.
                        </p>
                    </div>
                </div>

                <div class="hr-card">
                    <h3>6. Why do you want to join our company?</h3>
                    <div class="sample-answer">
                        <p>
                            I want to join your company because it offers
                            opportunities to learn, develop my skills,
                            work with experienced professionals, and
                            contribute to meaningful projects.
                        </p>
                    </div>
                </div>

                <div style="margin-top: 25px;">
                    <a class="btn" href="/">← Back to Home</a>
                </div>

            </div>
        </section>

        <footer>
            <p>PrepPath — Learn. Practise. Improve.</p>
        </footer>

    </body>
    </html>
    """)


if __name__ == "__main__":
    app.run(debug=True)