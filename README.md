# Farmer Based Advisory System

The backend for a smart farmer advisory system. It uses FastAPI, a MySQL database, SQLAlchemy models, and Alembic migrations.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Set up the project on macOS](#set-up-the-project-on-macos)
- [Set up the project on Windows](#set-up-the-project-on-windows)
- [Create the database](#create-the-database)
- [Create the admin user](#create-the-admin-user)
- [API documentation](#api-documentation)
- [Log in and use the API](#log-in-and-use-the-api)
- [Roles and privileges](#roles-and-privileges)
- [Settings](#settings)
- [Run the tests](#run-the-tests)
- [Project layout](#project-layout)
- [Database models](#database-models)
- [Audit trail](#audit-trail)
- [Database migrations](#database-migrations)
- [Troubleshooting](#troubleshooting)

## Features

- Insert, update, delete, delete-all, search, and pagination for each table, under `/api/v1`.
- Login with access tokens (JWT) and refresh tokens. Each refresh replaces the refresh token.
- Registration for farmers, password reset, and verification of the email and the phone number.
- Role-based access control (RBAC). Each operation needs a privilege, for example `farms.update`.
- Data scope. A farmer sees only their own data. An extension agent also sees the data of the farmers assigned to the agent.
- An audit trail of each change, login, and failed login.
- The app applies the database migrations and creates the roles when it starts.

## Requirements

- Python 3.14. The project was made with 3.14.7.
- [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) 8 or a compatible server.
- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/), to create the database. See the [MySQL Workbench tutorial](docs/mysql-workbench-tutorial/index.html).
- Git.

## Set up the project on macOS

Run these commands in the Terminal app.

1. Clone the repository and go into the folder.

   ```bash
   git clone https://github.com/fvnju/FarmerBasedAdvisorySystem.git
   cd FarmerBasedAdvisorySystem
   ```

2. Create and activate a virtual environment.

   ```bash
   python3.14 -m venv env
   source env/bin/activate
   ```

   The prompt starts with `(env)` when the environment is active. Activate it again each time you open a new terminal.

3. Install the packages.

   ```bash
   pip install -r requirements.txt
   ```

4. Create the database. See [Create the database](#create-the-database).

5. Create the `.env` file from the example.

   ```bash
   cp .env.example .env
   ```

6. Make a secret for the access tokens.

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

7. Open `.env` and set these values. See [Settings](#settings) for all values.

   - `DATABASE_URL`: your MySQL user, password, and database name.
   - `JWT_SECRET`: the secret from step 6.
   - `SEED_ADMIN_PASSWORD`: the password for the first admin.

8. Start the server.

   ```bash
   python app/main.py
   ```

   The server starts on `http://127.0.0.1:8000`. It applies the migrations and creates the roles. Auto-reload is off. To apply a code change, stop the server with `Ctrl+C` and start it again.

9. [Create the admin user](#create-the-admin-user).

## Set up the project on Windows

Run these commands in PowerShell.

1. Clone the repository and go into the folder.

   ```powershell
   git clone https://github.com/fvnju/FarmerBasedAdvisorySystem.git
   cd FarmerBasedAdvisorySystem
   ```

2. Create and activate a virtual environment.

   ```powershell
   py -3.14 -m venv env
   .\env\Scripts\Activate.ps1
   ```

   If PowerShell says that running scripts is disabled, run this command one time. Then activate the environment again.

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

   The prompt starts with `(env)` when the environment is active. Activate it again each time you open a new terminal.

3. Install the packages.

   ```powershell
   pip install -r requirements.txt
   ```

   The package `uvloop` does not work on Windows, so pip does not install it. The server works without it.

4. Create the database. See [Create the database](#create-the-database).

5. Create the `.env` file from the example.

   ```powershell
   Copy-Item .env.example .env
   ```

6. Make a secret for the access tokens.

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

7. Open `.env` in a text editor (for example `notepad .env`) and set these values. See [Settings](#settings) for all values.

   - `DATABASE_URL`: your MySQL user, password, and database name.
   - `JWT_SECRET`: the secret from step 6.
   - `SEED_ADMIN_PASSWORD`: the password for the first admin.

8. Start the server.

   ```powershell
   python app\main.py
   ```

   The server starts on `http://127.0.0.1:8000`. It applies the migrations and creates the roles. Auto-reload is off. To apply a code change, stop the server with `Ctrl+C` and start it again.

9. [Create the admin user](#create-the-admin-user).

## Create the database

Do these steps one time, on macOS or on Windows.

1. Open MySQL Workbench.
2. Click the connection to your local MySQL server. Enter the password for the `root` user.
3. Click **File** > **New Query Tab**.
4. Paste this SQL into the tab.

   ```sql
   CREATE DATABASE IF NOT EXISTS smartfarm
   CHARACTER SET utf8mb4
   COLLATE utf8mb4_unicode_ci;

   SHOW DATABASES LIKE 'smartfarm';
   ```

5. Click the lightning bolt icon to run all statements.
6. Make sure that the result grid shows one row with the name `smartfarm`.

You can use another name. The [MySQL Workbench tutorial](docs/mysql-workbench-tutorial/index.html) uses `testing`. The database name must be the same as the name at the end of `DATABASE_URL`:

```env
DATABASE_URL=mysql+pymysql://root:<password>@localhost:3306/smartfarm
```

If the password has special characters, encode them for a URL. For example, `@` becomes `%40`.

## Create the admin user

The admin user is `johndoe`. Its password is the value of `SEED_ADMIN_PASSWORD` in `.env`.

1. Make sure that `SEED_ADMIN_PASSWORD` is set in `.env`. If it is empty, the server makes a random password and prints it in the terminal one time.
2. Start the server.
3. Send `POST /seed-data`. Use one of these methods.

   - In a browser, open `http://127.0.0.1:8000/docs`. Open **POST /seed-data**, click **Try it out**, and click **Execute**.
   - On macOS:

     ```bash
     curl -X POST http://127.0.0.1:8000/seed-data
     ```

   - On Windows (PowerShell):

     ```powershell
     Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/seed-data
     ```

4. The response is `{"message": "Data seeded successfully!"}`.
5. Log in as `johndoe`. See [Log in and use the API](#log-in-and-use-the-api).

Rules for `/seed-data`:

- It is open until an active admin exists. After that, it needs a login with the privilege `rbac.manage`.
- You can run it again as an admin, for example after you add a privilege in `app/seed.py`. It does not add duplicate rows.
- Farmers can register before the admin exists. If a farmer took the name `johndoe`, the seed stops with an error. Delete that user or give it the admin role.

To give the admin role to another user, log in as the admin and send `PATCH /api/v1/users/{id}` with the role IDs, for example `{"role_ids": [1]}`. `GET /api/v1/roles` shows the role IDs.

## API documentation

Start the server, then open one of these addresses in a browser.

| Address | What it shows |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Swagger UI. You can send requests from the browser. |
| `http://127.0.0.1:8000/redoc` | ReDoc. The same documentation in a format that is easier to read. |
| `http://127.0.0.1:8000/openapi.json` | The OpenAPI document. Import it into Postman or a code generator. |
| `http://127.0.0.1:8000/health` | The health check. It shows if the API and the database work. |

The documentation groups the routes by resource. Each resource has these routes:

| Method and path | Operation |
| --- | --- |
| `GET /api/v1/<resource>` | List, search, and filter. Query parameters: `q` (search text), `page`, `size` (1 to 100), `sort` (for example `-created_at`), `include_total`, and the filters of the resource. |
| `GET /api/v1/<resource>/{id}` | Get one record. |
| `POST /api/v1/<resource>` | Insert a record. |
| `PATCH /api/v1/<resource>/{id}` | Update the fields that you send. |
| `DELETE /api/v1/<resource>/{id}` | Delete one record. |
| `DELETE /api/v1/<resource>?confirm=true` | Delete all records. Only the admin can do this. Records that other records use are skipped. |

Some resources have fewer routes. For example, the audit log is read-only, and a consent record cannot be changed.

For search as the user types, send `GET /api/v1/<resource>?q=<text>` after each key. Wait about 300 ms after the last key before you send the request. For infinite scroll, set `include_total=false`. The response is then faster, and `has_next` shows if more pages exist.

## Log in and use the API

### In Swagger UI

1. Open `http://127.0.0.1:8000/docs`.
2. Open **POST /api/v1/auth/login** and click **Try it out**.
3. Enter the login and the password, and click **Execute**.

   ```json
   {"login": "johndoe", "password": "<SEED_ADMIN_PASSWORD>"}
   ```

4. Copy the `access_token` from the response.
5. Click **Authorize** at the top of the page. Paste the token and click **Authorize**.
6. Swagger now sends the token with each request.

The access token expires after 15 minutes. Send the `refresh_token` to **POST /api/v1/auth/refresh** to get new tokens, or log in again.

### From a client

Send the access token in the `Authorization` header of each request:

```text
Authorization: Bearer <access_token>
```

Authentication routes, under `/api/v1/auth`:

| Route | Login needed | What it does |
| --- | --- | --- |
| `POST /register` | No | Registers a farmer. Sends a code to verify the email. |
| `POST /login` | No | Logs in with a username, an email, or a phone number. Returns the tokens. |
| `POST /refresh` | No | Returns new tokens. The old refresh token stops working. |
| `POST /logout` | No | Stops the session of a refresh token. |
| `POST /logout-all` | Yes | Stops all sessions of the user. |
| `GET /me`, `PATCH /me` | Yes | Shows or changes the account. The response also has the privileges and modules of the user, so the client can show or hide menus. |
| `POST /change-password` | Yes | Changes the password. All other sessions stop. |
| `POST /password-reset/request` | No | Sends a reset token. |
| `POST /password-reset/confirm` | No | Sets a new password with the reset token. |
| `POST /verification/request` | Yes | Sends a code to the email or the phone. |
| `POST /verification/confirm` | Yes | Verifies the email or the phone with the code. |

Security rules:

- After 5 failed logins in 15 minutes, the account is locked for 15 minutes. The API returns 429.
- If a used refresh token is sent again, all sessions of that user stop.
- The database keeps only hashes of passwords and tokens.

The app does not send email or SMS yet. In development, `app/integration/notifier.py` writes reset tokens and verification codes to the server terminal. For production, connect an email and SMS provider in that file.

## Roles and privileges

The app creates these roles when it starts. The privileges for each role are in `app/seed.py`.

| Role | Can do | Sees the data of |
| --- | --- | --- |
| `admin` | All operations, including delete-all. | All users. |
| `agronomist` | Reviews knowledge documents, responds to advisory requests, verifies field observations, and manages weather policies, prices, regions, and crops. | All farmers. |
| `extension_agent` | Registers farmers, manages farms, asks for advice for a farmer, and records consent. | Self and the farmers assigned to the agent. |
| `farmer` | Manages own farms, asks for advice, gives feedback, and records own consent. | Self only. |

Rules:

- A record that you cannot see returns 404, not 403.
- If an extension agent registers a farmer with `POST /api/v1/users`, the farmer gets the `farmer` role and is assigned to the agent.
- Only a user with `users.assign_roles` can set `role_ids`.
- You cannot delete or deactivate your own account or the last active admin.

## Settings

The app reads its settings from `.env`. `.env.example` shows all settings.

| Setting | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | none (required) | The MySQL connection. |
| `JWT_SECRET` | random | The secret for the access tokens. If it is empty, each restart logs out all users. |
| `ACCESS_TOKEN_MINUTES` | `15` | Life of an access token. |
| `REFRESH_TOKEN_DAYS` | `14` | Life of a refresh token. |
| `ONE_TIME_TOKEN_MINUTES` | `30` | Life of a reset token or a verification code. |
| `LOGIN_MAX_FAILURES` | `5` | Failed logins before the account is locked. |
| `LOGIN_LOCKOUT_MINUTES` | `15` | Time that the account stays locked. |
| `VERIFICATION_MAX_FAILURES` | `5` | Wrong codes before a verification code stops working. |
| `SEED_ADMIN_PASSWORD` | random | Password of the first admin. |
| `CORS_ORIGINS` | `["http://localhost:5173","http://localhost:3000"]` | Addresses of the web client, as a JSON list. |
| `PRIVACY_POLICY_VERSION` | `1.0` | Version of the privacy text that the registration form shows. |

Do not commit `.env`. It is in `.gitignore`.

## Run the tests

The tests use a database in memory. They do not change your MySQL database.

```bash
# macOS
env/bin/pytest -q

# Windows (PowerShell)
.\env\Scripts\pytest -q
```

## Project layout

A request goes through the layers in this order: route, controller, service, repository, model.

```text
.
├── alembic/              # Migration scripts and Alembic settings
├── app/
│   ├── main.py           # FastAPI app, start-up, and middleware
│   ├── database.py       # Engine, session, and Base class
│   ├── audit.py          # Audit trail
│   ├── seed.py           # Modules, privileges, roles, and the first admin
│   ├── core/             # Settings, security, errors, and error handlers
│   ├── model/            # SQLAlchemy models
│   ├── schema/           # Pydantic schemas for requests and responses
│   ├── repository/       # Database queries: search, filters, pagination, data scope
│   ├── service/          # Business rules, privileges, and transactions
│   ├── controller/       # Converts schemas to data for the services, and back
│   ├── route/            # HTTP routes
│   ├── integration/      # External services, for example email and SMS
│   └── util/             # Small helpers
├── docs/                 # MySQL Workbench tutorial
├── tests/                # Tests (pytest)
├── .env.example          # Example settings
└── requirements.txt
```

## Database models

| Area | Tables | Purpose |
| --- | --- | --- |
| Authentication | `users`, `refresh_tokens`, `one_time_tokens` | Accounts, login sessions, and tokens for verification and password reset. Tokens are stored as hashes. |
| Authorization | `roles`, `user_role`, `modules`, `role_modules`, `privileges`, `role_privileges` | Role-based access. A privilege has a code such as `farms.update`. |
| Data protection | `consent_records`, `agent_farmer_assignments`, `audit_logs` | Consent history, extension agent access to farmers, and a log of sensitive actions. |
| Farm profile | `regions`, `crops`, `farms`, `farm_resources`, `soil_records`, `crop_cycles` | Farm data. An empty column means "unknown". Soil values keep their provenance. |
| Knowledge | `knowledge_documents`, `document_chunks` | Crop guidance with crop, region, version, and review status. Only approved documents are for retrieval. |
| Weather and cost | `weather_forecasts`, `freshness_policies`, `price_records` | Forecasts with issue and retrieval times, the maximum forecast age for each action, and dated prices. |
| Advisory | `advisory_requests`, `advisory_responses`, `advisory_explanations`, `advisory_citations` | The question, the rule decision, the model text, and the cited passages. A new explanation does not change the decision. |
| Feedback and alerts | `advisory_feedback`, `field_observations`, `alerts` | What the farmer did, later observations, and weather action alerts. |

The app creates four roles: `admin`, `farmer`, `extension_agent`, and `agronomist`. See [Roles and privileges](#roles-and-privileges).

### Table reference

All model files are in `app/model/`. The fixed values for enum columns are in `app/model/enums.py`. Tables with `created_at` and `updated_at` get these columns from `TimestampMixin` in `app/model/mixins.py`.

#### Authentication

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `users` | `User`, `user.py` | `username`, `email`, and `phone_number` are unique. `hashed_password` keeps a hash, never the password. `is_active = false` blocks login without a delete. `email_verified_at` and `phone_verified_at` are empty until the user confirms them. |
| `refresh_tokens` | `RefreshToken`, `auth_token.py` | One row for each login session. `token_hash` keeps a SHA-256 hash. `revoked_at` is set on logout. `replaced_by_id` links a token to the next token, to find a token that is used two times. |
| `one_time_tokens` | `OneTimeToken`, `auth_token.py` | Tokens for email verification, phone verification, and password reset (`purpose`). `used_at` is set when the token is used. |

#### Authorization

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `roles` | `Role`, `role.py` | `is_system = true` for the four roles from the seed. Do not delete these roles. |
| `user_role` | `user_role_association`, `user_role.py` | Links users to roles. |
| `modules` | `Module`, `modules.py` | A feature area, for example `farms` or `knowledge`. |
| `role_modules` | `role_modules_association`, `role_modules.py` | The modules that a role can open. Use this to show or hide parts of the interface. |
| `privileges` | `Privilege`, `privilege.py` | One action in a module. `code` has the form `<module>.<action>`, for example `farms.update`. The API checks this code. |
| `role_privileges` | `role_privileges_association`, `role_privileges.py` | The privileges that a role has. |

#### Data protection

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `consent_records` | `ConsentRecord`, `consent.py` | One row for each grant or withdrawal (`granted`). Do not update rows. The newest row for a `consent_type` is the current consent. `recorded_by_id` is the agent, if an agent helped. |
| `agent_farmer_assignments` | `AgentFarmerAssignment`, `agent_assignment.py` | Gives an extension agent access to a farmer. Set `ended_at` to stop the access. |
| `audit_logs` | `AuditLog`, `audit_log.py` | The audit trail. See [Audit trail](#audit-trail). |

#### Farm profile

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `regions` | `Region`, `region.py` | Agroecological zones. `is_supported` shows where the system gives advice. |
| `crops` | `Crop`, `crop.py` | `is_supported` shows the crops that the system gives advice for. The first prototype supports maize. |
| `farms` | `Farm`, `farm.py` | `latitude` and `longitude` are approximate, and you keep them only with location consent. `water_access`, `cultivated_area_ha`, `budget_min`, and `budget_max` can be empty. An empty value means "unknown". Do not fill it with a guess. |
| `farm_resources` | `FarmResource`, `farm.py` | One input, equipment, water source, or labour item (`resource_type`). `is_available = false` records that the farmer does not have it. |
| `soil_records` | `SoilRecord`, `farm.py` | One soil value. `provenance` is `lab_test`, `farmer_estimate`, or `regional_source`. Use `value` for a number and `value_text` for text. |
| `crop_cycles` | `CropCycle`, `crop_cycle.py` | One season of one crop on one farm. `crop_stage` is text, for example `vegetative`. `status` is `active`, `completed`, or `abandoned`. |

#### Knowledge

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `knowledge_documents` | `KnowledgeDocument`, `knowledge.py` | Crop guidance. An empty `crop_id` or `region_id` means that the document applies to all crops or all regions. Use only documents with `review_status = approved` for retrieval. `superseded_by_id` links an old document to its replacement, and the old document gets `review_status = archived`. |
| `document_chunks` | `DocumentChunk`, `knowledge.py` | One passage of a document. Advice cites the `id`. `embedding` is a JSON list of numbers, and `embedding_model` is the model that made it. `content_hash` helps to find duplicate passages. |

#### Weather and cost

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `weather_forecasts` | `WeatherForecast`, `weather.py` | One fetch from a weather provider. Do not update rows. `issued_at` is the provider time and `retrieved_at` is the time of the fetch. A failed fetch has `status = failed`, so the app does not show an old forecast as current. |
| `freshness_policies` | `FreshnessPolicy`, `weather.py` | One row for each `action_type`. `max_forecast_age_hours` sets when a forecast is stale. `max_location_distance_km` sets when the app warns that the forecast point is far from the farm. |
| `price_records` | `PriceRecord`, `price.py` | A dated price (`priced_on`) for one unit of an input. `source` shows where the price came from. A quotation from one farmer has a `farm_id`. |

#### Advisory

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `advisory_requests` | `AdvisoryRequest`, `advisory.py` | The farmer's question and its `action_type`. `access_mode` is `independent` or `assisted`, and `assisted_by_id` is the agent. If the status is `clarification_needed`, `missing_fields` lists the data to ask for. |
| `advisory_responses` | `AdvisoryResponse`, `advisory.py` | The decision from the agronomic rules and the resource checks: `action`, `reason`, `suggested_timing`, and `resource_requirements`. `affordability` is `undetermined` when there are no prices. `weather_is_stale` and `forecast_distance_km` show forecast problems. |
| `advisory_explanations` | `AdvisoryExplanation`, `advisory.py` | The text from the language model for one decision. A new explanation gets a new row and does not change the decision. The current text has `is_current = true`. `validation_status` is the result of the output checks. |
| `advisory_citations` | `AdvisoryCitation`, `advisory.py` | The passages that an explanation cites. `similarity_score` is a retrieval score, not a probability that the advice is correct. |

#### Feedback and alerts

| Table | Model and file | Important columns and rules |
| --- | --- | --- |
| `advisory_feedback` | `AdvisoryFeedback`, `feedback.py` | What the farmer did with the advice: `followed`, `modified`, `rejected`, or `not_yet`. `reason` gives the cause of a change or a rejection. |
| `field_observations` | `FieldObservation`, `feedback.py` | A later observation in a crop cycle. `is_verified = false` for a reported value. Only a specialist sets it to `true`. |
| `alerts` | `Alert`, `alert.py` | A weather action alert. Send it only if the user has consent for `alerts`. `dedupe_key` is unique, so the same alert is not sent two times. Do not send the alert after `expires_at`. |

#### Offline sync

`farms`, `advisory_feedback`, and `field_observations` have a unique `client_reference` column. The offline client puts a UUID in this column. If the client sends the same record again, the database refuses the duplicate.

## Audit trail

The app writes a row to `audit_logs` for each insert, update, and delete that goes through a SQLAlchemy session. The row is in the same transaction as the change, so a rollback also removes the row.

Each row keeps:

- The action: `insert`, `update`, `delete`, or an event name.
- The table name and the record ID.
- The old and new value of each changed column, and the IDs added to or removed from many-to-many links such as `User.roles`.
- The user, the IP address, the user agent, and a request ID. The response header `X-Request-ID` gives the same request ID.

Rules:

- The trail writes `***` for `hashed_password` and `token_hash`. It does not keep the values.
- The trail does not record `audit_logs`, `refresh_tokens`, `one_time_tokens`, `document_chunks`, or `weather_forecasts`. Change `EXCLUDED_TABLES` in `app/audit.py` to change this list.
- The login dependency calls `set_audit_user`, so each change records the logged-in user.
- Call `record_event(db, "auth.login", entity=user)` for an event that does not change a row, for example a login, a failed login, or a data export.
- Bulk statements such as `db.query(Farm).update(...)` and raw SQL do not go through the trail. Do not use them for audited tables.

## Database migrations

The app runs `alembic upgrade head` when it starts. If the `alembic/versions/` folder is empty, the app first creates an initial migration from the models.

You can also run Alembic by hand, with the virtual environment active:

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after you change a model
alembic revision --autogenerate -m "describe the change"

# Undo the last migration
alembic downgrade -1
```

New models must be imported in `app/model/__init__.py`. If they are not, Alembic does not detect them.

Read each generated migration before you apply it. Alembic writes a rename as a drop and an add, and this deletes the data in the column.

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `No DATABASE_URL in env` | Make sure that `.env` is in the project root and has `DATABASE_URL`. |
| `Can't connect to MySQL server` | Start the MySQL server. Check the host, the port, and the login in `DATABASE_URL`. |
| `Unknown database 'smartfarm'` | Create the database. See [Create the database](#create-the-database). |
| `running scripts is disabled on this system` (Windows) | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` in PowerShell. |
| `JWT_SECRET is not set` in the terminal | Set `JWT_SECRET` in `.env`. Without it, all users are logged out when the server restarts. |
| `401 Log in first` | Log in and send the access token. In Swagger UI, click **Authorize**. |
| `401 The access token has expired` | Send the refresh token to `POST /api/v1/auth/refresh`, or log in again. |
| `403 You need the privilege ...` | Your role does not have that privilege. Log in as a user with a different role, or ask an admin. |
| `409 The roles are not set up yet` | Restart the server, or send `POST /seed-data`. |
| `429 Too many failed logins` | Wait 15 minutes, or reset the password. |
| `cryptography package is required` | Run `pip install -r requirements.txt` again. |
