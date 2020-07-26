# -*- coding:utf-8 -*-
import os
from flask import (render_template, request, flash,
                   escape, redirect, url_for, session, Blueprint, current_app)
from werkzeug.security import check_password_hash
from lsfd202201.utils import escape_quotes
from lsfd202201.models import Article
from lsfd202201.forms import UploadForm, AdminLoginForm, EditForm
from lsfd202201.extensions import db

articles_bp = Blueprint("articles", __name__)

@articles_bp.route('')
def articles():
    page = request.args.get('page', 1, int)
    all_articles = Article().query_all()
    if all_articles:
        article = Article().query_one(page)
        pagination = Article.query.order_by(
            Article.timestamp.desc()).paginate(page, 1)
        return render_template('articles.html',
                               this_article=article,
                               content=article["content"],
                               pagination=pagination)
    flash("No Articles! Please Upload one first!", "warning")
    return render_template("result.html", url=url_for("upload"))



@articles_bp.route('/upload')
def upload():
    form = UploadForm()
    return render_template('upload.html', form=form)


@articles_bp.route('/upload-result', methods=['POST'])
def upload_result():
    # get vars from upload page
    a = Article()
    name = escape(request.form['name'])
    password = request.form['password']
    date = escape(request.form['date'])
    title = escape(request.form['title'])
    content = request.form['content']
    id = len(a.query_all()) + 1
    config_password = current_app.config['PASSWORD']
    admin_password = current_app.config['ADMIN_PASSWORD']
    # password protection
    if not (check_password_hash(admin_password, password)
            or check_password_hash(config_password, password)):
        flash("Wrong Password", "warning")
        return render_template('result.html', url=url_for("upload"))
    # commit data
    article = Article(title=title, author=name, content=content, time=date,
                      id=id)
    db.session.add(article)
    db.session.commit()
    flash("Upload Success", "success")
    return render_template('result.html', url=url_for("articles"))

