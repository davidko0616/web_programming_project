from flask import Flask, render_template, request, redirect, url_for, abort, flash, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask_wtf.csrf import CSRFProtect




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qna.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'sdfh2337gffysdhfks0gsceuhfgvwhww3u7fgfkbgy1yufhf'  # Replace with a real secret key
csrf = CSRFProtect(app)



# 🔸 Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))  # 추가
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


@app.route('/history')
def history():
    return render_template('history.html')


# 🔹 Form
@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/team')
def team():
    return render_template('team.html')


# 🔹 Q&A List
@app.route('/qna')
def qna():
    query = request.args.get('query', '')
    if query:
        posts = Post.query.filter(
            (Post.title.contains(query)) |
            (Post.content.contains(query)) |
            (Post.name.contains(query))
        ).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('qna.html', posts=posts, query=query)

# 🔹 Write Post
@app.route('/qna/write', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        post = Post(name=name, title=title, content=content, password_hash=password_hash)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('qna'))
    return render_template('qna-write.html')




# 🔹 Delete Post
@app.route('/qna/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    password = request.form.get('password')

    if not password:
        flash('비밀번호를 입력해주세요.')
        return redirect(url_for('verify_delete', post_id=post.id))

    if check_password_hash(post.password_hash, password):
        db.session.delete(post)
        db.session.commit()
        flash('게시글이 성공적으로 삭제되었습니다.')
        return redirect(url_for('qna'))
    else:
        flash('비밀번호가 일치하지 않습니다.')
        return redirect(url_for('verify_delete', post_id=post.id))


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
        # Convert vote_type to integer and validate
        try:
            vote_type = int(vote_type)
        except ValueError:
            abort(400, description="Invalid vote type")

        if vote_type not in (1, -1):
            abort(400, description="Vote type must be 1 or -1")

        # Initialize user session if not exists
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())

        user_id = session['user_id']

        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            abort(404, description="Post not found")

        # Check for existing vote
        existing_vote = PostVote.query.filter_by(
            user_id=user_id,
            post_id=post_id
        ).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Same vote clicked again - remove the vote
                db.session.delete(existing_vote)
                db.session.commit()
                return redirect(url_for('qna'))
            else:
                # Opposite vote clicked - update the vote
                existing_vote.vote_type = vote_type
        else:
            # New vote
            new_vote = PostVote(
                user_id=user_id,
                post_id=post_id,
                vote_type=vote_type
            )
            db.session.add(new_vote)

        db.session.commit()
        return redirect(url_for('qna'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing vote: {str(e)}")
        abort(500, description="An error occurred while processing your vote")



# 🔹 Vote on Comment (dummy user_id=1)
@app.route('/comment/<int:comment_id>/vote/<path:vote_type>', methods=['POST'])
def vote_comment(comment_id, vote_type):
    try:
        # Convert vote_type to integer and validate
        try:
            vote_type = int(vote_type)
        except ValueError:
            abort(400, description="Invalid vote type")

        if vote_type not in (1, -1):
            abort(400, description="Vote type must be 1 or -1")

        # Initialize user session if not exists
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())

        user_id = session['user_id']

        # Check if comment exists
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(404, description="Comment not found")

        # Check for existing vote
        existing_vote = CommentVote.query.filter_by(
            user_id=user_id,
            comment_id=comment_id
        ).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Same vote clicked again - remove the vote
                db.session.delete(existing_vote)
                db.session.commit()
                return redirect(url_for('qna'))
            else:
                # Opposite vote clicked - update the vote
                existing_vote.vote_type = vote_type
        else:
            # New vote
            new_vote = CommentVote(
                user_id=user_id,
                comment_id=comment_id,
                vote_type=vote_type
            )
            db.session.add(new_vote)

        db.session.commit()
        return redirect(url_for('qna'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error processing comment vote: {str(e)}")
        abort(500, description="An error occurred while processing your vote")


@app.route('/qna/verify/<int:post_id>', methods=['GET', 'POST'])
def verify(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(post.password_hash, password):
            # Password correct - redirect to edit page
            return redirect(url_for('edit_post', post_id=post.id))
        else:
            flash('비밀번호가 일치하지 않습니다.')

    return render_template('verify.html', post=post)


@app.route('/qna/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        # No need to verify password again here since we came from verify
        post.name = request.form['name']
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('게시글이 성공적으로 수정되었습니다.')
        return redirect(url_for('qna'))

    return render_template('edit.html', post=post)


@app.route('/qna/verify-delete/<int:post_id>', methods=['GET', 'POST'])
def verify_delete(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(post.password_hash, password):
            db.session.delete(post)
            db.session.commit()
            flash('게시글이 성공적으로 삭제되었습니다.')
            return redirect(url_for('qna'))
        else:
            flash('비밀번호가 일치하지 않습니다.')

    return render_template('verify_delete.html', post=post)

# 🔹 Run App
if __name__ == '__main__':
    app.run(debug=True)
