from pydantic import BaseModel, Field
from typing import List, Optional

class User(BaseModel):
    id: str
    username: str
    groups: List[str] = Field(default_factory=list)
    
    def can_access(self, required_group: Optional[str]) -> bool:
        if not required_group:
            return True
        return required_group in self.groups
