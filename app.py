from fastapi import FastAPI,Request,HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import uvicorn
import firebase_admin
from firebase_admin import credentials,auth
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
class DB:
    fb_app = None

db = DB()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)
@app.on_event('startup')
def intialize_firebase_app():
    cred = credentials.Certificate('keys.json')
    db.fb_app = firebase_admin.initialize_app(cred)
    print('here')

class FirebaseIdTokenBearer(HTTPBearer):
    def __init__(self,auto_error:bool=True):
        super(FirebaseIdTokenBearer,self).__init__(auto_error=auto_error)
    
    async def __call__(self,request:Request):
        credentials:HTTPAuthorizationCredentials = await super(FirebaseIdTokenBearer,self).__call__(request)
        if credentials:
            if not credentials.scheme=="Bearer":
                raise HTTPException(status_code=403,detail="Invalid authentication scheme")
            if not auth.verify_id_token(credentials.credentials):
                raise HTTPException(status_code=403,detail="Invalid or expired token")
            pprint(auth.verify_id_token(credentials.credentials))
            return credentials.credentials
        else:
            raise HTTPException(status_code=403,detail="Invalid Authorization Code")

@app.get('/',dependencies=[Depends(FirebaseIdTokenBearer())])
def test():
    return {'test':'success'}

if __name__=='__main__':
    uvicorn.run("app:app",reload=True)