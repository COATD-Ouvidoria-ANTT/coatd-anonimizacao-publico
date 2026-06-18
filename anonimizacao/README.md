# Pasta Pipeline de Anonimização - Documentação Técnica

## Visão Geral

Esta pasta contém o pipeline principal e definitivo de processamento e anonimização de dados da Ouvidoria da ANTT. É o motor que consolida todas as etapas do projeto em um fluxo contínuo, unindo regras lógicas à Inteligência Artificial.

O objetivo deste pipeline é garantir a conformidade com a Lei Geral de Proteção de Dados (LGPD), ofuscando Informações Pessoais Identificáveis (PII) sem perder o contexto analítico das manifestações. Para garantir a segurança absoluta das informações, **todo o processamento é executado de forma estritamente local (*on-premises*)**, sem qualquer envio de dados para servidores externos ou serviços de LLM em nuvem.

O pipeline utiliza uma abordagem híbrida de alta eficiência:

1.  **Camada Estática (Regex):** Rápida e determinística, remove padrões fixos como CPFs, e-mails e placas de veículos.
2.  **Camada Estocástica (Deep Learning / NER):** O modelo treinado nas etapas anteriores analisa o contexto da frase para encontrar nomes próprios, empresas e endereços que não possuem formato fixo.

## Estrutura de Diretórios

```         
anonimizacao/
├── data/                                                 # Diretório de armazenamento de dados
│   ├── raw/                                              # Dados de entrada
│   │   └── txt/                                          # Diretório de dados textuais
│   │       └── ids_manifestacoes.txt                     # IDs extraídos da API do Fala.BR
│   └── processed/                                        # Dados de saída (Anonimizados)
│       ├── csv/                                          # Exportação em texto delimitado
│       │   └── data_anonimizado.csv                      # Arquivo final com texto anonimizado
│       └── xlsx/                                         # Exportação para planilhas
│           └── data_anonimizado.xlsx                     # Arquivo final com texto anonimizado
├── outputs/                                              # Resultados visuais e gerenciais
│   └── pdf/                                              # Arquivos do Relatório de Treinamento
│       └── relatorio_pipeline.pdf                        # Relatório gerado com métricas de ofuscação
└── scripts/                                              # Lógica de processamento
    └── qmd/                                              # Documentos Quarto Markdown
        └── anonimizacao_falabr.qmd                        # Script central que orquestra todo o fluxo
        └── anonimizacao_falabr_transformers.qmd          # Script que orquestra o fluxo avançado com arquitetura Transformers (GPU)
```

------------------------------------------------------------------------

## Funcionalidade de Cada Componente

### 1. Diretório `data/raw/` (Entrada Bruta)

Atua como o ponto de partida do pipeline. Ele armazena os artefatos iniciais necessários para a ingestão de dados, especificamente na subpasta `txt/`, que contém o arquivo `ids_manifestacoes.txt`. Este arquivo serve como referência de chaves identificadoras para o sistema buscar o teor textual de cada registro diretamente na API do Fala.BR.

### 2. Script Central (`pipeline_anonimizacao.qmd`)

Um documento interativo Quarto que orquestra todo o fluxo de processamento e ofuscação de dados sensíveis. Ele consolida o pipeline executando o trabalho pesado em blocos lógicos:

* **Extração:** Conecta-se à API do Fala.BR de forma segura para baixar os textos brutos das manifestações.
* **Limpeza e Regex:** Aplica a Camada Estática para varrer e ofuscar dados padronizados (CPF, e-mails, placas e telefones).
* **Chunking:** Fatiamento inteligente do texto utilizando o `spaCy` para criar sentenças contextuais que não ultrapassem o limite de leitura da Inteligência Artificial.
* **Inferência NER:** Submete as frases à Camada Estocástica, utilizando o modelo local treinado (`model-best`) para localizar e mascarar nomes, empresas e localidades.
* **Recomposição e Exportação:** Remonta o texto completamente anonimizado e o salva nos formatos de destino.

### 2.1. Script de Anonimização Avançado (`pipeline_anonimizacao_transformers.qmd`)

