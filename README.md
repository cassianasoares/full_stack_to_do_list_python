# Todo List API – Django + Docker

Este projeto é uma API em Django para gerenciamento de tarefas, containerizada com Docker e configurada para boas práticas de segurança e produção.

## 🚀 Tecnologias

- **Python 3.12 (slim)** – imagem leve e estável
    
- **Django** – framework web

- **SQLite** – banco de dados simples e persistente via volume
    
- **Docker Secrets** – gerenciamento seguro de segredos
    

## 🔒 Segurança

### Uso de Docker Secrets

- O `SECRET_KEY` do Django **não deve ser exposto em variáveis de ambiente**.
    
- Uso de **Docker Secrets**, para montar o segredo como um arquivo protegido dentro do container (`/run/secrets/django_secret_key`). Para o segredo não apareça em logs ou comandos como `docker inspect`.


### Não usar usuário root

- Usuário dedicado para rodar o Django, para garantir que mesmo que alguém explore o container, não terá privilégios de root.
    

## ⚙️ Como rodar

1. Crie o arquivo de segredo:
    
    bash
    
    ```
    echo "sua_chave_secreta_aqui" > django_secret_key.txt
    ```
    
2. Suba os containers:
    
    bash
    
    ```
    docker-compose up --build -d
    ```
    
3. Acesse a aplicação em:
    
    Código
    
    ```
    http://localhost:8000
    ```
    

## 📂 Volumes

- `sqlite_data` → persistência do banco `db.sqlite3`