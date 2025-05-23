# VIP Guild Dashboard - Local Development Setup (Windows 11)

This guide will walk you through setting up the VIP Guild Dashboard project for local development on a Windows 11 machine.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Windows 11:** This guide is specific to Windows 11.
2.  **Git:** For version control.
3.  **PyCharm (Recommended):** A Python IDE. Alternatively, any code editor will work.

## Step 1: Install Required Software

### 1.1 Install Git

If you don't have Git installed, download and install it from [git-scm.com](https://git-scm.com/download/win). During installation, accept the default options, but ensure that "Git Bash Here" and "Git GUI Here" are selected for Windows Explorer integration, and that "Git Credential Manager" is selected for authentication. This will help with authenticating to GitHub.

### 1.2 Install Python

1.  **Download Python:** Go to the official Python website at [python.org/downloads/windows/](https://python.org/downloads/windows/). Download the latest stable Python 3.11.x installer (Windows installer 64-bit).
2.  **Run the Installer:**
    *   Double-click the downloaded installer.
    *   **Important:** Check the box that says "Add Python 3.11 to PATH" at the bottom of the first installer screen.
    *   Click "Install Now".
    *   Once the installation is complete, you can close the installer.
3.  **Verify Installation:** Open a new Command Prompt or PowerShell window and type:
    ```bash
    python --version
    pip --version
    ```
    You should see the installed Python and pip versions printed.

### 1.3 Install Node.js and npm

1.  **Download Node.js:** Go to the official Node.js website at [nodejs.org](https://nodejs.org/). Download the LTS (Long Term Support) version recommended for most users.
2.  **Run the Installer:** Double-click the downloaded MSI file and follow the installation prompts. The default options are usually fine. npm (Node Package Manager) is included with Node.js.
3.  **Verify Installation:** Open a new Command Prompt or PowerShell window and type:
    ```bash
    node -v
    npm -v
    ```
    You should see the installed Node.js and npm versions.

### 1.4 Install PyCharm (Recommended)

1.  **Download PyCharm:** Go to the JetBrains website at [jetbrains.com/pycharm/download/](https://jetbrains.com/pycharm/download/). Download the PyCharm Community Edition (it's free).
2.  **Run the Installer:** Follow the installation prompts. Default options are usually fine.

## Step 2: Clone the Repository

1.  **Open Git Bash or Terminal.**
2.  **Navigate to your desired project directory.**
3.  **Clone the repository using HTTPS:**
    ```bash
    git clone https://github.com/grnt426/vip_webservice.git
    ```
    You may be prompted for your GitHub username and password (or a Personal Access Token if you have 2FA enabled).
4.  **Enter the project directory:**
    ```bash
    cd vip_webservice
    ```

## Step 3: Configure Guild Wars 2 API Key

To fetch data from the Guild Wars 2 API, you need to provide an API key.

1.  **Obtain a GW2 API Key:**
    *   Go to [https://account.arena.net/applications](https://account.arena.net/applications).
    *   Log in with your Guild Wars 2 account.
    *   Click "New Key".
    *   Give your key a **Name** (e.g., "VIP Dashboard Dev").
    *   Ensure the following **Permissions** are checked:
        *   `account`
        *   `guilds` (This will allow access to guild data for guilds your account is a member of)
        *   `characters`
        *   `wallet`
        *   `unlocks`
        *   `progression`
    *   Click "Create API Key".
    *   **Important:** Copy the generated API key immediately. You will not be able to see it again.
2.  **Create the `.secrets` file:**
    *   Navigate to the `backend` directory within your cloned `vip_webservice` project folder.
    *   Create a new file named `.secrets` (note the leading dot and no extension).
3.  **Add your API Key to `.secrets`:**
    *   Open the `.secrets` file in a text editor.
    *   Add your copied API key in the following format:
        ```
        API_KEY=YOUR_COPIED_GW2_API_KEY_GOES_HERE
        ```
    *   Replace `YOUR_COPIED_GW2_API_KEY_GOES_HERE` with the actual key you copied from ArenaNet.
    *   Save the file.

**Note on API Key Scope:** The Guild Wars 2 API key will only grant access to data for guilds that the account associated with the API key is currently a member of. If the application is configured to track specific guilds (as defined in `backend/app/api/guilds.py`), data will only be fetched for those guilds *if* your API key's account is a member of them. You may not see data for all configured guilds if your account isn't in all of them.

## Step 4: Set Up Backend (Python/FastAPI)

1.  **Navigate to backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a Python Virtual Environment (PyCharm can also help with this):**
    ```bash
    python -m venv .venv
    ```
3.  **Activate the Virtual Environment:**
    *   (See previous activation instructions for PowerShell, CMD, Git Bash)
    *   Your terminal prompt should change to indicate the active environment.
4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Step 5: Set Up Frontend (React/Vite)

1.  **Navigate to frontend directory:** (from project root)
    ```bash
    cd frontend
    ```
2.  **Install Node.js Dependencies:**
    ```bash
    npm install
    ```

## Step 6: Running the Application (Docker Recommended for Development)

1.  **Install Docker Desktop:**
    *   Download from [docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/). Enable WSL 2 if prompted.
2.  **Build and Run with Docker Compose:**
    *   In the project root directory (`vip_webservice`):
        ```bash
        docker-compose up --build
        ```
    *   This builds and starts both services.
3.  **Access the Application:** [http://localhost:8080](http://localhost:8080)

## Step 7: Development Workflow

*   **Backend Changes:** Code in `backend/app` is volume-mounted. Uvicorn reloads on Python file changes.
*   **Frontend Changes (Live Reload):**
    1.  New terminal: `cd frontend`
    2.  Run Vite: `npm run dev` (usually [http://localhost:5173](http://localhost:5173))
    3.  Backend API at `http://localhost:8080/api/...` is proxied.
    *   Rebuild Docker for production frontend: `docker-compose up --build -d`

## Troubleshooting

*   **Python/Node not found:** Verify PATH, restart terminal.
*   **Pip permission errors:** Use virtual environments. Or run terminal as admin (less ideal).
*   **GitHub Authentication Issues:** Ensure Git Credential Manager is working or consider using a GitHub Personal Access Token for HTTPS authentication if you have 2FA enabled.
*   **Docker Issues:**
    *   Docker Desktop running? WSL 2 enabled?
    *   Check `docker-compose up` output for errors (port conflicts, Dockerfile/docker-compose.yml issues).

Happy Coding!

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