Um documento Quarto semelhante ao principal, porém projetado para executar a etapa de inferência de Inteligência Artificial utilizando a arquitetura profunda de Transformers.

**Por que um script semelhante foi feito?**
Para flexibilizar o processamento de acordo com o hardware da máquina que executará a rotina. Enquanto o script padrão é altamente otimizado para rodar em CPU, esta versão foi desenhada para explorar a aceleração matemática de placas de vídeo (GPUs) dedicadas, viabilizando o processamento em massa de todo o histórico retroativo da Ouvidoria em tempo recorde.

### 3. Diretório `data/processed/` (Saída Final)

É o repositório definitivo onde os dados higienizados e seguros são disponibilizados para consumo. Após o processamento, as manifestações anonimizadas são entregues em dois formatos acessíveis: `csv/` (texto delimitado, ideal para ingestão automatizada em bancos de dados) e `xlsx/` (planilhas prontas para leitura humana e análise por equipes não-técnicas).

### 4. Diretório `outputs/pdf/` (Relatório de Impacto)

Armazena o documento `relatorio_pipeline.pdf`, gerado automaticamente ao final de cada execução do script. Ele atua como um comprovante gerencial do processamento do dia, consolidando métricas e gráficos que demonstram visualmente o volume de informações pessoais (PII) bloqueadas pela Inteligência Artificial e pelas expressões regulares.

### 5. Arquivo `.env` e Orquestração (Configuração)

Embora não esteja explicitamente dentro das pastas, o pipeline depende de um arquivo `.env` na raiz do projeto para armazenar o token da API de forma segura. O ambiente como um todo é orquestrado via contêineres Docker (quando aplicável), que se encarregam de mapear volumes externos — consumindo o modelo de IA pesado da pasta anterior sem precisar duplicá-lo — e isolando todas as dependências de software.

---

## Funcionalidade de Cada Etapa do Processamento

Os scripts das (`pipeline_anonimizacao.qmd` e `pipeline_anonimizacao_transformers.qmd`) são divididos em blocos lógicos executados sequencialmente:

### 1. Extração de Dados (API Fala.BR)

O sistema se autentica na API do Fala.BR utilizando credenciais seguras e realiza a ingestão das manifestações do dia. O processo primeiro coleta as chaves identificadoras (`IdManifestacao`) e depois busca o teor textual de cada registro, montando a base de trabalho bruta.

### 2. Diagnóstico e Limpeza Prévia

Realiza uma análise exploratória rápida para verificar se há dados nulos ou erros de formatação. Remove espaços em branco excessivos e caracteres de pontuação duplicados que poderiam confundir a Inteligência Artificial.

### 3. Aplicação de Expressões Regulares (Regex)

Varre o texto em busca de padrões matematicamente definíveis. Se encontrar um e-mail, um link, um CPF, CNPJ, RG, CEP, Telefone ou Placa Veicular, o sistema aplica imediatamente a máscara `[ANONIMIZADO]`.

### 4. Segmentação de Sentenças (*Chunking*)

Modelos de Inteligência Artificial baseados em Transformers (como o BERT) possuem um limite de leitura (geralmente 512 *tokens/subwords* por vez). Para que textos muito longos não sejam cortados pela metade, o pipeline usa o `spaCy` para dividir a manifestação de forma inteligente, quebrando-a no final de cada frase (ponto final), sem perder o contexto gramatical.

### 5. Inferência do Modelo NER (Inteligência Artificial)

As frases cortadas são enviadas para o nosso modelo treinado localmente (`model-best`). O modelo lê a frase, compreende o contexto e identifica nomes de pessoas, empresas e localidades, substituindo-os pelas tags de proteção correspondentes (ex: `[NOME]`, `[EMPRESA]`). Essa é a única etapa com uma grande variação dentro do código, cada script (`pipeline_anonimizacao.qmd` e `pipeline_anonimizacao_transformers.qmd`) contêm o modelo treinado previamente de acordo com a abordagem escolhida.

### 6. Recomposição e Exportação

