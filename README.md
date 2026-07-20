# Todo List API – Django + Docker

Este projeto é uma API em Django para gerenciamento de tarefas, containerizada com Docker e configurada para execução local e em ambientes de desenvolvimento.

## 🚀 Tecnologias

- **Python 3.12** – runtime da aplicação
- **Django** – framework web
- **Django REST Framework** – APIs REST
- **SQLite** – banco de dados simples e persistente via volume
- **Docker Compose** – execução do ambiente

## 🔒 Segurança

- **Variáveis de Ambiente**: Configurações sensíveis são definidos via arquivo `.env`, nunca hardcoded no código. O `SECRET_KEY` encontra-se no mesmo para simplificar uso e desenvolvimento do projeto.
- **Autenticação JWT**: Tokens JWT com expiração configurável (access: 5 min, refresh: 1 dia).
- **Validação de Senhas**: Senhas são validadas com regras de força (mínimo 8 caracteres, diversidade de caracteres).
- **Usuário Não-Root**: O container roda com um usuário dedicado sem privilégios administrativos.
- **Bandit Security Scan**: O projeto executa verificações de segurança estática via Bandit na CI/CD.

## ⚙️ Como rodar

1. Copie o arquivo de exemplo de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Ajuste as variáveis no arquivo `.env` conforme necessário.

3. Suba os containers:

   ```bash
   docker-compose up --build -d
   ```

4. Acesse a aplicação em:

   ```text
   http://localhost:8000
   ```

## 📂 Volumes

- `sqlite_data` → persistência do banco `db.sqlite3`
