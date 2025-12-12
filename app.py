from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

load_dotenv()

app.secret_key = os.getenv('serect-key')

UPLOAD_FOLDER = "static/uploads/image"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# app.config["UPLOAD_FOLDER"] = 'static/uploads/image'
app.config["AUDIO_UPLOAD_FOLDER"] = 'static/uploads/audio'

# posts = []
# post_id_counter = 1

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    audio_url = db.Column(db.String(200))

@app.route("/")
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("index.html", posts=posts, active="home")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("notfound.html"), 404

@app.route("/search")
def search():
    q = request.args.get("q", "").strip().lower()
    # results = [p for p in posts if q in p["title"].lower()]
    results = Post.query.filter(Post.title.ilike(f"%{q}%")).all()

    return render_template("search.html", posts=results, q=q, active=None)


@app.route("/post/<int:id>")
def post_single(id):
    # post = next((p for p in posts if p["id"] == id), None)

    post = Post.query.get(id)
    if not post:
        flash("Post not found.")
        return redirect(url_for("index"))
    return render_template("post.html", post=post, active=None)


@app.route("/create", methods=["GET", "POST"])
def create():
    global post_id_counter

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        image_file = request.files.get("photo")
        audio_file = request.files.get("audio")

        image_path = None
        audio_url = None

        if not title:
            flash("Title is required.")
            return render_template("form.html", mode="create", post=None, active="create")

        if not image_file or image_file.filename == "":
            flash("Please upload an image.")

            return render_template("form.html", mode="create", post=None, active="create")
        
        if image_file and image_file.filename != "":
            image_name = secure_filename(image_file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            image_file.save(img_path)
            image_path = f"/static/uploads/image/{image_name}"

        # filename = secure_filename(uploaded_file.filename)
        # save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if audio_file and audio_file.filename != "":
            audio_name = secure_filename(audio_file.filename)
            audio_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], audio_name)
            audio_file.save(audio_path)
            audio_url = f"/static/uploads/audio/{audio_name}"

        # counter = 1
        # original_name = filename
        # while os.path.exists(save_path):
        #     name, ext = os.path.splitext(original_name)
        #     filename = f"{name}_{counter}{ext}"
        #     save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        #     counter += 1

        # uploaded_file.save(save_path)

        # post = {
        #     "id": post_id_counter,
        #     "title": title,
        #     "content": content,
        #     "image_path": image_path,
        #     "audio_url": audio_url
        # }
        
        # posts.append(post)
        post = Post(title=title, content=content, image_path=image_path, audio_url=audio_url)
        db.session.add(post)
        db.session.commit()

        # post_id_counter += 1

        return redirect(url_for("index"))

    return render_template("form.html", mode="create", post=None, active="create")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    # post = next((p for p in posts if p["id"] == id), None)

    post = Post.query.get(id)
    
    if not post:
        flash("Post not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        uploaded_file = request.files.get("photo")
        audio_file = request.files.get("audio")

        if not title:
            flash("Title is required.")
            return render_template("form.html", mode="edit", post=post, active="create")

        # post["title"] = title
        # post["content"] = content

        post.title = title
        post.content = content

        if audio_file and audio_file.filename != "":
            audio_name = secure_filename(audio_file.filename)
            audio_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], audio_name)
            audio_file.save(audio_path)
            post.audio_url = f"/static/uploads/audio/{audio_name}"

        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            counter = 1
            original_name = filename
            while os.path.exists(save_path):
                name, ext = os.path.splitext(original_name)
                filename = f"{name}_{counter}{ext}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                counter += 1

            uploaded_file.save(save_path)
            post.image_path = f"/static/uploads/image/{filename}"

        db.session.commit()

        return redirect(url_for("post_single", id=id))

    return render_template("form.html", mode="edit", post=post, active="create")


# @app.route("/delete/<int:id>", methods=["POST"])
# def delete(id):
#     global posts
#     # posts = [p for p in posts if p["id"] != id]

#     post = Post.query.get(id)
#     db.session.delete(post)
#     db.session.commit()
#     flash("Post deleted.")
#     return redirect(url_for("index"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    post = Post.query.get(id)
    if not post:
        flash("Post not found")
        return redirect(url_for("index"))
    
    if post.image_path:
        image_full_path = os.path.join(app.root_path, post.image_path.lstrip("/"))
        if os.path.exists(image_full_path):
            os.remove(image_full_path)

    if post.audio_url:
        audio_full_path = os.path.join(app.root_path, post.audio_url.lstrip("/"))
        if os.path.exists(audio_full_path):
            os.remove(audio_full_path)
    
    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
