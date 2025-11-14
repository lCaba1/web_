DROP TABLE IF EXISTS visit_logs;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    description TEXT
);

CREATE TABLE users (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(25) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    last_name VARCHAR(25) NOT NULL,
    first_name VARCHAR(25) NOT NULL,
    middle_name VARCHAR(25),
    role_id SMALLINT REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE visit_logs(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO roles (id, name) VALUES (1, 'admin');
INSERT INTO roles (id, name) VALUES (2, 'user');

INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
VALUES ('admin', SHA2('admin', 256), 'Админов', 'Админ', 'Админович', 1);

INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
VALUES ('user', SHA2('user', 256), 'Кабашов', 'Александр', 'Михайлович', 2);
