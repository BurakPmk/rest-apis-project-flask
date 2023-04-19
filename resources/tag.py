from flask.views import MethodView
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError

from schemas import TagSchema,TagAndItemSchema
from models import TagModel,StoreModel,ItemModel,ItemsTagsModel
from db import db

blp = Blueprint("Tags","tags",description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):#get list of tags that are created under the store
        # tag = TagModel.query.filter_by(store_id=store_id).all()
        # return tag
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        if TagModel.query.filter(TagModel.store_id==store_id, TagModel.name == tag_data["name"]).first():
            abort(400,message="A tag with that name already exists in that store")
        tag = TagModel(**tag_data,store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message=e)

        return tag
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200,TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202,description="Deletes a tag if no item is tagged with it",example={"message":"Tag deleted"})
    @blp.alt_response(404,description="Tag not found.")
    @blp.alt_response(400,description="Returned if the tag is assigned to one or more items.In this case,the tag is not deleted.")
    def delete(self,tag_id):
        # if ItemsTagsModel.query.filter(tag_id==tag_id).first():
        #     abort(400,message="This tag associated with item(s), before deleting process please unlink from items the tag.") !!MY WAY

        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:#this part not exists in my way
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag deleted."}
        abort(400,message="Could not delete tag. Make sure tag is not associated with any items, then try again")#this to
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        
        try: 
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message="An error occured while inserting tag")

        return tag
    
    @blp.response(200,TagAndItemSchema)
    def delete(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occured while removing tag")

        return {"message":"Item Removed from tag","item":item,"tag":tag}