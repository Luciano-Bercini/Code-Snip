from flask import Flask, render_template, request, redirect
from datetime import *
from flask_sqlalchemy import *
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<Post %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_language = request.form['language']
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
        snippet_to_update.title = request.form['title']
        snippet_to_update.content = request.form['content']
        snippet_to_update.language = request.form['language']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task.'
    else:
        return render_template('update.html', snippet=snippet_to_update)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        post_title = request.form['title']
        post_language = request.form['language']
        posts = Post.query.filter(Post.title.contains(post_title), Post.language.ilike(post_language)) \
            .order_by(Post.title.desc()).all()
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
