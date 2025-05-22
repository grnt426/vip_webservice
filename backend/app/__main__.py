import uvicorn
from app.config import Settings


DEBUG = True
def main():
    print(f"Running with DEBUG={DEBUG}")
    try:
        uvicorn.run("app.server:app", host="0.0.0.0", port=Settings.BACKEND_PORT, reload=DEBUG)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
