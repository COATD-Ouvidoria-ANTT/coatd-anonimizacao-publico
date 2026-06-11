FROM python:3.13.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    r-base \
    wget \
    curl \
    fonts-texgyre \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.9.28/quarto-1.9.28-linux-amd64.deb \
    && dpkg -i quarto-1.9.28-linux-amd64.deb \
    && rm quarto-1.9.28-linux-amd64.deb

RUN R -e "install.packages(c('knitr', 'rmarkdown', 'reticulate'), repos='http://cran.rstudio.com/')"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download pt_core_news_lg

RUN quarto install tinytex

RUN /root/.TinyTeX/bin/*/tlmgr update --self \
    && /root/.TinyTeX/bin/*/tlmgr install babel-portuges hyphen-portuguese fancyhdr koma-script