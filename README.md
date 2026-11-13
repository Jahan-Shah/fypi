Project Setup and Installation Guide
Prerequisites

Before running the project, make sure the following software is installed:

Python (3.8 or later recommended)
Node.js and pnpm
MongoDB Community Server
1. Install MongoDB Community Server

Download and install MongoDB Community Server from the official website:

https://www.mongodb.com/try/download/community

Make sure MongoDB is installed and running before proceeding.

Installation
2. Install Python Dependencies

Navigate to the project's root directory and install the required Python packages:

bash
pip install -r requirement.txt


If the pip command doesn't work, use:

bash
py -m pip install -r requirement.txt

3. Install Web Dependencies

Navigate to the web directory and install the frontend dependencies:

bash
cd web
pnpm install

Running the Project

The project consists of a Python backend and a web frontend. Both must run simultaneously.

4. Start the Backend

Open a terminal in the project's root directory and run:

bash
python index.py

5. Start the Frontend

Open another terminal and navigate to the web directory:

bash
cd web
pnpm dev

Project Structure
text
project-root/
│
├── index.py
├── requirement.txt
├── web/
│   └── ... (Frontend application)
│
└── ... (Other project files)

Running Checklist
MongoDB Community Server is installed and running.
Python dependencies are installed.
Frontend dependencies are installed using pnpm install.
Backend is running using python index.py.
Frontend is running using pnpm dev.
Notes
Ensure MongoDB is running before starting the backend.
Run the backend and frontend in separate terminals.
Keep both terminals open while using the application.
