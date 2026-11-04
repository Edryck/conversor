# Converter PDF para MD

Segue a sequência de comandos para executar:

Criando o ambiente virtual Python e baixando as bibliotecas:
```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requitements.txt
```

Convertendo um arquivo:
```bash
python converter.py <nome-arquivo>.pdf -o <nome-arquivo>.md
```

Convertendo vários arquivos de uma vez:
```bash
for i in {<primeiro-numero>..<ultimo-numero>}; do python converter.py "<nome-arquivo>$i.pdf" -o "<nome-arquivo>$i.md"; done
```

> OBS.: Para vários arquivos, o exemplo que mostrei é para quando são vários arquivos com nome igual, diferenciando só o número que tem no final, exemplo:
    Arquivos: aula-1.pdf, aula-2.pdf, ..., aula-5.pdf. No código, ficaria assim:
```bash
for i in {1..5}; do python converter.py "aula-$i.pdf" -o "aula-$i.md"; done
```