O script junta todas as frases anonimizadas de volta em seus textos originais completos. Em seguida, exporta a base final e limpa para formatos acessíveis (`.csv` e `.xlsx`), além de gerar gráficos mostrando o volume de dados sensíveis bloqueados no dia.

------------------------------------------------------------------------

## Fluxo de Dados

```         
API Fala.BR (Dados Brutos)
        ↓
Ingestão Local Segura [Token .env]
        ↓
Camada Estática: Limpeza + Regex (Ofuscação de CPF, CNPJ, E-mail, etc.)
        ↓
Chunking: Divisão inteligente do texto em blocos menores
        ↓
Camada Estocástica: IA / Modelo NER (Ofuscação de Nomes, Empresas, etc.)
        ↓
Reconstrução das manifestações tratadas
        ↓
Exportação Final (.csv, .xlsx e relatório em .pdf)
```

------------------------------------------------------------------------

## Como Executar o Pipeline de Anonimização

**Pré-requisitos:** Ter o arquivo `.env` configurado com o `TOKEN_API_OUVIDORIA` válido na raiz da pasta `anonimizacao/` e certificar-se de que o modelo de IA (`model-best`) está corretamente posicionado na pasta `ner/models/v1_modelo_inicial/`. O Docker e o Docker Compose devem estar instalados e em execução na máquina.

1. **Navegue até a pasta do pipeline:** Abra o seu terminal e acesse a pasta correspondente:

```bash
cd anonimizacao
```

2. **Inicie o container Docker:** Rode o comando abaixo para construir o ambiente e disparar o processamento de forma 100% automatizada:

```bash
docker-compose --profile cpu up
```

O Docker Compose irá:

* Carregar a imagem e montar os volumes necessários, mapeando o modelo de IA externamente.
* Autenticar e extrair os dados brutos das manifestações na API do Fala.BR.
* Aplicar a limpeza e o mascaramento por expressões regulares (Camada Estática).
* Fatiar o texto inteligentemente e rodar a inferência com o modelo NER (Camada Estocástica).
* Recompor os textos, exportar os dados seguros e compilar o relatório gerencial `relatorio_pipeline.pdf`.

3. **Finalizando o container Docker:** Ao finalizar a pipeline, execute o comando abaixo para remover o container e liberar os recursos da rede:

```bash
docker-compose --profile cpu down
```

4. **Verifique as Saídas:** Após a conclusão, os dados limpos e prontos para uso seguro pela equipe estarão disponíveis em `data/processed/xlsx/` e `data/processed/csv/` (com separador `;`). Por fim, o relatório de impacto estará na pasta `outputs/pdf/`.
---

## Como Executar o Pipeline de Anonimização Avançado (Transformers)

**Pré-requisitos:** Os mesmos listados acima (arquivo `.env` configurado e modelo posicionado). Para esta versão do pipeline, é **OBRIGATÓRIO** o uso de hardware com **GPU** (placa de vídeo) para processar grandes volumes de manifestações em um tempo viável.

1. **Navegue até a pasta do pipeline:** Abra o seu terminal e acesse a pasta correspondente:

```bash
cd anonimizacao
```

2. **Inicie o container Docker:** Rode o comando correspondente ao ambiente de transformers para disparar o processamento acelerado:

```bash
docker-compose --profile transformers up
```

3. **Finalizando o container Docker:** Ao finalizar a pipeline, execute o comando abaixo para remover o container:

```bash
docker-compose --profile transformers down
```

4. **Verifique as Saídas:** Semelhante ao fluxo padrão, os dados totalmente anonimizados estarão disponíveis nas subpastas de `data/processed/` e o relatório analítico estará na pasta `outputs/pdf/`.

---

## Como Definir o Período de Extração (`DATA_INICIO` e `DATA_FIM`)

A janela de datas da extração é controlada por duas variáveis de ambiente, **sem necessidade de editar o código-fonte**. Elas valem tanto para o perfil `cpu` quanto para o `transformers`:

