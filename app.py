from flask import Flask, render_template, request, redirect, jsonify
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_title = request.form('title')
        post_content = request.form.get('content')
        post_language = request.form.get('language')
        new_post = Post(title=post_title, content=post_content, language=post_language)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue posting your task.'
    else:
        return render_template('index.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    snippet_to_update = Post.query.get_or_404(id)
    if request.method == 'POST':
        snippet_to_update.title = request.form.get('title')
        snippet_to_update.content = request.form.get('content')
        snippet_to_update.language = request.form.get('language')
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', snippet=snippet_to_update)

@app.route('/view/<int:id>')
def view(id):
    snippet_to_update = Post.query.get_or_404(id)
    return render_template('view.html', snippet=snippet_to_update)


@app.route('/render_query_table', methods=['GET'])
def render_query_table():
    post_title = request.args.get('title')
    post_language = request.args.get('language')
    conditions = []
    conditions.append(Post.title.contains(post_title))
    if post_language != 'Any':
        conditions.append(Post.language.ilike(post_language))
    posts = Post.query.filter(*conditions)\
        .order_by(Post.title.desc())\
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
        posts = Post.query.filter(*conditions)\
            .order_by(Post.title.desc())\
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


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)
