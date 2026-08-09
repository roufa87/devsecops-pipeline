FROM python:3.12-slim

# Créer un utilisateur non-root (bonne pratique de sécurité)
RUN useradd --create-home appuser

WORKDIR /app

# Installer les dépendances d'abord (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Donner la propriété des fichiers à l'utilisateur non-root
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]