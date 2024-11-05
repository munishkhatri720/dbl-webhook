from fastapi import FastAPI , Request , Response , HTTPException , Depends , BackgroundTasks
from fastapi.responses import JSONResponse
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
load_dotenv()
from models import SQLModel , Voter , Vote as VoteDBModel , VoteHistory
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession , async_sessionmaker
from datetime import datetime , timedelta , timezone
from sqlalchemy import select
from rich import print
from utils import post_webhook , fetch_upvotes



engine = create_async_engine(os.getenv("DATABASE_URL") , echo=False , future = True)
async_session = async_sessionmaker(bind=engine , class_=AsyncSession ,  expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def lifespan(app : FastAPI) -> AsyncGenerator:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        print("[-] Generated Schema ...")
    yield
        


app = FastAPI(debug=True , lifespan=lifespan)


async def background_task(voter : Voter , session : AsyncSession) -> None:
    results = await session.execute(select(VoteDBModel).where(VoteHistory.user_id == voter.id))
    await post_webhook(voter , len(results.scalars().all()))
    await fetch_upvotes(db_session=session)
    

@app.post('/votes')
async def vote(request: Request,background_tasks: BackgroundTasks ,  session: AsyncSession = Depends(get_session)) -> Response:
    auth = request.headers.get("authorization", None)
    if not auth or auth != os.getenv("WEBHOOK_AUTH"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not request.headers.get('x-dbl-signature', None):
        raise HTTPException(status_code=400, detail="No signature provided")
    data = await request.json()
    voter = Voter(**data)  
    result = await session.execute(select(VoteDBModel).where(VoteDBModel.user_id == voter.id))
    vote = result.scalars().first()
    if vote:
        vote.timestamp = datetime.now(timezone.utc) + timedelta(hours=12 , minutes=5)
        print("[-] Updated old vote data")
    else:
        session.add(VoteDBModel(user_id=voter.id, username=voter.username, timestamp=datetime.now(timezone.utc) + timedelta(hours=12 , minutes=5)))
        print("[-] Added new vote data.")
    session.add(VoteHistory(user_id=voter.id , username=voter.username , timestamp=datetime.now(timezone.utc)))    
    await session.commit()  
    background_tasks.add_task(background_task , voter ,  session)
    return Response(status_code=200)

@app.get('/votes/{user_id}/check')
async def vote_check(user_id : int , session : AsyncSession = Depends(get_session)) -> Response:
    result = await session.execute(select(VoteDBModel).where(VoteDBModel.user_id == user_id))
    vote =  result.scalars().first()
    if vote and vote.timestamp.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        return JSONResponse({'voted': True} , status_code=200)
    
    if vote and vote.timestamp.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
    
        return JSONResponse({'voted': False} , status_code=200)
    
    return JSONResponse({'voted' : False} , status_code=404)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app' , host="0.0.0.0" , port=2335)
    
    
    