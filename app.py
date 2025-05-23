from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
import tempfile
from lambda_functions.processor.dynamodb_handler import DynamoDBHandler  
from lambda_functions.processor.s3_handler import S3Handler
from lambda_functions.processor.utils.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configurações
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')
S3_BUCKET = os.environ.get('S3_BUCKET')
logger = setup_logger(__name__)

# Inicialização de Handlers
dynamodb_handler = DynamoDBHandler(DYNAMODB_TABLE) 
s3_handler = S3Handler(S3_BUCKET)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), email: str = Form(...)):
    # Validar se o arquivo é um CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos.")

    # Validar o tamanho do arquivo (máximo 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="O arquivo deve ter no máximo 5MB")

    # Validar o formato do e-mail (usando email-validator)
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Usar diretório temporário multiplataforma
    tmp_dir = tempfile.gettempdir()
    file_location = os.path.join(tmp_dir, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(file_content)

    s3_key = f"uploads/{file.filename}"
    try:
        s3_handler.upload_file(file_location, s3_key)
    except Exception as e:
        logger.error(f"Erro ao fazer upload do arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao fazer upload do arquivo.")

    # Armazenar no DynamoDB com o e-mail
    audit_data = {
        'audit_id': str(uuid.uuid4()),  # Geração de ID único
        'requester_email': email,
        'file_name': file.filename,
        's3_path': s3_key,
        'status': 'PENDING',  # Status inicial
        'created_at': datetime.utcnow().isoformat(),  # Timestamp atual
    }
    try:
        dynamodb_handler.save_audit_result(audit_data)  
    except Exception as e:
        logger.error(f"Erro ao salvar resultado da auditoria: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao salvar resultado da auditoria.")

    return {"filename": file.filename, "message": "Arquivo enviado com sucesso!", "email": email}

@app.get("/sensitive-data/")
def get_sensitive_data(email: str = Query(..., description="E-mail do solicitante para filtrar auditorias")):
    try:
        audits = dynamodb_handler.list_audits_by_requester(email)  
        return JSONResponse(content=audits)
    except Exception as e:
        logger.error(f"Erro ao buscar auditorias: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar auditorias.")

@app.delete("/clear-dynamodb/")
def clear_dynamodb():
    try:
        audits = dynamodb_handler.list_audits_by_requester("example@domain.com")  
        for audit in audits:
            dynamodb_handler.delete_audit(audit['audit_id'])
        return {"message": "Tabela DynamoDB limpa com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao limpar a tabela: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao limpar a tabela.")