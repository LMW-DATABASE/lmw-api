#!/bin/sh

echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

echo "Verificando criação de superusuário..."
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser \
        --no-input \
        || echo "Aviso: Superusuário já existe ou os dados são inválidos."
fi

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

exec "$@"