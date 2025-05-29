FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Instale Python manualmente
RUN powershell -Command `
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe -OutFile python-installer.exe ; `
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item python-installer.exe

# Atualize o PATH para garantir que python e pip estejam disponíveis
ENV PATH="C:\\Program Files\\Python311;C:\\Program Files\\Python311\\Scripts;${PATH}"

WORKDIR /app

# Copie requirements.txt para a raiz do projeto
COPY requirements.txt .

# Instale dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código
COPY . .

EXPOSE 8000

# Use uvicorn se for FastAPI, ou python app.py se for Flask/Django/etc
CMD ["python", "app.py"]
# ou, para FastAPI:
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]