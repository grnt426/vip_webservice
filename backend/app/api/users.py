from fastapi import APIRouter


users = APIRouter()


mock = [
    {"first_name": "John", "last_name": "Doe"},
    {"first_name": "Lorem", "last_name": "Ipsum"},
]


@users.get("/users/")
async def read_users():
    return {'data': mock}
