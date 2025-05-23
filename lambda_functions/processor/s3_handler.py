"""
Manipulação de arquivos no Amazon S3 para o Data Sentinel.
"""

import boto3
import logging
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv() 

from lambda_functions.notifier.utils.logger import setup_logger

# Configuração de logging
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

class S3Handler:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')  
        )

    def upload_file(self, file_path, s3_key):
        """
        Faz upload de um arquivo para o S3.
        
        Args:
            file_path (str): Caminho do arquivo local
            s3_key (str): Chave do objeto no S3
            
        Returns:
            str: URL do arquivo no S3
        """
        logger.info(f"Iniciando upload do arquivo {file_path} para S3 com chave {s3_key}")
        
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            
            # Gera URL do arquivo
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            logger.info(f"Upload concluído com sucesso. URL: {url}")
            
            return url
            
        except ClientError as e:
            logger.error(f"Erro ao fazer upload do arquivo para S3: {str(e)}", exc_info=True)
            raise
        
    def download_file(self, s3_key, local_path):
        """
        Faz download de um arquivo do S3.
        
        Args:
            s3_key (str): Chave do objeto no S3
            local_path (str): Caminho local para salvar o arquivo
            
        Returns:
            str: Caminho local do arquivo baixado
        """
        logger.info(f"Iniciando download do arquivo S3 {s3_key} para {local_path}")
        
        try:
            # Garante que o diretório de destino existe
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Download concluído com sucesso: {local_path}")
            
            return local_path
            
        except ClientError as e:
            logger.error(f"Erro ao fazer download do arquivo do S3: {str(e)}", exc_info=True)
            raise
            
    def delete_file(self, s3_key):
        """
        Remove um arquivo do S3.
        
        Args:
            s3_key (str): Chave do objeto no S3
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        logger.info(f"Removendo arquivo {s3_key} do S3")
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Arquivo removido com sucesso")
            
            return True
            
        except ClientError as e:
            logger.error(f"Erro ao remover arquivo do S3: {str(e)}", exc_info=True)
            raise
            
    def list_files(self, prefix=""):
        """
        Lista arquivos no bucket S3.
        
        Args:
            prefix (str): Prefixo para filtrar os arquivos
            
        Returns:
            list: Lista de objetos no bucket
        """
        logger.info(f"Listando arquivos no bucket {self.bucket_name} com prefixo {prefix}")
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                
            logger.info(f"Encontrados {len(files)} arquivos")
            return files
            
        except ClientError as e:
            logger.error(f"Erro ao listar arquivos no S3: {str(e)}", exc_info=True)
            raise
