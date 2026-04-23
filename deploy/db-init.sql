CREATE DATABASE {database};

\connect {database};

CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

CREATE USER {username} WITH ENCRYPTED PASSWORD '{password}';
GRANT ALL PRIVILEGES ON DATABASE {database} TO {username};
