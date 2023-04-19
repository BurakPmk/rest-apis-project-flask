from db import db


class ItemsTagsModel(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(db.Integer,primary_key=True)
    item_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"),nullable=False)