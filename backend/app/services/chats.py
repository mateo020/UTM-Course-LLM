from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId
from ..core.database import get_database
from ..core.config import settings

class ProjectService:
    @staticmethod
    async def get_user_projects(user_id: str):
        """
        Get all projects for a user
        """
        try:
            print(f"Getting projects for user: {user_id}")
            db = await get_database()
            # Use db directly like in create_project
            projects = await db["projects"].find(
                {"user_id": user_id}
            ).to_list(length=None)
            
            print(f"Found projects: {projects}")
            
            # Convert ObjectId to string for JSON serialization
            for project in projects:
                project["id"] = str(project["_id"])
                del project["_id"]
                # Make sure name field exists
                if "project_name" in project:
                    project["name"] = project["project_name"]
                    del project["project_name"]
                
            return projects
        except Exception as e:
            print(f"Error in get_user_projects: {str(e)}")
            raise e

    @staticmethod
    async def delete_project(project_id: str):
        """
        Delete a project
        """
        db = await get_database()
        result = await db["projects"].delete_one(
            {"_id": ObjectId(project_id)}
        )
        if result.deleted_count:
            return {"message": "Project deleted successfully"}
        return {"message": "Project not found"}

    @staticmethod
    async def create_project(user_id: str, project_name: str, collaborators: List[str], is_public: bool):
        """
        Create a new project
        """
        try:
            db = await get_database()
            project = {
                "user_id": user_id,
                "name": project_name,  # Changed from project_name to name to match schema
                "created_at": datetime.utcnow(),
                "is_public": is_public,
                "collaborators": collaborators,
                "chat_history": []
            }
            result = await db["projects"].insert_one(project)
            
            # Return the created project
            created_project = await db["projects"].find_one({"_id": result.inserted_id})
            created_project["id"] = str(created_project["_id"])
            del created_project["_id"]
            
            return created_project
        except Exception as e:
            print(f"Error in create_project: {str(e)}")
            raise e

    @staticmethod
    async def get_one(project_id: str):
        """
        Get a project and all its attributes
        """
        try:
            db = await get_database()
            project = await db["projects"].find_one({"_id": ObjectId(project_id)})
            if project:
                # Convert ObjectId to string for JSON serialization
                project["id"] = str(project["_id"])
                del project["_id"]
                
                # Ensure all dates are serializable
                if "created_at" in project:
                    project["created_at"] = project["created_at"].isoformat()
                    
                print("Found project:", project)
                return project
            else:
                print("No project found with id:", project_id)
                return None
        except Exception as e:
            print(f"Error in get_one: {str(e)}")
            raise e

    @staticmethod
    async def save_chat(project_id: str, chat_history: List[Dict[str, Any]]):
        """
        Save the chat history for a project
        """
        try:
            db = await get_database()
            result = await db["projects"].update_one(
                {"_id": ObjectId(project_id)},
                {"$set": {"chat_history": chat_history}}
            )
            return {"message": "Chat history saved successfully"}
        except Exception as e:
            print(f"Error in save_chat: {str(e)}")
            raise e

