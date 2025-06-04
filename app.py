import json
import os
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from lambda_functions.processor.dynamodb_handler import DynamoDBHandler
from lambda_functions.processor.dados_auditoria_handler import DadosAuditoriaHandler
from lambda_functions.processor.s3_handler import S3Handler
from lambda_functions.processor.utils.logger import setup_logger
import csv
import io

load_dotenv()
app = FastAPI()

# Configurações
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')
DYNAMODB_TABLE_RESULT = os.environ.get('DYNAMODB_TABLE_RESULT', 'dados-auditoria')
S3_BUCKET = os.environ.get('S3_BUCKET')
logger = setup_logger(__name__)

# Inicialização de Handlers
dynamodb_handler = DynamoDBHandler(DYNAMODB_TABLE)
dados_auditoria_handler = DadosAuditoriaHandler(DYNAMODB_TABLE_RESULT)
s3_handler = S3Handler(S3_BUCKET)

def formatar_data_brasil(data_iso):
    if '.' in data_iso:
        data_iso = data_iso.split('.')[0]
    dt = datetime.strptime(data_iso, "%Y-%m-%dT%H:%M:%S")
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def mascarar_csv_text(text, n=2):
    f = io.StringIO(text)
    reader = csv.DictReader(f, delimiter=';')
    campos_sensiveis = {'cpf', 'email', 'cartao', 'telefone'}
    mascarado = []
    for i, row in enumerate(reader):
        if i >= n:
            break
        for campo in campos_sensiveis:
            if campo in row:
                row[campo] = "*****"
        mascarado.append(row)
    return mascarado

def contar_dados_expostos_csv(text):
    f = io.StringIO(text)
    reader = csv.DictReader(f, delimiter=';')
    campos_sensiveis = {'cpf', 'email', 'cartao', 'telefone'}
    expostos = 0
    for row in reader:
        for campo in campos_sensiveis:
            valor = row.get(campo, "")
            if isinstance(valor, str) and not valor.startswith("*****"):
                expostos += 1
    return expostos

@app.post("/arquivos")
async def upload_arquivo(file: UploadFile = File(...), email: str = Form(...)):
    # Validar se o arquivo é um CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são permitidos.")
    # Validar o tamanho do arquivo (máximo 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="O arquivo deve ter no máximo 5MB")
    # Validar o formato do e-mail
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
    # Armazenar no DynamoDB com o e-mail e o CSV puro
    audit_data = {
        'audit_id': str(uuid.uuid4()),
        'created_at': datetime.utcnow().isoformat(),
        'timestamp': datetime.utcnow().isoformat(),
        'requester_email': email,
        'file_name': file.filename,
        's3_path': s3_key,
        'status': 'PENDING',
        'text': file_content.decode()  # Salva o CSV puro como string
    }
    try:
        dynamodb_handler.save_audit_result(audit_data)
    except Exception as e:
        logger.error(f"Erro ao salvar resultado da auditoria: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao salvar resultado da auditoria.")
    return {"filename": file.filename, "message": "Arquivo enviado com sucesso!", "email": email}

@app.get("/dados-sensiveis")
def get_dados_sensiveis(email: str = Query(..., description="E-mail do solicitante para filtrar auditorias")):
    try:
        audits = dados_auditoria_handler.list_audits_by_requester(email)
        audits = [a for a in audits if a.get("requester_email") == email]
        if not audits:
            return JSONResponse(content={"detail": "Nenhuma auditoria encontrada para este e-mail."}, status_code=404)
        audits_sorted = sorted(audits, key=lambda x: x.get('created_at', ''), reverse=True)
        audit = audits_sorted[0]
        text = audit.get("text", "")
        dados_expostos = contar_dados_expostos_csv(text)
        amostra = mascarar_csv_text(text)
        audit_data_iso = audit.get("created_at", None)
        if audit_data_iso:
            data_formatada = formatar_data_brasil(audit_data_iso)
        else:
            data_formatada = "Data não informada"
        response = {
            "Olá": audit.get("nome", "Solicitante"),
            "A auditoria realizada em": data_formatada,
            "identificou": f"- {dados_expostos} DADOS EXPOSTOS",
            "Recomendamos": "o tratamento desses dados.",
            "Atenciosamente": "Equipe Data Sentinel",
            "Amostra de Dados Mascarados": amostra
        }
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Erro ao buscar auditorias: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar auditorias.")

@app.delete("/dados-sensiveis")
def delete_dados_sensiveis(email: str = Query(..., description="E-mail do solicitante para deletar auditorias")):
    try:
        audits = dados_auditoria_handler.list_audits_by_requester(email)
        for audit in audits:
            dados_auditoria_handler.delete_audit(audit['HASH'], audit['RANGE'])
        return {"message": "Auditoria Limpa com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao limpar a tabela: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao limpar a tabela.")