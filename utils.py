import aiohttp
from typing import TYPE_CHECKING , Optional
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
if TYPE_CHECKING:
    from models import Voter
from datetime import datetime , timezone , timedelta    
from discord import Webhook  , Embed  , Color
from dataclasses import dataclass
from models import Vote


@dataclass
class VoteClass:
    user_id : int
    timestamp : datetime
    username : str
    avatar : Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

async def fetch_upvotes(db_session : AsyncSession) -> None:
    headers = {'Authorization' : f"{os.getenv('WEBHOOK_AUTH')}"}
    url = "https://discordbotlist.com/api/v1/bots/1021732722479202304/upvotes"
    async with aiohttp.ClientSession(headers=headers) as session:  
        async with session.get(url) as response:
            data = await response.json()
            votes = [VoteClass(**d) for d in data['upvotes']]
            print(f"[-] Fetched {len(votes)} vote from the api.")
            for vote in votes:
                result = await db_session.execute(select(Vote).where(Vote.user_id == vote.user_id))
                existing_vote = result.scalars().first()

                if existing_vote:
                    existing_vote.timestamp = vote.timestamp + timedelta(hours=12)
                    print(f"[-] Increased timestamp of fetched vote from the api.")
                else:
                    new_vote = Vote(
                        user_id=vote.user_id,
                        username=vote.username,
                        timestamp=vote.timestamp + timedelta(hours=12)
                    )
                    db_session.add(new_vote)
                    print("[-] Added fetched vote from api  to database.")
            await db_session.commit()
             
            

async def post_webhook( voter : "Voter" , total_upvotes : int = None):
    async with aiohttp.ClientSession() as session:
        wb = Webhook.from_url(os.getenv("DISCORD_WEBHOOK") , session=session)
        embed = Embed(color=Color.dark_theme())
        embed.set_author(name=voter.username  , icon_url=voter.avatar_url)
        embed.title = "Thank you for voting for Hade#7267"
        embed.url = "https://discordbotlist.com/bots/hade"
        embed.description = f"User: ` {voter.username} (id: {voter.id})` just voted on discordbotlist for Hade ! 🎉\n"
        embed.description += f"* Total upvotes: `{total_upvotes}`\n"
        next_vote = datetime.now(timezone.utc) + timedelta(hours=12)
        embed.description += f"* Next upvote in: <t:{int(next_vote.timestamp())}:F>\n"
        embed.set_thumbnail(url=voter.avatar_url)
        await wb.send(embed=embed , username="Hade UpVotes" , avatar_url="https://cdn.discordapp.com/avatars/1021732722479202304/a_57217a0e55762896f49cd2365d30f1d8.png?size=1024")
        
        