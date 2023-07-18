from flask import Blueprint, render_template, request, url_for, redirect, flash
from app_database.models import Post
from app_database.db_connect import session_maker
from flask_login import login_required, current_user
from post.forms import PostForm, SearchForm
from sqlalchemy import select, or_, func

post = Blueprint("post", __name__, template_folder="templates", static_folder="static")


def get_post_form_data(form):
    """Get data is form"""
    form_data = {}
    exclude_fields = ["submit", "csrf_token"]
    for field in form:
        if field.name not in exclude_fields:
            form_data.setdefault(field.name, field.data)
    form_data.update({"author_id": current_user.id})
    return form_data


@post.route("/create-post", methods=["POST", "GET"])
@login_required
def create_post():
    """Create Post"""
    response = {
        "title": "Create Post",
        "create_post": True,
    }
    form = PostForm()
    if request.method == "POST":
        if form.validate_on_submit():
            form_data = get_post_form_data(form)
            try:
                with session_maker() as db_session:
                    create = Post(**form_data)
                    db_session.add(create)
                    db_session.commit()
                    flash(message="Post added successfully", category="success")
                    return redirect(url_for("index"))
            except Exception as ex:
                flash(message=f"Error connect Database {ex}", category="danger")
        else:
            for field, error in form.errors.items():
                flash(message=f"Error: field - {error.pop(0)}", category="danger")
    return render_template("post/post_crete.html", response=response, form=form)


@post.route("/")
def view_all_posts():
    response = {
        "title": "Flask Home Page"
    }
    with session_maker() as db_session:
        try:
            results = db_session.scalars(select(Post)).all()
            return render_template('post/index.html', results=results, response=response)
        except Exception as ex:
            flash(message=f"Error connect Databse {ex}", category='danger')
            return redirect(url_for('index'))


@post.route("/detail-post<int:post_id>")
def detail_post(post_id):
    with session_maker() as db_session:
        try:
            view_post = db_session.get(Post, post_id)
        except Exception as ex:
            flash(message=f"Error connect Databse {ex}", category='danger')
            return redirect(url_for('index'))
        response = {
            "title": view_post.title,
        }
        return render_template('post/view_post.html', view_post=view_post, response=response)


@post.route("/update-post/<int:post_id>", methods=["POST", "GET"])
def update_post(post_id):
    """Update Post"""
    form = PostForm()
    with session_maker() as db_session:
        try:
            update_current_post = db_session.get(Post, post_id)
            form.content.data = update_current_post.content  # Field TextArea
            response = {
                "title": f"Update: {update_current_post.title}",
                "update_post": True
            }
            if request.method == "POST":
                if form.validate_on_submit():
                    form.content.data = request.form.get("content")  # Field TextArea
                    form_data = get_post_form_data(form)
                    for key, value in form_data.items():
                        setattr(update_current_post, key, value)
                    db_session.commit()
                    flash(message=f"Post {update_current_post.title} successfully updated", category="success")
                    return redirect(url_for('post.detail_post', post_id=post_id))
                else:
                    for field, error in form.errors.items():
                        flash(message=f"Error: field - {error.pop(0)}", category="danger")
                    return render_template('post/post_crete.html', response=response, form=form,
                                           update_current_post=update_current_post)
        except Exception as ex:
            flash(message=f"Error connect Databse {ex}", category='danger')
            return redirect(url_for('post.update_post'))
        return render_template('post/post_crete.html', response=response, form=form,
                               update_current_post=update_current_post)


@post.route("/delete-post/<int:post_id>")
@login_required
def delete_post(post_id):
    """Delete Post"""
    with session_maker() as db_session:
        try:
            post_delete = db_session.get(Post, post_id)
            title = post_delete.title
            db_session.delete(post_delete)
            db_session.commit()
            flash(message=f"Post: {title} Deleted", category="info")
            return redirect(url_for('index'))
        except Exception as ex:
            flash(message=f"Error connect Databse {ex}", category='danger')
            return redirect(url_for("index"))


@post.route('/search', methods=["POST"])
def search():
    """Search Post"""
    with session_maker() as db_session:
        response = {
            "title": "Search result"
        }
        form = SearchForm()
        if form.validate_on_submit():
            try:
                post_name = form.search.data
                results = db_session.scalars(select(Post).filter(or_(
                    func.lower(Post.title).like(f"%{post_name.lower()}%"),
                    func.lower(Post.content).like(f"%{post_name.lower()}%")
                )))
                return render_template('post/index.html', response=response, results=results)
            except Exception as ex:
                flash(message=f"Error connect Databse {ex}", category='danger')
                return redirect(url_for("index"))
