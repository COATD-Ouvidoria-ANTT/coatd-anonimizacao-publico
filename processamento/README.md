# Pasta Processamento - Documentação Técnica

## Visão Geral

A pasta `processamento` é o núcleo operacional do projeto de anonimização de dados. Ela contém toda a lógica necessária para transformar dados brutos coletados da plataforma de ouvidoria em dados prontos para a etapa de rotulação de texto. Essa rotulação servirá para o fine-tuning (treinamento especializado) do nosso modelo NER (Inteligência Artificial que reconhece nomes, empresas e endereços).

O fluxo desta pasta segue o seguinte padrão: dados brutos são ingeridos, passam por processamento automático utilizando expressões regulares e modelos de Processamento de Linguagem Natural, geram um relatório em um arquivo PDF e por fim enviam dados para a próxima etapa, a rotulagem do modelo.

## Estrutura de Diretórios

```         
processamento/
├── .env                           # Arquivo de variáveis de ambiente
├── docker-compose.yml             # Configuração do container Docker
├── data/                          # Diretório de armazenamento de dados
│   ├── raw/                       # Dados brutos (entrada)
│   └── processed/                 # Dados processados (intermediários)
├── scripts/                       # Scripts de processamento
│   └── qmd/                       # Documentos Quarto Markdown
│       └── tratamento_falabr.qmd  # Script principal de tratamento
└── outputs/                       # Resultados finais
    └── pdf/                       # Arquivos PDF gerados
```

## Funcionalidade de Cada Componente

### 1. Arquivo `docker-compose.yml` (Orquestração em Container)

Define o ambiente containerizado onde o processamento é executado. Configurações principais:

- **Serviço**: `motor-processamento`
- **Imagem**: `motor-anonimizacao-base` (imagem Docker personalizada com todas as dependências)
- **Container**: `pipeline-processamento`
- **Variáveis de Ambiente**: Carregadas do arquivo `.env`
- **Volumes Montados**:
  - `ABNT/` e `_quarto.yml` da raiz do projeto (formatação dos relatórios)
  - `../rme` montado em `/app/rme` dentro do container — **acoplamento direto com a próxima etapa**: o script escreve o arquivo `dataset_para_rotular.csv` diretamente na pasta `rme/data/raw/csv/` do host. A pasta `rme/` precisa existir no mesmo nível que `processamento/` antes de rodar este container.
  - Pastas `data/`, `scripts/` e `outputs/` do processamento
- **Diretório de Trabalho**: `/app` dentro do container
- **Comando de Execução**: Renderiza o documento Quarto e move os PDFs gerados

### 2. Diretório `data/` (Gerenciamento de Dados)

#### Subpasta `raw/`

Armazena os dados brutos obtidos diretamente da API do Fala.BR. Contém a subpasta `txt/` com o arquivo `ids_manifestacoes.txt`, gerado automaticamente pelo script durante a primeira fase de extração. Esse arquivo lista um `IdManifestacao` por linha e é usado como referência para a segunda fase (busca dos detalhes de cada manifestação).

#### Subpasta `processed/`

Armazena dados intermediários resultantes das etapas de processamento. Estes arquivos são gerados durante a execução do script e servem como ponto de transição entre dados brutos e o relatório final.

### 3. Diretório `scripts/qmd/` (Lógica de Processamento)

#### Arquivo `tratamento_falabr.qmd`

Este é o arquivo central que orquestra todo o processo de anonimização. É um documento Quarto Markdown, que combina código Python com documentação técnica estruturada.

**Funções Principais**:

1.  **Importação de Bibliotecas**:
    - pandas: manipulação de dados estruturados
    - spacy: processamento de linguagem natural
    - requests: requisições HTTP para APIs
    - regex (re): expressões regulares para identificação de padrões
    - torch e transformers: modelos de deep learning
2.  **Autenticação e Ingestão de Dados**:
    - Utiliza o TOKEN_API_OUVIDORIA do arquivo .env
    - Consome dados da API de ouvidoria em lotes
