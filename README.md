# Farmer Based Advisory System

A FastAPI backend with a MySQL database. SQLAlchemy defines the models. Alembic manages the database schema.

## Current state

- A FastAPI app in `app/main.py`.
- Two routes: `GET /` (health check) and `POST /seed-data` (adds two roles and one test user).
- Models in `app/model/`: `User`, `Role`, and the `user_role` link table.
- One Alembic migration in `alembic/versions/`.
- The app applies all migrations when it starts.

## Requirements

- Python 3.14 (the project was made with 3.14.7)
- [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) 8 or a compatible server [CLICK ME](https://dev.mysql.com/downloads/mysql/)
- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) (to create the database) [CLICK ME](https://dev.mysql.com/downloads/workbench/)
- Git

## Set up the project

1. Clone the repository and go into the folder.

   ```bash
   git clone https://github.com/fvnju/FarmerBasedAdvisorySystem.git
   cd FarmerBasedAdvisorySystem
   ```

2. Create a virtual environment.

   ```bash
   python3.14 -m venv env
   ```

3. Activate the virtual environment.

   ```bash
   # macOS and Linux
   source env/bin/activate

   # Windows (PowerShell)
   env\Scripts\Activate.ps1
   ```

4. Install the packages.

   ```bash
   pip install -r requirements.txt
   ```

5. Create the MySQL database in MySQL Workbench. Use the name that you put in `DATABASE_URL` in step 6.

   1. Open MySQL Workbench.
   2. Click a connection to your local MySQL server. Enter the password for the `root` user.
   3. Click **File** > **New Query Tab**.
   4. Paste this SQL into the tab.

      ```sql
      CREATE DATABASE IF NOT EXISTS testing
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_unicode_ci;

      SHOW DATABASES LIKE 'testing';
      ```

   5. Click the lightning bolt icon to run all statements.
   6. Make sure the result grid shows one row with the name `testing`.

6. Create a file named `.env` in the project root. Add the database URL.

   ```env
   DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/testing
   ```

   - Replace `<user>` and `<password>` with your MySQL login.
   - The `.env` file is in `.gitignore`. Do not commit it.
   - If the password has special characters, encode them as a URL (for example, `@` becomes `%40`).

7. Start the server.

   ```bash
   python app/main.py
   ```

   The server starts on `http://127.0.0.1:8000`. Auto-reload is off. To apply a code change, stop the server and start it again.

## Check that the setup is correct

1. Open `http://127.0.0.1:8000/` in a browser. The response is:

   ```json
   {"message": "School Management System is running!"}
   ```

2. Open `http://127.0.0.1:8000/docs` to see the interactive API documentation.

3. Optional: add test data.

   ```bash
   curl -X POST http://127.0.0.1:8000/seed-data
   ```

   Run this command one time only. A second run fails because the role names and the user name must be unique.

## Database migrations

The app runs `alembic upgrade head` when it starts. If the `alembic/versions/` folder is empty, the app first creates an initial migration from the models.

You can also run Alembic by hand:

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after you change a model
alembic revision --autogenerate -m "describe the change"

# Undo the last migration
alembic downgrade -1
```

New models must be imported in `app/model/__init__.py` and in `alembic/env.py`. If they are not, Alembic does not detect them.

## Project layout

```text
.
├── alembic/              # Migration scripts and Alembic settings
│   ├── env.py
│   └── versions/
├── alembic.ini
├── app/
│   ├── main.py           # FastAPI app and routes
│   ├── database.py       # Engine, session, and Base class
│   └── model/            # SQLAlchemy models
├── requirements.txt
└── .env                  # Local settings (not in Git)
```

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `No DATABASE_URL in env` | Make sure the `.env` file is in the project root and has `DATABASE_URL`. |
| `Can't connect to MySQL server` | Start the MySQL server. Check the host, the port, and the login in `DATABASE_URL`. |
| `Unknown database 'testing'` | Create the database in MySQL Workbench (step 5). |
| `cryptography package is required` | Run `pip install -r requirements.txt` again. |
