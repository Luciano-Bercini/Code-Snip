import logging
from flask import Flask, render_template, request, redirect, jsonify, make_response, send_from_directory
from datetime import *
from dataclasses import dataclass
from flask_sqlalchemy import *
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


@dataclass
class Post(db.Model):
    id: int
    title: str
    content: str
    language: str
    date_created: date

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))


@app.route('/post_snippet', methods=['POST'])
def post_snippet():
    title = request.form.get('title')
    content = request.form.get('content')
    language = request.form.get('language')

    post_validation = is_snippet_valid(title, content)
    if not post_validation[0]:
        return post_validation[1]

    new_post = Post(title=title, content=content, language=language)
    try:
        db.session.add(new_post)
        db.session.commit()
        return "success"
    except Exception as e:
        logging.exception(e)
        return "Unable to commit to database"


def is_snippet_valid(title, content):
    if not title:
        return False, "Missing title!"
    if len(title) > 1000:
        return False, "Title is over 1000 characters!"
    if len(content) > 10000:
        return False, "Content is over 10000 characters!"
    return True, "The post is valid!"



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/update_snippet/<int:id>', methods=['GET', 'POST'])
def update_snippet(id):
    snippet = Post.query.get_or_404(id)
    if request.method == 'POST':
        snippet.title = request.form.get('title')
        snippet.content = request.form.get('content')
        snippet.language = request.form.get('language')
        post_validation = is_snippet_valid(snippet.title, snippet.content)
        if not post_validation[0]:
            return post_validation[1]
        try:
            db.session.commit()
            return "success"
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', snippet=snippet)


@app.route('/sw.js')
def sw():
    response = make_response(send_from_directory('static', 'sw.js'))
    return response


@app.route('/view/<int:id>')
def view(id):
    snippet = Post.query.get_or_404(id)
    return render_template('view.html', snippet=snippet)


@app.route('/render_query_table', methods=['GET'])
def render_query_table():
    post_title = request.args.get('title')
    post_language = request.args.get('language')
    conditions = []
    conditions.append(Post.title.contains(post_title))
    if post_language != 'Any':
        conditions.append(Post.language.ilike(post_language))
    posts = Post.query.filter(*conditions) \
        .order_by(Post.title.desc()) \
        .all()
    return jsonify(render_template('query_table.html', posts=posts))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        post_title = request.form['title']
        post_language = request.form['language']
        conditions = []
        if not post_title:
            conditions.append(Post.title.contains(post_title))
        if post_language != 'Any':
            conditions.append(Post.language.ilike(post_language))
        posts = Post.query.filter(*conditions) \
            .order_by(Post.title.desc()) \
            .all()
    else:
        posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('/search.html', posts=posts)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Post.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/search')
    except:
        return 'There was a problem deleting the task.'


@app.route('/information')
def information():
    return render_template('information.html')


if __name__ == "__main__":
    app.run(debug=True)
