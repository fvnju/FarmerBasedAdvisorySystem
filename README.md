# Farmer Based Advisory System

A FastAPI backend with a MySQL database. SQLAlchemy defines the models. Alembic manages the database schema.

## Current state

- A FastAPI app in `app/main.py`.
- Two routes: `GET /` (health check) and `POST /seed-data` (adds the roles, modules, privileges, and one test user).
- Models in `app/model/`. See [Database models](#database-models).
- Three Alembic migrations in `alembic/versions/`.
- An audit trail in `app/audit.py`. See [Audit trail](#audit-trail).
- The app applies all migrations when it starts.

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

The seed creates four roles: `admin`, `farmer`, `extension_agent`, and `agronomist`. The privileges for each role are in `app/seed.py`.

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
- Call `set_audit_user(user.id)` after you authenticate the user. If you do not, `user_id` is empty.
- Call `record_event(db, "auth.login", entity=user)` for an event that does not change a row, for example a login, a failed login, or a data export.
- Bulk statements such as `db.query(Farm).update(...)` and raw SQL do not go through the trail. Do not use them for audited tables.

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

   You can run this command again. It does not add duplicate rows.

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

New models must be imported in `app/model/__init__.py`. If they are not, Alembic does not detect them.

Read each generated migration before you apply it. Alembic writes a rename as a drop and an add, and this deletes the data in the column.

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
│   ├── seed.py           # Roles, modules, privileges, and test data
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
