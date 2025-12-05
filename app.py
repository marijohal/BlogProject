# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, abort
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

TOPICS_FILE = 'topics.json'
POSTS_FILE = 'posts.json'

def load_json(filename, default=[]):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    return default

def save_json(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError:
        return False

def get_topics():
    return load_json(TOPICS_FILE, [])

def save_topics(topics):
    return save_json(TOPICS_FILE, topics)

def get_posts():
    posts = load_json(POSTS_FILE, [])
    # Ensure each post has an ID if missing (for legacy data)
    for post in posts:
        if 'id' not in post:
            post['id'] = len(posts) + 1
    return posts

def save_posts(posts):
    return save_json(POSTS_FILE, posts)

@app.route('/')
def index():
    posts = get_posts()
    recent_posts = posts[-3:] if len(posts) > 3 else posts  # Latest 3
    topics = get_topics()
    return render_template('index.html', posts=recent_posts, topics=topics)

@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    topics = get_topics()
    if request.method == 'POST':
        new_topic = request.form.get('topic', '').strip()
        if new_topic and new_topic not in topics:
            topics.append(new_topic)
            if save_topics(topics):
                flash(f'Topic "{new_topic}" added successfully!', 'success')
            else:
                flash('Error saving topic. Please try again.', 'error')
            return redirect(url_for('index'))
        elif new_topic in topics:
            flash('Topic already exists!', 'error')
        else:
            flash('Topic name cannot be empty!', 'error')
    return render_template('add_topic.html', topics=topics)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    topics = get_topics()
    if not topics:
        flash('No topics available. Please add a topic first.', 'warning')
        return redirect(url_for('add_topic'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        topic = request.form.get('topic', '')
        content = request.form.get('content', '').strip()
        
        if title and topic in topics and content:
            posts = get_posts()
            new_id = max([p.get('id', 0) for p in posts] + [0]) + 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_post = {
                'id': new_id,
                'title': title,
                'topic': topic,
                'content': content,
                'timestamp': timestamp
            }
            posts.append(new_post)
            if save_posts(posts):
                flash('Post created successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error saving post. Please try again.', 'error')
        else:
            if not title:
                flash('Title is required!', 'error')
            if not topic:
                flash('Please select a topic!', 'error')
            if not content:
                flash('Post content cannot be empty!', 'error')
    
    return render_template('add_post.html', topics=topics)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = get_posts()
    post = next((p for p in posts if p.get('id') == post_id), None)
    if not post:
        abort(404)
    return render_template('view_post.html', post=post)

if __name__ == '__main__':
    app.run(debug=True)