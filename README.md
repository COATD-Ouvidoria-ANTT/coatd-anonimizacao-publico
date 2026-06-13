# Projeto de Anonimização de Manifestações (Ouvidoria ANTT)

**Coordenação de Análise e Tratamento de Dados (COATD)**

Este repositório contém a arquitetura completa para extração, processamento, rotulação e ofuscação de dados sensíveis (PII) do sistema Fala.BR. Toda a solução foi desenhada para processamento estritamente local (*on-premises*) utilizando Inteligência Artificial (Deep Learning e NLP) e Expressões Regulares (Regex), garantindo conformidade total com a LGPD sem a necessidade de envio de dados para nuvens externas.

---

## Estrutura do Repositório

O repositório é modular e dividido em pastas com responsabilidades específicas. Cada diretório possui sua própria documentação técnica detalhada (`README.md` interno).

```text
coatd-anonimizacao-publico/
├── ABNT/                 # Regras globais de formatação e estilos para os relatórios
├── anonimizacao/         # Pipeline final de produção (Extração -> Ofuscação -> Exportação)
├── ner/                  # Motor de Inteligência Artificial (Treinamento e Fine-Tuning)
├── processamento/        # Scripts de preparação prévia de dados para a equipe de rotulação
├── rme/                  # Aplicação Web para Rotulação Manual de Entidades (Interface Humana)
├── _quarto.yml           # Configurações globais de renderização de documentos
├── .dockerignore         # Exclusões de contexto para otimização do build
├── .gitignore            # Exclusões de versionamento de arquivos sensíveis/locais
├── .gitattributes        # Padronização de finais de linha para ambientes Linux/Windows
├── Dockerfile            # Receita da imagem base com todo o ecossistema de Data Science
└── requirements.txt      # Dependências e bibliotecas Python do projeto
```

---

## Arquivos de Configuração e Infraestrutura

A raiz do projeto contém arquivos essenciais que padronizam a formatação dos relatórios, garantem a segurança do versionamento e definem o ambiente de execução.

### Diretório ABNT e Citações Bibliográficas

A pasta `ABNT/` contém os arquivos responsáveis pela formatação acadêmica e técnica dos relatórios gerados pelo Quarto. Ela possui dois arquivos:

* `abnt.csl`: Arquivo de linguagem de estilo de citação que define as regras visuais da Associação Brasileira de Normas Técnicas (ABNT).
* `referencias.bib`: Um banco de dados em formato texto que armazena todas as referências bibliográficas do projeto.

**Como adicionar novas citações:**
Para incluir uma nova referência (como leis, artigos ou documentações técnicas), abra o arquivo `referencias.bib` e adicione a entrada no formato BibTeX. Por exemplo:

```bibtex
@legislation{lgpd2018,
  title   = {Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD)},
  author  = {{Brasil}},
  year    = {2018},
  url     = {https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm}
}
```

Nos scripts `.qmd`, basta utilizar a sintaxe `[@lgpd2018]` e o Quarto formatará automaticamente a citação no texto e gerará a lista de referências ao final do PDF.

### Configuração Global do Quarto (`_quarto.yml`)

O arquivo `_quarto.yml` atua como o modelo mestre para a renderização de todos os relatórios do projeto. Ele centraliza as regras visuais para que não seja necessário repeti-las em cada script.

Suas principais definições incluem:

* **Motor de Renderização:** Utiliza o `xelatex` para converter o Markdown em PDF de alta qualidade.
* **Estrutura do Documento:** Gera sumários automáticos (`toc: true`), numera as seções e aplica margens padronizadas (superior/inferior de 2.5cm, laterais de 3cm).
* **Cabeçalhos e Rodapés:** Configura o pacote LaTeX `fancyhdr` para injetar automaticamente "Relatório Técnico" e "Processo de Anonimização" no topo das páginas, além da numeração no rodapé.
* **Integração Bibliográfica:** Aponta automaticamente para os arquivos `abnt.csl` e `referencias.bib` explicados acima.

### Segurança de Dados (`.gitignore`)

Como este projeto lida com dados sensíveis da Ouvidoria, o `.gitignore` foi rigorosamente configurado para impedir vazamentos e manter o repositório leve:

* **Bloqueio de Credenciais:** Impede o versionamento do arquivo `.env`, garantindo que o token da API da CGU nunca seja exposto no controle de versão.
* **Bloqueio de Dados (LGPD):** Ignora todas as extensões de dados (`.csv`, `.xlsx`, `.json`, `.txt`) dentro das pastas `data/raw/` e `data/processed/`.
* **Bloqueio de Modelos Pesados:** Ignora a pasta `models/`, evitando que o repositório trave ao tentar subir redes neurais de vários gigabytes.
* **Preservação de Estrutura:** Utiliza a estratégia de exceção com arquivos vazios `!/.gitkeep`. Isso garante que as pastas sejam criadas na máquina de outros desenvolvedores, mesmo sem enviar os dados que deveriam estar dentro delas.

### Padronização de Finais de Linha (`.gitattributes`)
Este arquivo previne de forma invisível falhas de compatibilidade entre sistemas operacionais (Windows, Mac, Linux). Ele instrui o Git a forçar o padrão de quebra de linha LF (Line Feed) para códigos e scripts (`.sh`, `.yml`, `.py`, `.qmd`, `.json`).

