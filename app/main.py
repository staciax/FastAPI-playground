from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()


# https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=('*'),
    allow_credentials=True,
    allow_methods=('GET', 'POST', 'PUT', 'DELETE'),
    allow_headers=('*'),
)


@app.get('/', include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({'message': 'OK'})
