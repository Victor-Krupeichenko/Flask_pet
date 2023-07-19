from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required
from category.forms import CategoryForm
from app_database.db_connect import session_maker
from sqlalchemy import func, select
from app_database.models import Category, Post
from user.routers import get_errors, get_error_database_flash_message

category = Blueprint("category", __name__, static_folder="static", template_folder="templates")


@category.route("/create-category", methods=["POST", "GET"])
@login_required
def create_category():
    """Create Category"""
    response = {
        "title": "Create Category",
        "category_create": True
    }
    form = CategoryForm()
    if request.method == "POST":
        if form.validate_on_submit():
            title = request.form.get("title")
            with session_maker() as db_session:
                try:
                    create = Category(title=title)
                    db_session.add(create)
                    db_session.commit()
                    flash(message=f"Category: {title} Successfully added", category="success")
                    return redirect(url_for('category.all_categories'))
                except Exception as ex:
                    get_error_database_flash_message(error=ex, db_session=db_session)
                    return render_template("category/create_category.html", form=form, response=response)
        else:
            get_errors(form)
    return render_template("category/create_category.html", response=response, form=form)


@category.route("/all-categories")
@login_required
def all_categories():
    """All Categories"""
    response = {
        "title": "All Category",
        "all_category": True
    }
    with session_maker() as db_session:
        try:
            category_all = db_session.query(Category.id, Category.title, func.count(Post.id)).outerjoin(Post).group_by(
                Category.id, Category.title).all()
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for("category.all_categories"))
        return render_template('category/all_category.html', response=response, categories=category_all)


@category.route("/posts-category/<int:category_id>")
def posts_category(category_id):
    with session_maker() as db_session:
        try:
            title = db_session.get(Category, category_id)
            results = db_session.scalars(
                select(Post).filter(Post.category_id == category_id).filter(Post.publish)).all()
            response = {
                "title": title.title
            }
            return render_template("post/index.html", results=results, response=response)
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for("index"))


@category.route("/update-category/<int:category_id>", methods=["POST", "GET"])
@login_required
def update_category(category_id):
    """Update Category"""
    response = {
        "title": "Update Category",
        "update_category": True
    }
    form = CategoryForm()
    with session_maker() as db_session:
        update = db_session.get(Category, category_id)
        if form.validate_on_submit():
            try:
                update.title = request.form.get("title")
                db_session.commit()
                flash(message=f"Category: {update.title} Update!", category="success")
                return redirect(url_for("category.all_categories"))
            except Exception as ex:
                get_error_database_flash_message(error=ex, db_session=db_session)
                return render_template("category/create_category.html", form=form, response=response)
        else:
            get_errors(form)
    return render_template("category/create_category.html", response=response, form=form, update=update)


@category.route("/delete-category/<int:category_id>")
@login_required
def delete_category(category_id):
    """Delete Category"""
    with session_maker() as db_session:
        try:
            category_del = db_session.get(Category, category_id)
            title = category_del.title
            db_session.delete(category_del)
            db_session.commit()
            flash(message=f"Category {title} Deleted", category="info")
            return redirect(url_for("category.all_categories"))
        except Exception as ex:
            get_error_database_flash_message(error=ex, db_session=db_session)
            return redirect(url_for("category.all_categories"))
