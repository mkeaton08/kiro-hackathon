"""
Database module for Mini CTF Game
Handles SQLite database operations and table management.
"""

import sqlite3
import os
from datetime import datetime
import hashlib

DATABASE_FILE = "ctf_game.db"

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_database():
    """Initialize the database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            is_organizer INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create challenges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            flag TEXT NOT NULL,
            points INTEGER NOT NULL,
            max_attempts INTEGER DEFAULT -1,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            challenge_id INTEGER,
            submitted_flag TEXT NOT NULL,
            is_correct INTEGER,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')
    
    # Create user challenge progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_challenge_progress (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            challenge_id INTEGER,
            is_solved INTEGER DEFAULT 0,
            attempts_count INTEGER DEFAULT 0,
            solved_at TIMESTAMP,
            locked_until TIMESTAMP,
            UNIQUE(user_id, challenge_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# User management functions
def create_user(username, password, is_organizer=False):
    """Create a new user with hashed password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_organizer)
            VALUES (?, ?, ?)
        ''', (username, password_hash, int(is_organizer)))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Username already exists

def get_user_by_username(username):
    """Get user information by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    return user

def verify_password(username, password):
    """Verify user password and return user info if correct."""
    user = get_user_by_username(username)
    if not user:
        return None
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] == password_hash:
        return user
    return None

# Challenge management functions
def create_challenge(title, description, category, flag, points, max_attempts=-1):
    """Create a new challenge."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO challenges (title, description, category, flag, points, max_attempts)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, category, flag, points, max_attempts))
    
    challenge_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return challenge_id

def get_all_challenges():
    """Get all active challenges."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM challenges WHERE is_active = 1 ORDER BY points ASC')
    challenges = cursor.fetchall()
    conn.close()
    
    return challenges

def get_challenge_by_id(challenge_id):
    """Get a specific challenge by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM challenges WHERE id = ? AND is_active = 1', (challenge_id,))
    challenge = cursor.fetchone()
    conn.close()
    
    return challenge

# Submission and progress functions
def submit_flag(user_id, challenge_id, submitted_flag):
    """Submit a flag for a challenge and return result."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the challenge
    challenge = get_challenge_by_id(challenge_id)
    if not challenge:
        conn.close()
        return False, "Challenge not found"
    
    # Check if already solved
    cursor.execute('''
        SELECT is_solved FROM user_challenge_progress 
        WHERE user_id = ? AND challenge_id = ?
    ''', (user_id, challenge_id))
    
    progress = cursor.fetchone()
    if progress and progress['is_solved']:
        conn.close()
        return False, "Challenge already solved"
    
    # Check flag correctness
    is_correct = (submitted_flag.strip() == challenge['flag'].strip())
    
    # Record submission
    cursor.execute('''
        INSERT INTO submissions (user_id, challenge_id, submitted_flag, is_correct)
        VALUES (?, ?, ?, ?)
    ''', (user_id, challenge_id, submitted_flag, int(is_correct)))
    
    # Update or create progress record
    if progress:
        cursor.execute('''
            UPDATE user_challenge_progress 
            SET attempts_count = attempts_count + 1,
                is_solved = ?,
                solved_at = ?
            WHERE user_id = ? AND challenge_id = ?
        ''', (int(is_correct), datetime.now() if is_correct else None, user_id, challenge_id))
    else:
        cursor.execute('''
            INSERT INTO user_challenge_progress 
            (user_id, challenge_id, attempts_count, is_solved, solved_at)
            VALUES (?, ?, 1, ?, ?)
        ''', (user_id, challenge_id, int(is_correct), datetime.now() if is_correct else None))
    
    # Update user score if correct
    if is_correct:
        cursor.execute('''
            UPDATE users SET score = score + ? WHERE id = ?
        ''', (challenge['points'], user_id))
    
    conn.commit()
    conn.close()
    
    if is_correct:
        return True, f"Correct! You earned {challenge['points']} points!"
    else:
        return False, "Incorrect flag. Try again!"

def get_user_progress(user_id):
    """Get user's challenge progress and score."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute('SELECT username, score FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    # Get solved challenges
    cursor.execute('''
        SELECT c.title, c.points, p.solved_at
        FROM challenges c
        JOIN user_challenge_progress p ON c.id = p.challenge_id
        WHERE p.user_id = ? AND p.is_solved = 1
        ORDER BY p.solved_at ASC
    ''', (user_id,))
    
    solved_challenges = cursor.fetchall()
    conn.close()
    
    return user, solved_challenges

def get_leaderboard():
    """Get leaderboard sorted by score and solve time."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, score, created_at
        FROM users
        WHERE score > 0
        ORDER BY score DESC, created_at ASC
    ''')
    
    leaderboard = cursor.fetchall()
    conn.close()
    
    return leaderboard