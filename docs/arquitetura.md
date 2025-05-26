# Arquitetura do Data Sentinel

## Visão Geral

O Data Sentinel é uma solução de auditoria automatizada projetada para identificar dados sensíveis não mascarados em arquivos CSV. Utilizando uma arquitetura serverless na AWS e integrando-se com o StackSpot IA, o sistema oferece uma abordagem eficiente para garantir a conformidade e a segurança dos dados.

## Diagrama de Arquitetura

A imagem abaixo ilustra o fluxo principal e os componentes da arquitetura do Data Sentinel:

![Diagrama de Arquitetura do Data Sentinel](https://private-us-east-1.manuscdn.com/sessionFile/azQFudc161d48xTMgBJ8EZ/sandbox/eb1zZkVJIdXv8tUJOwnfpY-images_1748269109405_na1fn_L2hvbWUvdWJ1bnR1L2Rlc2FmaW9GaW5hbC1EYXRhU2VudGluZWwvZG9jcy9GTFVYT0dSQU1BREVTQUZJT0ZJTkFMU1FVQUQyLmRyYXdpbw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYXpRRnVkYzE2MWQ0OHhUTWdCSjhFWi9zYW5kYm94L2ViMXpaa1ZKSWRYdjh0VUpPd25mcFktaW1hZ2VzXzE3NDgyNjkxMDk0MDVfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyUmxjMkZtYVc5R2FXNWhiQzFFWVhSaFUyVnVkR2x1Wld3dlpHOWpjeTlHVEZWWVQwZFNRVTFCUkVWVFFVWkpUMFpKVGtGTVUxRlZRVVF5TG1SeVlYZHBidy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NjcyMjU2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=hND8~uSmHQofRMXallNKKpgWgMC63qjcTn8lhDZsZ9h4sSgpgKXDMfop70n1IWOQUd1a8p-7qFZzeP8cK2VlmwLaUDBRSP5A8K1VhJ1T2xUtMgAJHfxsQnqzQbmeWsPNqwF58lTT792x1gvrXnxmOEWDEjTgIZZiyg7rsNqmC6AUfU3iHKdw0gFfAfTgQIfctGe2-1s32Ilt2uUrTRs2mKEE7YY7nUc3O3cmnPq4jkpuQzMBJwTVwGPfwBEzBKly9~zMhqJHI-xVrPUtQUqqERFQscEGmY3MqqtJ7m93bEYFH4k~bKulkRU~mO51akWnIjWL0eOQFY5o-0IIzShgIQ__)

## Componentes Principais

### 1. Solicitante da Auditoria
O usuário inicia o processo enviando um arquivo CSV (contendo, por exemplo, id, nome, cpf) para análise.

### 2. AWS Lambda Function - Processador
- **Nome (sugerido):** `data_sentinel_processor`
- **Função:** Esta função Lambda, escrita em Python, atua como o ponto central de processamento. Ela recebe o arquivo CSV, utiliza um Quick Command remoto do StackSpot AI para identificar dados não mascarados, armazena o arquivo CSV original no Bucket S3 e salva os dados com conteúdo potencialmente sensível (resultados da análise) na tabela do DynamoDB.
- **Trigger:** Geralmente acionada por um upload de arquivo (via API Gateway, S3 Event, ou outra interface).

### 3. Amazon S3
- **Bucket (sugerido):** `data-sentinel-storage`
- **Função:** Armazena de forma segura os arquivos CSV originais enviados pelo solicitante.

### 4. Amazon DynamoDB
- **Tabela (sugerida):** `data-sentinel-audit-results`
- **Função:** Armazena os metadados e os resultados da análise de dados sensíveis realizada pela função Lambda Processador. Também é consultada pela função Notificadora para obter informações sobre a auditoria.

### 5. AWS Lambda Function - Notificador
- **Nome (sugerido):** `data_sentinel_notifier`
- **Função:** Responsável por notificar o solicitante sobre o resultado da auditoria. Recupera os dados da pessoa auditora (provavelmente o e-mail e o status da auditoria) do DynamoDB e envia uma notificação via Amazon SNS.
- **Trigger:** É disparada por um trigger originado na função Lambda Processador após a conclusão da análise e armazenamento dos dados.

### 6. Amazon SNS
- **Tópico (sugerido):** `data-sentinel-notifications`
- **Função:** Recebe a mensagem da função Lambda Notificadora e envia a notificação final (geralmente por e-mail) para o Solicitante da Auditoria.

## Fluxo de Dados Detalhado

1.  **Envio do Arquivo:** O Solicitante da Auditoria envia um arquivo CSV para o sistema.
2.  **Processamento Inicial:** A função Lambda Processadora é acionada.
3.  **Análise e Armazenamento:**
    *   A Lambda Processadora utiliza o StackSpot AI (via Quick Command) para analisar o conteúdo do CSV em busca de dados sensíveis.
    *   O arquivo CSV original é armazenado no Bucket S3.
    *   Os resultados da análise (dados potencialmente sensíveis) são armazenados na tabela do DynamoDB.
4.  **Disparo da Notificação:** Após o processamento, a Lambda Processadora dispara um trigger para a Lambda Notificadora.
5.  **Recuperação e Envio:**
    *   A Lambda Notificadora recupera os dados relevantes da auditoria (como o e-mail do solicitante e um resumo dos resultados) do DynamoDB.
    *   A Lambda Notificadora envia uma mensagem formatada para o tópico SNS.
6.  **Notificação Final:** O Amazon SNS entrega a notificação (por e-mail) ao Solicitante da Auditoria.

## Integração com StackSpot IA

A identificação de dados sensíveis é realizada pela função Lambda Processadora através da execução de um Quick Command remoto do StackSpot AI, especializado em detectar padrões como CPFs, e-mails, cartões de crédito, etc.

## Outras Considerações (Detalhes em outros documentos)

*   **Estrutura de Código:** Consulte `docs/estrutura_codigo.md` para detalhes sobre a organização dos arquivos das Lambdas e da aplicação FastAPI.
*   **Implantação:** O `docs/guia_implantacao.md` fornece instruções para configurar e implantar os recursos AWS.
*   **Segurança e Compliance:** Medidas como criptografia, permissões IAM e mascaramento de dados são essenciais e devem ser implementadas conforme as melhores práticas.
*   **Escalabilidade:** A arquitetura serverless com Lambda, S3, DynamoDB e SNS oferece alta escalabilidade.

# Arquitetura do Data Sentinel

## Visão Geral

O Data Sentinel é uma solução de auditoria automatizada projetada para identificar dados sensíveis não mascarados em arquivos CSV. Utilizando uma arquitetura serverless na AWS e integrando-se com o StackSpot IA, o sistema oferece uma abordagem eficiente para garantir a conformidade e a segurança dos dados.

## Diagrama de Arquitetura

A imagem abaixo ilustra o fluxo principal e os componentes da arquitetura do Data Sentinel:

![Diagrama de Arquitetura do Data Sentinel](https://private-us-east-1.manuscdn.com/sessionFile/azQFudc161d48xTMgBJ8EZ/sandbox/eb1zZkVJIdXv8tUJOwnfpY-images_1748269109405_na1fn_L2hvbWUvdWJ1bnR1L2Rlc2FmaW9GaW5hbC1EYXRhU2VudGluZWwvZG9jcy9GTFVYT0dSQU1BREVTQUZJT0ZJTkFMU1FVQUQyLmRyYXdpbw.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvYXpRRnVkYzE2MWQ0OHhUTWdCSjhFWi9zYW5kYm94L2ViMXpaa1ZKSWRYdjh0VUpPd25mcFktaW1hZ2VzXzE3NDgyNjkxMDk0MDVfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyUmxjMkZtYVc5R2FXNWhiQzFFWVhSaFUyVnVkR2x1Wld3dlpHOWpjeTlHVEZWWVQwZFNRVTFCUkVWVFFVWkpUMFpKVGtGTVUxRlZRVVF5TG1SeVlYZHBidy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NjcyMjU2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=hND8~uSmHQofRMXallNKKpgWgMC63qjcTn8lhDZsZ9h4sSgpgKXDMfop70n1IWOQUd1a8p-7qFZzeP8cK2VlmwLaUDBRSP5A8K1VhJ1T2xUtMgAJHfxsQnqzQbmeWsPNqwF58lTT792x1gvrXnxmOEWDEjTgIZZiyg7rsNqmC6AUfU3iHKdw0gFfAfTgQIfctGe2-1s32Ilt2uUrTRs2mKEE7YY7nUc3O3cmnPq4jkpuQzMBJwTVwGPfwBEzBKly9~zMhqJHI-xVrPUtQUqqERFQscEGmY3MqqtJ7m93bEYFH4k~bKulkRU~mO51akWnIjWL0eOQFY5o-0IIzShgIQ__)

## Componentes Principais

### 1. Solicitante da Auditoria
O usuário inicia o processo enviando um arquivo CSV (contendo, por exemplo, id, nome, cpf) para análise.

### 2. AWS Lambda Function - Processador
- **Nome (sugerido):** `data_sentinel_processor`
- **Função:** Esta função Lambda, escrita em Python, atua como o ponto central de processamento. Ela recebe o arquivo CSV, utiliza um Quick Command remoto do StackSpot AI para identificar dados não mascarados, armazena o arquivo CSV original no Bucket S3 e salva os dados com conteúdo potencialmente sensível (resultados da análise) na tabela do DynamoDB.
- **Trigger:** Geralmente acionada por um upload de arquivo (via API Gateway, S3 Event, ou outra interface).

### 3. Amazon S3
- **Bucket (sugerido):** `data-sentinel-storage`
- **Função:** Armazena de forma segura os arquivos CSV originais enviados pelo solicitante.

### 4. Amazon DynamoDB
- **Tabela (sugerida):** `data-sentinel-audit-results`
- **Função:** Armazena os metadados e os resultados da análise de dados sensíveis realizada pela função Lambda Processador. Também é consultada pela função Notificadora para obter informações sobre a auditoria.

### 5. AWS Lambda Function - Notificador
- **Nome (sugerido):** `data_sentinel_notifier`
- **Função:** Responsável por notificar o solicitante sobre o resultado da auditoria. Recupera os dados da pessoa auditora (provavelmente o e-mail e o status da auditoria) do DynamoDB e envia uma notificação via Amazon SNS.
- **Trigger:** É disparada por um trigger originado na função Lambda Processador após a conclusão da análise e armazenamento dos dados.

### 6. Amazon SNS
- **Tópico (sugerido):** `data-sentinel-notifications`
- **Função:** Recebe a mensagem da função Lambda Notificadora e envia a notificação final (geralmente por e-mail) para o Solicitante da Auditoria.

## Fluxo de Dados Detalhado

1.  **Envio do Arquivo:** O Solicitante da Auditoria envia um arquivo CSV para o sistema.
2.  **Processamento Inicial:** A função Lambda Processadora é acionada.
3.  **Análise e Armazenamento:**
    *   A Lambda Processadora utiliza o StackSpot AI (via Quick Command) para analisar o conteúdo do CSV em busca de dados sensíveis.
    *   O arquivo CSV original é armazenado no Bucket S3.
    *   Os resultados da análise (dados potencialmente sensíveis) são armazenados na tabela do DynamoDB.
4.  **Disparo da Notificação:** Após o processamento, a Lambda Processadora dispara um trigger para a Lambda Notificadora.
5.  **Recuperação e Envio:**
    *   A Lambda Notificadora recupera os dados relevantes da auditoria (como o e-mail do solicitante e um resumo dos resultados) do DynamoDB.
    *   A Lambda Notificadora envia uma mensagem formatada para o tópico SNS.
6.  **Notificação Final:** O Amazon SNS entrega a notificação (por e-mail) ao Solicitante da Auditoria.

## Integração com StackSpot IA

A identificação de dados sensíveis é realizada pela função Lambda Processadora através da execução de um Quick Command remoto do StackSpot AI, especializado em detectar padrões como CPFs, e-mails, cartões de crédito, etc.

## Outras Considerações (Detalhes em outros documentos)

*   **Estrutura de Código:** Consulte `docs/estrutura_codigo.md` para detalhes sobre a organização dos arquivos das Lambdas e da aplicação FastAPI.
*   **Implantação:** O `docs/guia_implantacao.md` fornece instruções para configurar e implantar os recursos AWS.
*   **Segurança e Compliance:** Medidas como criptografia, permissões IAM e mascaramento de dados são essenciais e devem ser implementadas conforme as melhores práticas.
*   **Escalabilidade:** A arquitetura serverless com Lambda, S3, DynamoDB e SNS oferece alta escalabilidade.