| Variável | Formato | Padrão (se não definida) |
|---|---|---|
| `DATA_INICIO` | `DD/MM/AAAA` | `01/01/2026` |
| `DATA_FIM` | `DD/MM/AAAA` | data atual (`hoje`) |

**Comportamento padrão** — subir o container sem definir nada coleta de **01/01/2026 até hoje**:

``` bash
docker-compose --profile cpu up
```

**Definindo um período específico** — exporte as variáveis antes de subir o container. O Docker Compose as injeta automaticamente no pipeline:

``` bash
# Linux / macOS / Git Bash
DATA_INICIO=01/06/2026 DATA_FIM=30/06/2026 docker-compose --profile cpu up
```

``` powershell
# Windows PowerShell
$env:DATA_INICIO="01/06/2026"; $env:DATA_FIM="30/06/2026"; docker-compose --profile cpu up
```

Definir apenas `DATA_INICIO` mantém `DATA_FIM` no padrão (hoje). Se `DATA_INICIO` for posterior a `DATA_FIM`, o pipeline interrompe a execução com um erro de validação.

> Alternativamente, as variáveis podem ser fixadas no arquivo `.env` (junto ao `TOKEN_API_OUVIDORIA`), tornando o período persistente entre execuções.

## Como Personalizar os Filtros de Extração

Por padrão, o script de ingestão está configurado para coletar todo o acervo de manifestações a partir de **01/01/2026 até a data atual** (ajustável pelas variáveis `DATA_INICIO`/`DATA_FIM` descritas acima). Contudo, as necessidades de análise podem variar (ex: necessidade de extrair apenas denúncias, filtrar por tipo de formulário ou focar em manifestações com apuração de servidor).

Localize o bloco de código Python responsável pela requisição, especificamente onde o dicionário `parametros` é definido. O código padrão se parece com isto:

```python
parametros = {
    "dataCadastroInicio": str_data,
    "dataCadastroFim": str_data
}
```

É possível observar um *loop* após a segunda requisação (Requisação feita com os IDs extraídos), ele é responsável por extrair os campos do `.csv` ou `.xlsx` estruturado ao final do pipeline. Consulte o dicionário da API do Fala.BR, citado no link após o código abaixo, para entender a arquitetura do `.json` e ter propriedade para adicionar chaves e listas ao *loop* abaixo.

```python
dados_filtrados = []

for item in dados_completos:
    id_manifestacao = item.get("IdManifestacao")
    descricao = ((item.get("Teor") or {}).get("DescricaoAtosOuFatos") or {})

    linha_filtrada = {
        "id_mensagem": id_manifestacao,
        "descricao": descricao
    }
    
    dados_filtrados.append(linha_filtrada)
```

df = pd.DataFrame(dados_filtrados)

