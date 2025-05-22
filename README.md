# VIP Guild

This project is a web application for managing large Guild Wars 2 guild conglomerates. It includes both a backend and a frontend component.

## Backend Setup

1. **Install Dependencies**
   
   Navigate to the `backend` directory and install the dependencies using Poetry:
   ```bash
   cd backend
   poetry install
   ```

2. **Run the Backend**

   Start the backend server using Uvicorn:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
   The backend will be accessible at `http://localhost:8080`.

## Frontend Setup

1. **Install Dependencies**

   Navigate to the `frontend` directory and install the dependencies using npm:
   ```bash
   cd frontend
   npm install
   ```

2. **Run the Frontend**

   Start the frontend development server:
   ```bash
   npm run dev
   ```
   The frontend will be accessible at `http://localhost:5173`.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, TypeScript, Vite, Material UI

For more detailed information, refer to the `backend/README.md` and `frontend/README.md` files.

## Tech stack, design and structure
See [backend/README.md](https://github.com/GrantKurtzTrueAd/dashboard/blob/master/backend/README.md) and [frontend/README.me](https://github.com/GrantKurtzTrueAd/dashboard/blob/master/frontend/README.md)

Also see following templates for examples of stack implementation:
- https://github.com/mongodb-developer/farm-stack-to-do-app
- https://github.com/fastapi/full-stack-fastapi-template/tree/master
- 
