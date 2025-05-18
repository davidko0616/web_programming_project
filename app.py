from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qna.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🔸 Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(20), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    votes = db.relationship('PostVote', backref='post', lazy=True, cascade="all, delete-orphan")

    @property
    def vote_count(self):
        return db.session.query(db.func.sum(PostVote.vote_type)).filter(
            PostVote.post_id == self.id
        ).scalar() or 0


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    votes = db.relationship('CommentVote', backref='comment', lazy=True, cascade="all, delete-orphan")

    @property
    def vote_count(self):
        return db.session.query(db.func.sum(CommentVote.vote_type)).filter(
            CommentVote.comment_id == self.id
        ).scalar() or 0


class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    vote_type = db.Column(db.Integer)  # 1 or -1


class CommentVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    vote_type = db.Column(db.Integer)


# 🔸 Create tables
with app.app_context():
    db.create_all()


# 🔹 Home
@app.route('/')
def home():
    return render_template('Home Page.html')


# 🔹 Intro
@app.route('/intro')
def intro():
    return render_template('intro.html')


# 🔹 Form
@app.route('/form')
def form():
    return render_template('form.html')


# 🔹 Q&A List
@app.route('/qna')
def qna():
    query = request.args.get("q", "")
    if query:
        filtered_posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
        ).all()
    else:
        filtered_posts = Post.query.all()
    return render_template('qna.html', posts=filtered_posts, query=query)


# 🔹 Write Post
@app.route('/qna/write', methods=['GET', 'POST'])
def qna_write():
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new_post = Post(name=name, title=title, content=content, created_at=created_at)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('qna'))

    return render_template('qna-write.html')


# 🔹 Edit Post
@app.route('/qna/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.name = request.form.get('name', post.name)
        db.session.commit()
        return redirect(url_for('qna'))

    return render_template('edit.html', post=post)


# 🔹 Delete Post
@app.route('/qna/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('qna'))


# 🔹 Add Comment
@app.route('/qna/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment_content = request.form['comment']

    new_comment = Comment(content=comment_content, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('qna'))


# 🔹 Vote on Post (dummy user_id=1)
@app.route('/post/<int:post_id>/vote/<path:vote_type>', methods=['POST'])
def vote_post(post_id, vote_type):
    try:
        vote_type = int(vote_type)
    except ValueError:
        abort(400)

    if vote_type not in (1, -1):
        abort(400)

    user_id = 1  # Dummy user ID

    existing_vote = PostVote.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            pass  # Same vote clicked again → do nothing
        else:
            db.session.delete(existing_vote)  # Opposite vote → remove vote (becomes 0)
    else:
        new_vote = PostVote(user_id=user_id, post_id=post_id, vote_type=vote_type)
        db.session.add(new_vote)

    db.session.commit()
    return redirect(url_for('qna'))



# 🔹 Vote on Comment (dummy user_id=1)
@app.route('/comment/<int:comment_id>/vote/<path:vote_type>', methods=['POST'])
def vote_comment(comment_id, vote_type):
    try:
        vote_type = int(vote_type)
    except ValueError:
        abort(400)

    if vote_type not in (1, -1):
        abort(400)

    user_id = 1  # Dummy user ID

    existing_vote = CommentVote.query.filter_by(user_id=user_id, comment_id=comment_id).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            pass  # Same vote clicked → do nothing
        else:
            db.session.delete(existing_vote)  # Opposite vote clicked → cancel vote
    else:
        new_vote = CommentVote(user_id=user_id, comment_id=comment_id, vote_type=vote_type)
        db.session.add(new_vote)

    db.session.commit()
    return redirect(url_for('qna'))



# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)
