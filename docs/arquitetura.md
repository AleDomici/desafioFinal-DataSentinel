# Arquitetura do Data Sentinel

## Visão Geral

O Data Sentinel é uma solução de auditoria automatizada para identificação de dados sensíveis não mascarados em arquivos CSV. A arquitetura utiliza serviços AWS e integração com StackSpot IA para fornecer uma solução completa de compliance e segurança de dados.

## Componentes AWS

### 1. AWS Lambda Functions

#### Lambda Function 1: Processador de Auditoria
- **Nome**: `data_sentinel_processor`
- **Runtime**: Python 3.9
- **Função**: Recebe o arquivo CSV, identifica dados sensíveis usando StackSpot IA (Quick Commands), armazena o arquivo original no S3 e os resultados da análise no DynamoDB.
- **Triggers**: Upload de arquivo via API Gateway ou interface web
- **Permissões**: Acesso ao S3, DynamoDB e SNS

#### Lambda Function 2: Notificador
- **Nome**: `data_sentinel_notifier`
- **Runtime**: Python 3.9
- **Função**: Envia notificações por e-mail para o solicitante da auditoria com os resultados resumidos
- **Triggers**: Evento do DynamoDB ou mensagem SNS da primeira Lambda
- **Permissões**: Acesso ao SNS e DynamoDB (leitura)

### 2. Amazon S3

- **Bucket**: `data-sentinel-storage`
- **Função**: Armazenar os arquivos CSV originais enviados para auditoria
- **Configuração**: 
  - Criptografia em repouso (SSE-S3)
  - Políticas de ciclo de vida para gerenciar retenção de dados
  - Controle de acesso restrito

### 3. Amazon DynamoDB

- **Tabela**: `data-sentinel-audit-results`
- **Chave Primária**: `audit_id` (UUID gerado para cada auditoria)
- **Chave de Ordenação**: `timestamp`
- **Atributos**:
  - `requester_email`: E-mail do solicitante
  - `file_name`: Nome do arquivo original
  - `s3_path`: Caminho do arquivo no S3
  - `sensitive_data_count`: Contagem de dados sensíveis por tipo
  - `sensitive_data_details`: Detalhes dos dados sensíveis encontrados (mascarados)
  - `status`: Status da auditoria
  - `created_at`: Data/hora da criação
  - `updated_at`: Data/hora da última atualização

### 4. Amazon SNS

- **Tópico**: `data-sentinel-notifications`
- **Função**: Enviar notificações por e-mail para os solicitantes
- **Subscribers**: Endereços de e-mail dos solicitantes (adicionados dinamicamente)

### 5. API Gateway (opcional para expansão)

- **API**: `data-sentinel-api`
- **Endpoints**:
  - `POST /audit`: Enviar arquivo para auditoria
  - `GET /audit/{audit_id}`: Obter resultados da auditoria (requer autenticação)
- **Segurança**: Autenticação JWT para acesso aos detalhes da auditoria

## Integração com StackSpot IA

A integração com StackSpot IA é realizada através do recurso Quick Commands, que permite identificar padrões de dados sensíveis como:

- CPFs
- E-mails
- Cartões de crédito
- Telefones
- Outros dados pessoais

O processo utiliza a biblioteca StackSpot para Python, que é invocada pela função Lambda de processamento.

## Fluxo de Dados

1. O solicitante envia um arquivo CSV para auditoria
2. A função Lambda `data_sentinel_processor` é acionada
3. O arquivo é armazenado no bucket S3
4. A função Lambda utiliza StackSpot IA para identificar dados sensíveis
5. Os resultados são armazenados no DynamoDB
6. Um evento é enviado para o SNS
7. A função Lambda `data_sentinel_notifier` é acionada
8. Uma notificação por e-mail é enviada ao solicitante
9. O solicitante pode acessar os detalhes completos mediante autenticação

## Segurança e Compliance

- Todos os dados em trânsito são criptografados usando TLS
- Dados em repouso são criptografados no S3 e DynamoDB
- Acesso aos detalhes da auditoria requer autenticação JWT
- Os dados sensíveis são mascarados nos resultados detalhados
- Logs de auditoria são mantidos para rastreabilidade
- Conformidade com LGPD e GDPR

## Escalabilidade

- As funções Lambda escalam automaticamente conforme a demanda
- O DynamoDB pode ser configurado com capacidade sob demanda
- O S3 oferece escalabilidade praticamente ilimitada
- O SNS suporta milhões de assinaturas e mensagens

## Diagrama de Arquitetura

```
+----------------+     +-------------------+     +----------------+
| Solicitante    |---->| Lambda Function 1 |---->| S3 Bucket      |
| da Auditoria   |     | (Processor)       |     | (CSV Storage)  |
+----------------+     +-------------------+     +----------------+
                              |
                              | Usa StackSpot IA
                              | Quick Commands
                              v
                       +----------------+
                       | DynamoDB       |
                       | (Audit Results)|
                       +----------------+
                              |
                              | Trigger
                              v
                     +-------------------+     +----------------+
                     | Lambda Function 2 |---->| SNS            |
                     | (Notifier)        |     | (Email)        |
                     +-------------------+     +----------------+
                                                      |
                                                      v
                                               +----------------+
                                               | Solicitante    |
                                               | da Auditoria   |
                                               +----------------+
```

Este diagrama representa o fluxo básico da arquitetura, conforme mostrado na imagem de referência do projeto.