### Otimização de Construção (`.dockerignore`)

Este arquivo define o que é enviado para o "contexto de build" quando você roda o comando de criação da imagem base do Docker. Ele foi configurado com uma abordagem extrema de "negação por padrão":

```text
*
!requirements.txt
!Dockerfile
```

**Por que foi feito assim?**
A imagem Docker deste projeto atua puramente como um "motor" de processamento. Ela só precisa conhecer a receita de instalação (`Dockerfile`) e a lista de bibliotecas (`requirements.txt`).
Todo o resto (scripts, modelos e dados) é bloqueado pelo `.dockerignore` para não ser "chumbado" dentro da imagem. A conexão entre o motor Docker e o código do projeto ocorre em tempo de execução através do mapeamento de **volumes** (descrito nos arquivos `docker-compose.yml` de cada pasta), permitindo que você altere o código Python sem precisar reconstruir a imagem gigante de 30 minutos.

### Controle de Versões de Bibliotecas (`requirements.txt`)

Este arquivo contém o ecossistema Python necessário para sustentar a aplicação. O versionamento explícito (ex: `spacy==3.8.14`, `torch==2.11.0`, `pandas==3.0.2`) garante a total reprodutibilidade do projeto. Se o código for executado em outra máquina, no futuro, as dependências instaladas serão cirurgicamente as mesmas, evitando que atualizações de bibliotecas quebrem a lógica ou as métricas de Deep Learning.

As dependências abrangem cinco grandes áreas do projeto:

1. **Manipulação de Dados:** `pandas`, `openpyxl`, `numpy`.
2. **Integração e Ambiente:** `requests` (para a API), `python-dotenv`.
3. **Inteligência Artificial (NLP):** `spacy`, `transformers`, `spacy-transformers`, `torch`.
4. **Interface Web (Rotulador):** `Flask`, `flask-cors`.
5. **Visualização e Relatórios:** `matplotlib`, `seaborn`, `plotly`, `tabulate`.

## Ordem Cronológica de Execução (O Fluxo de Trabalho)

Para que o projeto funcione corretamente, as pastas devem ser operadas em uma sequência lógica, onde a saída de uma etapa é a entrada da seguinte. O fluxo de vida dos dados segue esta ordem:

1. **`processamento/` (Preparação):** Onde tudo começa. Os dados brutos são ingeridos da API, passam por uma limpeza básica e são fatiados em blocos de texto menores (*chunking*). O resultado é exportado para a etapa seguinte.
2. **`rme/` (O Fator Humano):** Utiliza os dados processados para alimentar a Ferramenta de Rotulação Manual. A equipe utiliza a interface para ensinar à máquina o que é um nome, uma empresa ou um endereço.
3. **`ner/` (Aprendizado de Máquina):** Pega a base de dados que a equipe acabou de rotular na etapa anterior e treina o modelo de Inteligência Artificial (*Fine-tuning* do spaCy/Transformers), gerando o artefato final inteligente (`model-best`).
4. **`anonimizacao/` (Produção):** A etapa definitiva. Importa o modelo treinado na etapa 3 e roda o pipeline diário: extrai dados novos, aplica regras estáticas (Regex), roda a IA para o que for complexo e cospe a planilha final completamente anonimizada e segura para uso analítico.

---

## Configuração Inicial: O Motor Base (Docker)

Toda a arquitetura deste projeto roda dentro de containers isolados para garantir que funcione perfeitamente em qualquer máquina. Para isso, precisamos construir a imagem base **uma única vez**.

O arquivo `Dockerfile` na raiz do projeto é extremamente robusto. Ele instala automaticamente o Python 3.13, o motor da linguagem R, o sistema de relatórios Quarto, o processador de PDFs TinyTeX, e faz o download de modelos linguísticos pré-treinados gigabytes de tamanho.

Para construir este motor, abra o terminal na pasta raiz e execute:

```bash
docker build -t motor-anonimizacao-base .
```

> **Aviso Importante sobre o Tempo de Instalação:**
> Devido ao tamanho dos componentes de Deep Learning, linguagens e processadores de texto integrados, **este download e compilação podem demorar cerca de 30 minutos** dependendo da sua conexão com a internet. Não feche o terminal. Este é um processo de configuração inicial executado apenas uma vez; após criado, os containers das pastas iniciarão em poucos segundos.

## Tecnologias Utilizadas

O ecossistema do projeto foi construído empregando as ferramentas mais sólidas do mercado de Ciência de Dados e Engenharia de Software:

* **Python** Linguagens base para processamento de dados e estatística.
* **spaCy** Arquitetura central para o Processamento de Linguagem Natural e redes neurais.
* **Flask:** Backend ágil para sustentar a ferramenta web de rotulação humana.
* **Quarto Markdown:** Motor analítico de ponta para a geração interativa e automatizada de relatórios gerenciais e acompanhamento de métricas.
* **Docker:** Orquestração e padronização do ambiente de execução.

## Contato

Para aprofundar-se no funcionamento técnico de cada etapa, navegue até as pastas individuais e consulte seus respectivos arquivos `README.md`. Para manutenção evolutiva ou suporte à infraestrutura, acione a Coordenação de Análise e Tratamento de Dados (COATD).