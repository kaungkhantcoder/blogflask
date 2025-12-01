from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

posts = []
post_id_counter = 1


@app.route("/")
def index():
    return render_template("index.html", posts=posts, active="home")


@app.route("/search")
def search():
    q = request.args.get("q", "").strip().lower()
    results = [p for p in posts if q in p["title"].lower()]
    return render_template("search.html", posts=results, q=q, active=None)


@app.route("/post/<int:id>")
def post_single(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:

        return redirect(url_for("index"))
    return render_template("post.html", post=post, active=None)


@app.route("/create", methods=["GET", "POST"])
def create():
    global post_id_counter

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        uploaded_file = request.files.get("photo")

        if not title:

            return render_template("form.html", mode="create", post=None, active="create")

        if not uploaded_file or uploaded_file.filename == "":

            return render_template("form.html", mode="create", post=None, active="create")

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

        post = {
            "id": post_id_counter,
            "title": title,
            "content": content,
            "image_path": f"/static/uploads/{filename}",
        }
        posts.append(post)
        post_id_counter += 1

        return redirect(url_for("index"))

    return render_template("form.html", mode="create", post=None, active="create")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:

        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        uploaded_file = request.files.get("photo")

        if not title:

            return render_template("form.html", mode="edit", post=post, active="create")

        post["title"] = title
        post["content"] = content

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
            post["image_path"] = f"/static/uploads/{filename}"

        return redirect(url_for("post_single", id=id))

    return render_template("form.html", mode="edit", post=post, active="create")


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    global posts
    posts = [p for p in posts if p["id"] != id]

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
