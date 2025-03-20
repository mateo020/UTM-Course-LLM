# from datetime import datetime
# from bson import ObjectId
# from ..core.database import get_database

# class UserService:
#     @staticmethod
#     async def get_all_users():
#         """
#         Get all users
#         """
#         db = await get_database()
#         users = await db["users"].find().to_list(length=None)
        
#         # Convert ObjectId to string for JSON serialization
#         for user in users:
#             user["id"] = str(user["_id"])
#             del user["_id"]
            
#         return users

#     @staticmethod
#     async def get_user(user_id: str):
#         """
#         Get a specific user
#         """
#         db = await get_database()
#         user = await db["users"].find_one({"_id": ObjectId(user_id)})
#         if user:
#             user["id"] = str(user["_id"])
#             del user["_id"]
#         return user 