A API do Fala.BR suporta a injeção de múltiplos filtros adicionais. Para consultar a lista completa de campos, chaves e formatos aceitos, acesse a [Documentação Oficial do Manual da API Fala.BR](https://falabr.cgu.gov.br/Help/Api?apiId=GET-api-manifestacoes_NumProtocolo_DataCadastroInicio_DataCadastroFim_DataPrazoRespostaInicio_DataPrazoRespostaFim_DataAtualizacaoInicio_DataAtualizacaoFim_IdSituacaoManifestacao_ApenasDenunciasAptas_ApenasComApuracaoDeEmpresa_ApenasComApuracaoDeServidor_IdTipoFormulario_MaxResultados_PosInicioPagina_OrderBy).

Salve o arquivo após a alteração. Na próxima vez que o comando `docker-compose up` for executado, o pipeline respeitará os novos filtros aplicados na ingestão.

## Como Adaptar as Expressões Regulares (Regex) para Regras de Negócio

Por padrão, o pipeline inclui uma etapa de pré-anonimização baseada em expressões regulares (regex). Esse processo varre os textos das manifestações para identificar e ocultar dados sensíveis comuns (como CPF, CNPJ, e-mails, placas de veículos e telefones), substituindo-os automaticamente pela tag `[ANONIMIZADO]`. Contudo, as necessidades de proteção de dados e análise podem variar (ex: necessidade de ocultar um número de matrícula de servidor específico ou manter determinados identificadores numéricos que não sejam sensíveis).

Você pode alterar os critérios e padrões de anonimização diretamente no código-fonte. Para isso, abra o arquivo `scripts/qmd/anonimizacao_falabr.qmd` utilizando qualquer ferramenta de edição de texto (como VS Code, RStudio, ou até mesmo o Bloco de Notas).

Localize o bloco de código Python responsável pela limpeza dos textos, especificamente onde o dicionário `patterns` é definido e a função de substituição é criada. O código padrão se parece com isto:

```python
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

* **Adicionando novas regras:** Se o seu órgão utiliza um formato de processo interno padrão (ex: Número Único de Protocolo - NUP), você pode mapeá-lo adicionando uma nova linha ao dicionário: `"NUP": r"\d{5}\.\d{6}/\d{4}-\d{2}"`.
* **Ajustando o rigor da limpeza:** Se a regra genérica de segurança `"REDACTED"` (que oculta preventivamente qualquer sequência de 6 ou mais números) estiver apagando dados numéricos importantes para a sua análise estatística, você pode removê-la do dicionário ou aumentar o limite de dígitos (ex: alterando para `r"\d{10,}"`).

Para testar a eficácia de novas expressões regulares ou consultar a sintaxe antes de aplicá-las ao script, acesse plataformas de simulação como o [Regex101](https://regex101.com/) ou consulte a [Documentação Oficial do Módulo 're' do Python](https://docs.python.org/pt-br/3/library/re.html).

Salve o arquivo após a alteração. Na próxima vez que o fluxo de tratamento dos dados for executado, os textos originais das manifestações serão anonimizados respeitando os novos padrões configurados.

------------------------------------------------------------------------

## Dependências Externas

As seguintes bibliotecas e ferramentas formam a base operacional deste pipeline:

- **pandas & matplotlib/seaborn:** Utilizados para a manipulação dos dados tabulares e geração dos gráficos de volumetria de anonimização.
- **requests & python-dotenv:** Responsáveis pela comunicação segura com a API do Fala.BR e gerenciamento do token de acesso.
- **regex (re):** Motor de expressões regulares para a aplicação da camada estática de ofuscação de padrões fixos.
- **spaCy** Arquitetura central responsável pelo fatiamento sintático (*chunking*) e pela execução do nosso modelo de Inteligência Artificial (NER).
- **torch** Bibliotecas base (*backend*) de Deep Learning que fornecem a aceleração matemática necessária para rodar redes neurais locais.

------------------------------------------------------------------------

## Tratamento de Erros Comuns

### Erro de Conexão com o Fala.BR (Status Code diferente de 200)

- **Causa:** O token da API expirou, a URL da CGU está passando por instabilidades ou o limite de requisições foi atingido.
- **Solução:** Verifique a validade do seu `TOKEN_API_OUVIDORIA` no arquivo `.env`. Se o token for válido, tente rodar a extração novamente após alguns minutos.

### Erro de Memória (Out of Memory - OOM)

- **Causa:** O *garbage collector* (`gc.collect()`) não conseguiu liberar a memória RAM a tempo entre o processamento de lotes pesados da rede neural.
- **Solução:** Reduza o tamanho do lote (`batch_size`) na função de processamento de texto, alterando de `batch_size=100` para `batch_size=32` ou menor.

------------------------------------------------------------------------

## Próximas Etapas e Evolução Tecnológica

Com este pipeline consolidado e rodando localmente, os dados sensíveis estão resguardados. Os próximos passos para elevar o nível de maturidade do projeto incluem:

- **Automação Contínua (Agendamento):** Orquestrar a execução deste script para rodar de forma automática todos os dias, integrando as saídas (dados anonimizados) para consumo imediato em ferramentas de *Business Intelligence* do seu Órgão.

## Contato e Suporte

Para dúvidas sobre a arquitetura do código, calibração das expressões regulares ou relato de problemas na execução do pipeline, entre em contato com a equipe de desenvolvimento da COATD.