3.  **Identificação de Entidades Sensíveis**:
    - Aplica expressões regulares para padrões específicos (CPF, CNPJ, etc)
4.  **Anonimização de Dados**:
    - Substitui informações identificáveis por marcadores genéricos (ex: \[ANONIMIZADO\])
    - Mantém a estrutura e contexto dos dados
    - Garante que dados relacionados entre si sejam consistentemente anonimizados
5.  **Fatiamento do Texto (Chunking)**:
    - Fatiamento do texto utilizando o modelo `pt_core_news_lg`.
6.  **Geração de Relatório**:
    - Compila estatísticas do processamento
    - Cria visualizações dos dados tratados
    - Exporta o resultado como PDF

### 4. Diretório `outputs/pdf/` (Resultados)

Armazena os arquivos PDF gerados após o processamento. Estes documentos contêm:

- Relatório estruturado com os dados gerados pelo pipeline
- Gráficos e visualizações de análise
- Metadados sobre o processamento realizado
- Estatísticas sobre entidades mascaradas

## Como Utilizar

### Pré-requisitos

- Docker instalado e em execução
- Docker Compose instalado
- Acesso à rede (para consumir a API de ouvidoria)
- Arquivo `.env` devidamente configurado com token válido

### Executando o Processamento

1.  **Crie o arquivo `.env`**: Na raiz da pasta `processamento`/, crie um arquivo vazio chamado `.env`. Abra-o em um editor de texto, adicione a varíavel `TOKEN_API_OUVIDORIA`. Se atente ao tipo de arquivo, ele não pode possuir nenhum tipo, sendo apenas `.env`.

- Exemplo Correto: `.env`

- Exemplo Incorreto: `.env.txt`

- Abra-o em um editor de texto, adicione a varíavel `TOKEN_API_OUVIDORIA` e adicione o seu token de acesso da API após o `=`, assim como no exemplo abaixo.

``` bash
TOKEN_API_OUVIDORIA=insira_seu_token_valido_aqui
```

2.  **Navegue até o diretório processamento**:

``` bash
cd processamento
```

3.  **Inicie o container Docker**:

``` bash
docker-compose up
```

4.  **Finalizando o container Docker**: Ao finalizar a pipeline execute o comando abaixo para remover o container:

``` bash
docker-compose down
```

O Docker Compose irá: - Montar todos os volumes - Executar o comando de renderização do Quarto - Gerar o arquivo PDF em `outputs/pdf/`

4.  **Acompanhe o progresso**: O terminal exibirá os logs do processamento em tempo real (download de lotes, aplicação de RegEx/NER e chunking do texto). Aguarde até que o terminal indique que o comando foi finalizado com sucesso.

5.  **Verifique os resultados**: Os arquivos PDF processados estarão disponíveis em `outputs/pdf/`.

## Como Definir o Período de Extração (`DATA_INICIO` e `DATA_FIM`)

A janela de datas da extração é controlada por duas variáveis de ambiente, **sem necessidade de editar o código-fonte**:

| Variável      | Formato      | Padrão (se não definida) |
|---------------|--------------|--------------------------|
| `DATA_INICIO` | `DD/MM/AAAA` | `01/01/2026`             |
| `DATA_FIM`    | `DD/MM/AAAA` | data atual (`hoje`)      |

**Comportamento padrão** — subir o container sem definir nada coleta de **01/01/2026 até hoje**:

``` bash
docker-compose up
```

**Definindo um período específico** — exporte as variáveis antes de subir o container. O Docker Compose as injeta automaticamente no pipeline:

``` bash
# Linux / macOS / Git Bash
DATA_INICIO=01/06/2026 DATA_FIM=30/06/2026 docker-compose up
```

``` powershell
# Windows PowerShell
$env:DATA_INICIO="01/06/2026"; $env:DATA_FIM="30/06/2026"; docker-compose up
```

Definir apenas `DATA_INICIO` mantém `DATA_FIM` no padrão (hoje). Se `DATA_INICIO` for posterior a `DATA_FIM`, o pipeline interrompe a execução com um erro de validação.

