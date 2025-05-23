"""
Formatador de e-mails para notificações de auditoria.
"""

import logging
import os
from datetime import datetime

from utils.logger import setup_logger

# Configuração de logging
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

class EmailFormatter:
    """
    Classe responsável pela formatação de e-mails.
    """
    
    def format_audit_notification(self, audit_data):
        """
        Formata uma notificação de auditoria para envio por e-mail.
        
        Args:
            audit_data (dict): Dados da auditoria
            
        Returns:
            dict: Mensagem formatada para e-mail
        """
        logger.info(f"Formatando e-mail de notificação para auditoria {audit_data.get('audit_id')}")
        
        try:
            # Extração de dados
            audit_id = audit_data.get('audit_id')
            requester_email = audit_data.get('requester_email')
            summary = audit_data.get('summary', {})
            timestamp = audit_data.get('timestamp')
            
            # Conversão do timestamp para formato legível
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
                except (ValueError, TypeError):
                    formatted_date = timestamp
            else:
                formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Formatação do resumo
            summary_text = ""
            if summary:
                for data_type, count in summary.items():
                    if count > 0:
                        data_type_name = self._get_data_type_name(data_type)
                        summary_text += f"- {count} {data_type_name} não mascarados\n"
            
            if not summary_text:
                summary_text = "- Nenhum dado sensível encontrado\n"
            
            # Formatação do e-mail
            subject = f"Resultado da Auditoria de Dados Sensíveis - {audit_id[:8]}"
            
            body = f"""Olá,

A auditoria realizada em {formatted_date} identificou:

{summary_text}
Recomendamos o tratamento desses dados antes do uso em ambientes não produtivos.

Para acessar os detalhes completos da auditoria, incluindo a localização exata dos dados sensíveis, 
acesse o portal Data Sentinel e autentique-se com suas credenciais.

ID da Auditoria: {audit_id}

Atenciosamente,
Equipe Data Sentinel
"""
            
            logger.info(f"E-mail formatado com sucesso")
            
            return {
                'subject': subject,
                'body': body,
                'recipient': requester_email
            }
            
        except Exception as e:
            logger.error(f"Erro ao formatar e-mail de notificação: {str(e)}", exc_info=True)
            raise
    
    def _get_data_type_name(self, data_type):
        """
        Obtém o nome amigável para um tipo de dado sensível.
        
        Args:
            data_type (str): Tipo de dado sensível
            
        Returns:
            str: Nome amigável
        """
        data_type_names = {
            'cpf': 'CPFs',
            'email': 'E-mails',
            'cartao_credito': 'Cartões de crédito',
            'telefone': 'Telefones',
            'rg': 'RGs',
            'endereco': 'Endereços',
            'nome_completo': 'Nomes completos'
        }
        
        return data_type_names.get(data_type, data_type)
