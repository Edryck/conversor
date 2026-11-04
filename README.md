# Conversor para Markdown

CLI em Python que converte PDFs e outros formatos de documento para Markdown.

| Formato | Biblioteca | Recursos |
| --- | --- | --- |
| PDF | [Docling](https://github.com/docling-project/docling) | Ordem de leitura em colunas duplas, tabelas e OCR |
| Demais (DOCX, PPTX, XLSX etc.) | [MarkItDown](https://github.com/microsoft/markitdown) | Conversão direta para Markdown |

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

Salvar o resultado em um arquivo:

```bash
python converter.py <arquivo-de-entrada> -o <arquivo-de-saida>.md
```

Sem a opção `-o`, o Markdown é impresso no terminal:

```bash
python converter.py <arquivo-de-entrada>
```

| Argumento | Obrigatório | Descrição |
| --- | --- | --- |
| `input` | Sim | Caminho do arquivo de entrada |
| `-o`, `--output` | Não | Caminho do arquivo Markdown de saída |

## Converter vários arquivos

Todos os PDFs da pasta atual:

```bash
for file in *.pdf; do python converter.py "$file" -o "${file%.pdf}.md"; done
```

Arquivos numerados em sequência, como `aula-1.pdf` até `aula-5.pdf`:

```bash
for i in {1..5}; do python converter.py "aula-$i.pdf" -o "aula-$i.md"; done
```
