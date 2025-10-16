## Запуск:
`docker-compose up --build`

## После загрузки сервиса бекенда и pg-admin (если сайт не грузится, еще не сбилдилось): 
pgAdmin: Open `http://localhost:7070` and log in with
login: `admin@admin.com`
password: `admin` 

Add New Server > Connection:

Host: `db`
Port: `5432`
Username: `postgres`
Password: `postgres`
Database: `postgres`

## После этого:
`http://localhost:3000`
