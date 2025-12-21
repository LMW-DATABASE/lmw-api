# LMW Database API

API de back-end para o projeto LMW, desenvolvida em Django. Esta API é responsável pelo gerenciamento de usuários, moléculas e outras entidades da base de dados. O projeto é totalmente containerizado com Docker para facilitar o desenvolvimento e a implantação.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Django, Django REST Framework
* **Banco de Dados:** PostgreSQL
* **Autenticação:** Token Authentication (padrão do DRF)
* **Documentação da API:** drf-spectacular (Swagger UI / ReDoc)
* **Ambiente:** Docker, Docker Compose

---

## 🚀 Como Configurar e Rodar o Ambiente

Siga estes passos para ter o ambiente de desenvolvimento completo rodando na sua máquina.

### Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/) (Docker Desktop para Mac/Windows já inclui o Docker Compose)

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_GITLAB>
    cd ednu-lmw-api
    ```

2.  **Crie o arquivo de ambiente (`.env`):**
    Este arquivo guarda as senhas e configurações locais. Ele não é enviado para o GitLab.
    
    Crie um arquivo chamado `.env` na raiz do projeto e cole o seguinte conteúdo nele:
    ```env
    # .env

    # Chave secreta do Django (pode ser qualquer string longa e aleatória)
    DJANGO_SECRET_KEY='django-insecure-sua-chave-aleatoria-aqui'

    # Configuração do modo DEBUG
    DJANGO_DEBUG=True

    # Credenciais do Banco de Dados PostgreSQL (o Docker Compose usará isso para criar o banco)
    POSTGRES_DB=lmw_db
    POSTGRES_USER=lmw_user
    POSTGRES_PASSWORD=lmw_password

    # (OPCIONAL) Defina uma porta diferente se a 8000 estiver em uso na sua máquina
    # DJANGO_PORT=8001
    ```

3.  **Construa e Inicie os Contêineres:**
    Este comando vai construir a imagem do Django e iniciar os contêineres do backend e do banco de dados.
    ```bash
    docker compose up --build
    ```
    * Na primeira vez, isso pode demorar um pouco, pois o Docker precisa baixar as imagens base.
    * O `--build` força a reconstrução da imagem, útil quando você altera o `Dockerfile` ou o `requirements.txt`.

A aplicação estará rodando! O servidor da API estará acessível no endereço `http://localhost:8000` (ou na porta que você definiu em `DJANGO_PORT`).

---

## ▶️ Comandos do Dia a Dia

* **Para iniciar o ambiente:**
    ```bash
    docker compose up
    ```

* **Para parar o ambiente:**
    Pressione `Ctrl + C` no terminal onde os contêineres estão rodando. Depois, para garantir que tudo foi removido, rode:
    ```bash
    docker compose down
    ```

---

## 👨‍💻 Como Executar Comandos do Django (`manage.py`)

Com o Docker, você não roda mais `python manage.py` diretamente. Você pede ao Docker para executar o comando *dentro* do contêiner do backend.

**Com os contêineres em execução**, abra um **novo terminal** e use o prefixo `docker compose exec backend`:

* **Criar novas migrações:**
    ```bash
    docker compose exec backend python manage.py makemigrations
    ```

* **Criar um superusuário:**
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```
    
* **Abrir o shell do Django:**
    ```bash
    docker compose exec backend python manage.py shell
    ```

---

## 🌿 Fluxo de Trabalho com Git

Nosso projeto usa um fluxo baseado no Git Flow, com duas branches principais:
* `main`: Contém o código estável (versão de "produção"). Ninguém envia código diretamente para cá.
* `develop`: Branch principal de desenvolvimento, onde as novas funcionalidades são integradas. É a nossa base de trabalho.

**Para criar uma nova funcionalidade:**

1.  Certifique-se de que sua branch `develop` local está atualizada:
    ```bash
    git checkout develop
    git pull origin develop
    ```

2.  Crie uma nova branch a partir da `develop`:
    ```bash
    git checkout -b feature/nome-da-sua-tarefa
    ```
    *(Ex: `feature/criar-endpoint-moleculas`)*

3.  Trabalhe e faça seus commits na sua `feature` branch.

4.  Quando terminar, envie sua branch para o GitLab e abra um **Merge Request** para a `develop`.
    ```bash
    git push origin feature/nome-da-sua-tarefa
    ```

---

## 📚 Documentação da API

Com o ambiente rodando, você pode acessar a documentação interativa da API, gerada automaticamente, nos seguintes endereços:

* **Swagger UI:** `http://localhost:8000/api/swagger-ui/`
* **ReDoc:** `http://localhost:8000/api/redoc/`

*(Lembre-se de trocar `8000` pela porta que você configurou no seu `.env`, se for o caso.)*



------------------------------
## Como criar um usuario inicial

## entrar no conteiner do docker
docker exec -it lmw_django_api python manage.py shell


from django.contrib.auth import get_user_model
User = get_user_model()

# Pega o usuário pelo email
u = User.objects.get(email="admin@admin.com")

# Define a nova senha
u.set_password("123456")

# Dá permissão de Super Usuário e Staff
u.is_superuser = True
u.is_staff = True

# Salva no banco
u.save()

print(f"Pronto! O usuário {u.email} agora é admin e a senha é 123456")