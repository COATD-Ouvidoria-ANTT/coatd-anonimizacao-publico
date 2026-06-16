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
├── data/                                   # Diretório de armazenamento de dados
│   ├── raw/                                # Dados de entrada
│   │   └── txt/                            # Diretório de dados textuais
│   │       └── ids_manifestacoes.txt       # IDs extraídos da API do Fala.BR
│   └── processed/                          # Dados de saída (Anonimizados)
│       ├── csv/                            # Exportação em texto delimitado
│       │   └── data_anonimizado.csv        # Arquivo final com texto anonimizado
│       └── xlsx/                           # Exportação para planilhas
│           └── data_anonimizado.xlsx       # Arquivo final com texto anonimizado
├── outputs/                                # Resultados visuais e gerenciais
│   └── pdf/                                # Arquivos do Relatório de Treinamento
│       └── relatorio_pipeline.pdf          # Relatório gerado com métricas de ofuscação
└── scripts/                                # Lógica de processamento
    └── qmd/                                # Documentos Quarto Markdown
        └── pipeline_anonimizacao.qmd       # Script central que orquestra todo o fluxo
```

------------------------------------------------------------------------

## Funcionalidade de Cada Etapa do Processamento

O script central (`pipeline_anonimizacao.qmd`) é dividido em blocos lógicos executados sequencialmente:

### 1. Extração de Dados (API Fala.BR)

O sistema se autentica na API do Fala.BR utilizando credenciais seguras e realiza a ingestão das manifestações do dia. O processo primeiro coleta as chaves identificadoras (`IdManifestacao`) e depois busca o teor textual de cada registro, montando a base de trabalho bruta.

### 2. Diagnóstico e Limpeza Prévia

Realiza uma análise exploratória rápida para verificar se há dados nulos ou erros de formatação. Remove espaços em branco excessivos e caracteres de pontuação duplicados que poderiam confundir a Inteligência Artificial.

### 3. Aplicação de Expressões Regulares (Regex)

Varre o texto em busca de padrões matematicamente definíveis. Se encontrar um e-mail, um link, um CPF, CNPJ, RG, CEP, Telefone ou Placa Veicular, o sistema aplica imediatamente a máscara `[ANONIMIZADO]`.

### 4. Segmentação de Sentenças (*Chunking*)

Modelos de Inteligência Artificial baseados em Transformers (como o BERT) possuem um limite de leitura (geralmente 512 *tokens/subwords* por vez). Para que textos muito longos não sejam cortados pela metade, o pipeline usa o `spaCy` para dividir a manifestação de forma inteligente, quebrando-a no final de cada frase (ponto final), sem perder o contexto gramatical.

### 5. Inferência do Modelo NER (Inteligência Artificial)

As frases cortadas são enviadas para o nosso modelo treinado localmente (`model-best`). O modelo lê a frase, compreende o contexto e identifica nomes de pessoas, empresas e localidades, substituindo-os pelas tags de proteção correspondentes (ex: `[NOME]`, `[EMPRESA]`).

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

## Como Executar o Pipeline

### Pré-requisitos e Execução

O texto original foi refinado para corrigir pequenos erros de digitação e garantir clareza no processo de configuração do `.env` e mapeamento do modelo. A numeração também foi corrigida.

**Pré-requisitos:**

* **Modelo de IA Disponível:** Certifique-se de que o modelo treinado (`model-best`) gerado na etapa anterior está corretamente posicionado na pasta `ner/models/v1_modelo_inicial/`. O modelo não foi copiado para a pasta `anonimizacao/` devido ao seu tamanho elevado. Para economizar espaço em disco e evitar redundâncias, o modelo foi mantido na pasta original e é consumido de forma inteligente apontando como um volume durante a criação do container.
* **Variáveis de Ambiente (.env):** Tenha o arquivo `.env` na raiz do projeto contendo o `TOKEN_API_OUVIDORIA` válido. Se você seguiu a ordem cronológica do projeto, este arquivo já foi criado na pasta `processamento/`. Basta copiá-lo para a raiz da pasta `anonimizacao/`.
* **Criação Manual do .env (Caso pule etapas):** Na raiz da pasta `anonimizacao/`, crie um arquivo vazio e renomeie-o estritamente para `.env` (sem nenhuma extensão oculta, como `.txt`). Abra-o em um editor de texto e insira o seu token de acesso da API após o sinal de igual, conforme o exemplo:

```bash
TOKEN_API_OUVIDORIA=insira_seu_token_valido_aqui

```

1. **Navegue até a pasta do pipeline:** Abra o seu terminal e acesse a pasta correspondente:

```bash
cd anonimizacao

```

2. **Inicie o container Docker:**

```bash
docker-compose up
```

3. **Verifique as Saídas:** Após a conclusão, os dados limpos e prontos para uso seguro pela equipe estarão disponíveis em `data/processed/xlsx/` e `data/processed/csv/` (com separador `;`). Por fim, o relatório de impacto estará na pasta `outputs/pdf/`.

---

## Como Personalizar os Filtros de Extração

Por padrão, o script de ingestão está configurado para coletar todo o acervo de manifestações a partir de **01/01/2026 até a data atual**. Contudo, as necessidades de análise podem variar (ex: necessidade de extrair apenas denúncias, filtrar por tipo de formulário ou focar em manifestações com apuração de servidor).

Você pode alterar os critérios da busca diretamente no código-fonte. Para isso, abra o arquivo `scripts/qmd/anonimizacao_falabr.qmd` utilizando qualquer ferramenta de edição de texto (como VS Code, RStudio, ou até mesmo o Bloco de Notas).

Localize o bloco de código Python responsável pela requisição, especificamente onde o dicionário `parametros` é definido. O código padrão se parece com isto:

```python
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

- **Hardware Acceleration (Upgrade de Infraestrutura):** Implantação de clusters ou estações de trabalho equipadas com GPUs dedicadas para escalar o processamento e viabilizar a anonimização imediata de centenas de milhares de manifestações retroativas.
- **Automação Contínua (Agendamento):** Orquestrar a execução deste script para rodar de forma automática todos os dias, integrando as saídas (dados anonimizados) para consumo imediato em ferramentas de *Business Intelligence* do seu Órgão.

## Contato e Suporte

Para dúvidas sobre a arquitetura do código, calibração das expressões regulares ou relato de problemas na execução do pipeline, entre em contato com a equipe de desenvolvimento da COATD.