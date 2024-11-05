from sqlmodel import SQLModel , Field 
from datetime import datetime , timezone 
from typing import Optional
from dataclasses import dataclass


@dataclass
class Voter:
    id : int
    username : str
    avatar : Optional[str] = None
    
    @property
    def avatar_url(self) -> str:
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        else:
            f"https://cdn.discordapp.com/embed/avatars/4.png"

class VoteHistory(SQLModel , table=True):
    id : Optional[int] = Field(default=None , primary_key=True)
    user_id : int
    username : str
    timestamp : datetime = Field(default=lambda : datetime.now(timezone.utc))    
    
class Vote(SQLModel , table=True):
    user_id : int = Field(primary_key=True , index=True)
    username : str
    timestamp : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))






    
    