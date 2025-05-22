# Backend
Python, FastAPI backend.

## Dependencies
Activate the python environment and use pip to install required packages. Consider migrating to a modern package manager
(poetry)?

```bash
pip install -r requirements.txt
```

## Starting the backend
Currently the application backend is run by the following procedure. There is no database yet. 
1. Open shell in `backend` directory and activate python environment.
2. Run command:
```bash
python -m app
```

## Backend Structure

```
$ tree "backend"
backend
├── __main__.py  # Startup script. Starts uvicorn.
├── server.py  # FastAPI application.
├── api  # Package with all APIRouters and database.
│   ├── router.py  # Master APIRouter which includes all other APIRouters.
│   ├── users.py  # Other routers for example.
│   │   └── db  # Will contain database CRUD, models, and such in the future.
│   ├── application.py  # FastAPI application configuration.
│   └── lifespan.py  # Contains actions to perform on startup and shutdown.
├── config  # Package with configuration data.
│   └── settings.py  # Contains settings information.
└── tests  # Package with backend testing in future.
```

## API

### Routing Conventions

### Database
Intention is to use AWS DynamoDB as NoSQL database. Database scripts and functions will be located in backend/app/api/db
and be called from the API end points. 

## Testing
To be implemented. 
