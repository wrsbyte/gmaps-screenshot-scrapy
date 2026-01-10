### ✨ Manual to configure the database

This project uses a PostgreSQL database to store the target locations. Postgres run in a docker container.

To configure the database, you need to set the following environment variables:

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

To access the database, you can use the following command:

```bash
docker exec -it postgres_container_name psql -U postgres -d postgres_db_name
```

Or use pgAdmin to access the database.

In pgAdmin, you can connect to the database using the following credentials:

- Hostname: postgres
- Port: 5432
- Username: postgres
- Password: your_postgres_password

## ✨ Create tables

Run the following SQL query to create the tables:

```sql
CREATE TABLE target_locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(255) NOT NULL,
    link VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    gmaps_zoom INT NOT NULL,
    gmaps_extra_params JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## ✨ Insert data

Run the following SQL query to insert data:

```sql
INSERT INTO target_locations (name, description, address, link, latitude, longitude, gmaps_zoom, gmaps_extra_params, active)
VALUES ('Target Location 1', 'Description 1', 'Address 1', 'Link 1', 1.1, 1.1, 1, '{"param1": "value1"}', TRUE);
```

🪂Enjoy!
