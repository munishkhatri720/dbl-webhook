import aiohttp
import asyncio
from rich import print
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Vote:
    user_id : int
    timestamp : datetime
    username : str
    avatar : Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


async def main():
    headers = {'Authorization' : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoxLCJpZCI6IjEwMjE3MzI3MjI0NzkyMDIzMDQiLCJpYXQiOjE3MzA3OTI0NTN9.y_MJgw9nXYjggJAoykWqjMLriWMemTRKxdhwm0ZWfi0"}
    url = "https://discordbotlist.com/api/v1/bots/1021732722479202304/upvotes"
    async with aiohttp.ClientSession(headers=headers) as session:  
        async with session.get(url) as response:
            data = await response.json()
            votes = [Vote(**d) for d in data['upvotes']]
            votes.extend(votes)
            print(len(set(votes)))
            

async def test():
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization' : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoxLCJpZCI6IjEwMjE3MzI3MjI0NzkyMDIzMDQiLCJpYXQiOjE3MzA3OTI0NTN9.y_MJgw9nXYjggJAoykWqjMLriWMemTRKxdhwm0ZWfi0"}
        headers['x-dbl-signature'] = "test"
        payload = {
            'id' : 1,
            'username' :'manish',
            'avatar' : 'xyz'
            
        }
        async with session.post('http://localhost:5000/votes' , json=payload , headers=headers) as response:
            print(response.status)

if __name__ == '__main__':
    asyncio.run(test())
    