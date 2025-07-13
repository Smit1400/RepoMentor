import uuid
from typing import List
from pydantic import BaseModel, Field

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    project_name: str = Field(...)
    project_description: str = Field(...)
    project_git_repo: str = Field(...)
    project_git_branch: str = Field(...)
    project_end_date: str = Field(...)
    project_index_path: List = Field(...)
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "project_name": "Tic Tac Toe",
                "project_description": "Game",
                "project_git_repo": "",
                "project_git_branch": "",
                "project_end_date": "08/13/2025",
                "project_index_path": []
            }
        }