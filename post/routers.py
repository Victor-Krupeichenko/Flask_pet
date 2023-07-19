from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from math import ceil
from app_database.models import Post
from app_database.db_connect import session_maker, limit
from flask_login import login_required, current_user
from post.forms import PostForm, SearchForm
from sqlalchemy import select, or_, func
from user.routers import get_errors, get_error_database_flash_message

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
                get_error_database_flash_message(error=ex, db_session=db_session)
                return redirect(url_for("post.create_post"))
        else:
            get_errors(form)
    return render_template("post/post_crete.html", response=response, form=form)


def pagination(_limit, total_posts, query, title_page, start, end):
    """Pagination"""
    total_pages = ceil(total_posts / _limit)
    show_pagination = total_pages > 1
    results = query[start:end]
    response = {
        "results": results,
        "total_pages": total_pages,
        "show_pagination": show_pagination,
        "title": title_page
    }
    return response


def my_range(_limit):
    """Range and limit post"""
    page = request.args.get('page', default=1, type=int)
    start = (page - 1) * _limit
    end = start + _limit
    return start, end, page


@post.route("/")
def view_all_posts():
    title_page = "Flask Home Page"
    with session_maker() as db_session:
        try:
            query = db_session.scalars(select(Post).filter(Post.publish).order_by(Post.id.desc())).all()
            total_posts = len(query)
            start, end, page = my_range(limit)
            response = pagination(
                _limit=limit, total_posts=total_posts, query=query, title_page=title_page, start=start, end=end
            )
            return render_template('post/index.html', response=response, page=page)
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for('index'))


@post.route("/detail-post/<int:post_id>")
def detail_post(post_id):
    """Detail Post"""
    with session_maker() as db_session:
        try:
            view_post = db_session.get(Post, post_id)
            if view_post:
                response = {
                    "title": view_post.title,
                }
                return render_template('post/view_post.html', view_post=view_post, response=response)
            else:
                abort(404)
        except Exception as ex:
            flash(message=f'{ex}', category="info")
            abort(404)


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
                    get_errors(form)
                    return render_template('post/post_crete.html', response=response, form=form,
                                           update_current_post=update_current_post)
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
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
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for("index"))


@post.route('/search', methods=["GET"])
def search():
    """Search Post"""
    form = SearchForm()
    search_query = request.args.get("search", "").strip()  # Получаем значение параметра "search" из запроса
    response_not_query = {
        "results": [],
        "total_pages": 0,
        "show_pagination": False,
        "title": f"Search {search_query} not found"
    }
    if search_query:
        with session_maker() as db_session:
            query = db_session.scalars(select(Post).filter(
                or_(
                    func.lower(Post.title).like(f"%{search_query.lower()}%"),
                    func.lower(Post.content).like(f"%{search_query.lower()}%")
                )
            )).all()
        total_posts = len(query)
        if total_posts == 0:
            flash(message=f"{search_query} not found", category="info")
            return render_template("post/index.html", form=form, search_query=search_query, response=response_not_query)
        title = f"Search {search_query}"
        start, end, page = my_range(limit)
        response = pagination(limit, title_page=title, start=start, end=end, total_posts=total_posts, query=query)
        return render_template("post/index.html", form=form, search_query=search_query, response=response, page=page)
    else:
        return render_template("post/index.html", form=form, search_query=search_query, response=response_not_query)
