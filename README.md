# Flask Demo Project

Flask demo app for working out issues in isolation.

This demo relates to setting up tests to automatically rollback database changes.

The current problem of this demo is that database changes are not rolled back between each test.

The tests assume a `flaskdemo-test` PostgreSQL database.

Username, password, host and port is setup in `.env` file.

## Configuration

Populate `.env`, refer to `.env.example`.

## Database Migrations

https://alembic.sqlalchemy.org/en/latest/autogenerate.html

1. Modify `models.py`.

2. Generate migration:

    ```sh
    flask db revision "Initial migration"
    flask db revision "Added account table"
    ```

3. Check in the generated migration file and update as needed.

4. Run the migration:

    ```sh
    flask db upgrade
    ```

## App

```sh
flask --app app run --debug --port 5333
```

## Tests

```sh
pytest
```
