# Flask Demo Project

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