## Como Personalizar os Filtros de Extração

Por padrão, o script de ingestão está configurado para coletar todo o acervo de manifestações a partir de **01/01/2026 até a data atual** (ajustável pelas variáveis `DATA_INICIO`/`DATA_FIM` descritas acima). Contudo, as necessidades de análise podem variar com a injeção de filtros adicionais da API (ex: tipo de formulário, situação da manifestação).

Localize o bloco de código Python responsável pela requisição, especificamente onde o dicionário `parametros` é definido. O código padrão se parece com isto:

``` python
parametros = {
    "dataCadastroInicio": str_data,
    "dataCadastroFim": str_data
}
```

A API do Fala.BR suporta a injeção de múltiplos filtros adicionais. Para consultar a lista completa de campos, chaves e formatos aceitos, acesse a [Documentação Oficial do Manual da API Fala.BR](https://falabr.cgu.gov.br/Help/Api?apiId=GET-api-manifestacoes_NumProtocolo_DataCadastroInicio_DataCadastroFim_DataPrazoRespostaInicio_DataPrazoRespostaFim_DataAtualizacaoInicio_DataAtualizacaoFim_IdSituacaoManifestacao_ApenasDenunciasAptas_ApenasComApuracaoDeEmpresa_ApenasComApuracaoDeServidor_IdTipoFormulario_MaxResultados_PosInicioPagina_OrderBy).

Salve o arquivo após a alteração. Na próxima vez que o comando `docker-compose up` for executado, o pipeline respeitará os novos filtros aplicados na ingestão.

## Como Adaptar as Expressões Regulares (Regex) para Regras de Negócio

Por padrão, o pipeline inclui uma etapa de pré-anonimização baseada em expressões regulares (regex). Esse processo varre os textos das manifestações para identificar e ocultar dados sensíveis comuns (como CPF, CNPJ, e-mails, placas de veículos e telefones), substituindo-os automaticamente pela tag `[ANONIMIZADO]`. Contudo, as necessidades de proteção de dados e análise podem variar (ex: necessidade de ocultar um número de matrícula de servidor específico ou manter determinados identificadores numéricos que não sejam sensíveis).

Você pode alterar os critérios e padrões de anonimização diretamente no código-fonte. Para isso, abra o arquivo `scripts/qmd/tratamento_falabr.qmd` utilizando qualquer ferramenta de edição de texto (como VS Code, RStudio, ou até mesmo o Bloco de Notas).

Localize o bloco de código Python responsável pela limpeza dos textos, especificamente onde o dicionário `patterns` é definido e a função de substituição é criada. O código padrão se parece com isto:

``` python
patterns = {
    "EMAIL": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "URL": r'https?:\/{1,2}[^\s"<>]+|www\.[^\s"<>]+',
    "MANIFESTACAO": r"\d{5}(?:[.\-/_\s]*)\d{6}(?:[.\-/_\s]*)/?(?:[.\-/_\s]*)\d{4}(?:[.\-/_\s]*)\d{2}",
    "CNPJ": r"\d{2}(?:[.\-/_\s]*)\d{3}(?:[.\-/_\s]*)\d{3}(?:[.\-/_\s]*)(?:[.\-/_\s]*)\d{4}(?:[.\-/_\s]*)\d{2}",
    "CPF": r"\d{3}(?:[.\-/_\s]*)\d{3}(?:[.\-/_\s]*)\d{3}(?:[.\-/_\s]*)\d{2}",
    "PLACA": r"([A-Za-z]{3}[.\-/_\s]*\d{4})|([A-Za-z]{3}[.\-/_\s]*\d[.\-/_\s]*[A-Za-z][.\-/_\s]*\d{2})",
    "TELEFONE": r"(?:\+?55[.\-/_\s]*)?(?:\(?\d{2}\)?[.\-/_\s]*)?(?:9[.\-/_\s]*)?\d{4}[.\-/_\s]*\d{4}",
    "RG": r"\d{1,3}(?:[.\-_\s]*)\d{3}(?:[.\-_\s]*)\d{2,3}(?:[.\-_\s]*)[\dXx]",
    "CEP": r"\d{5}(?:[.\-/_\s]*)\d{3}",
    "REDACTED": r"\d{6,}"
}
```

Para adaptar esse código às suas regras negociais, você pode adicionar novas chaves ao dicionário `patterns` ou modificar as existentes. Observe que os padrões atuais utilizam extensivamente o grupo de captura não-nomeado `(?:[.\-/_\s]*)` para lidar com digitações sujas — como pontos, traços, barras e espaços irregulares inseridos pelos cidadãos durante a digitação.

- **Adicionando novas regras:** Se o seu órgão utiliza um formato de processo interno padrão (ex: Número Único de Protocolo - NUP), você pode mapeá-lo adicionando uma nova linha ao dicionário: `"NUP": r"\d{5}\.\d{6}/\d{4}-\d{2}"`.
- **Ajustando o rigor da limpeza:** Se a regra genérica de segurança `"REDACTED"` (que oculta preventivamente qualquer sequência de 6 ou mais números) estiver apagando dados numéricos importantes para a sua análise estatística, você pode removê-la do dicionário ou aumentar o limite de dígitos (ex: alterando para `r"\d{10,}"`).

Para testar a eficácia de novas expressões regulares ou consultar a sintaxe antes de aplicá-las ao script, acesse plataformas de simulação como o [Regex101](https://regex101.com/) ou consulte a [Documentação Oficial do Módulo 're' do Python](https://docs.python.org/pt-br/3/library/re.html).

Salve o arquivo após a alteração. Na próxima vez que o fluxo de tratamento dos dados for executado, os textos originais das manifestações serão anonimizados respeitando os novos padrões configurados.

## Fluxo de Dados

```         
API Ouvidoria (Dados Brutos)
        ↓
Autenticação Segura [Token do .env]
        ↓
Coleta e Importação de Dados
        ↓
Identificação de Padrões (Regex)
        ↓
Divisão do Texto em Partes Menores (Chunking)
        ↓
Exportação para Pasta rme/ (Rotulação do Texto)
        ↓
Salvamento de backup dos dados na pasta data/processed/
        ↓
Geração do Relatório Final em PDF
```

## Dependências Externas

As seguintes bibliotecas Python são utilizadas (especificadas em `requirements.txt`):

- **pandas**: Manipulação e transformação de dados tabulares
- **requests**: Requisições HTTP para APIs externas
- **spacy**: Processamento de linguagem natural e extração de entidades
- **transformers**: Acesso a modelos de deep learning pré-treinados
- **torch**: Framework de machine learning (backend do transformers)
- **regex (re)**: Expressões regulares para padrões customizados
- **plotly, matplotlib, seaborn**: Visualizações de dados
- **python-dotenv**: Carregamento de variáveis de ambiente

## Tratamento de Erros Comuns

### Erro: "Token inválido ou expirado"

- Verifique se o TOKEN_API_OUVIDORIA no `.env` é válido e não expirou
- Solicite um novo token ao administrador do sistema

### Erro: "Imagem Docker não encontrada"

- Execute: `docker build -t motor-anonimizacao-base -f Dockerfile .` na pasta raiz do projeto antes de executar a etapa `processamento/`.

### Processamento muito lento

- Aumente recursos alocados ao Docker (CPU/memória)

## Próximas Etapas do Projeto

Após o processamento nesta pasta, os dados preparados para rotulação serão exportados para a pasta `rme/`. A próxima etapa consiste nos seguintes tópicos:

- Rotulação Manual de Entidades (RME)
- Preparação da base anotada para futuro fine-tuning do modelo

## Contato e Suporte

Para dúvidas sobre o funcionamento desta pasta ou reportar problemas, consulte a documentação adicional nas pastas irmãs ou contacte o time de desenvolvimento da COATD.