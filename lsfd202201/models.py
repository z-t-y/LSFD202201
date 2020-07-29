"""
 models.py
 A python module for database storing
"""
from datetime import datetime
from . import db


class Article(db.Model):
    """
    A model for articles
    """
    __tablename__ = 'articles'
    # initialize columns
    title = db.Column(db.String(64), index=True)
    author = db.Column(db.String(64))
    date = db.Column(db.String(64))
    content = db.Column(db.Text(2048))
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    def __repr__(self) -> str:
        return '<Article %r>' % self.title

    def query_all(self) -> list:
        return self.query.all()

    def query_by_id(self, id: int) -> db.Model:
        return self.query.filter_by(id=id).first()

    def delete_by_id(self, id: int) -> None:
        article_to_delete = self.query.filter_by(id=id).first()
        db.session.delete(article_to_delete)
        db.session.commit()
