# Conversor para Markdown

CLI em Python que converte PDFs e outros formatos de documento para Markdown.

| Formato | Biblioteca | Recursos |
| --- | --- | --- |
| PDF | [Docling](https://github.com/docling-project/docling) | Ordem de leitura em colunas duplas, tabelas, OCR opcional, imagens, fórmulas e código |
| Demais (DOCX, PPTX, XLSX etc.) | [MarkItDown](https://github.com/microsoft/markitdown) | Conversão direta para Markdown |

## Instalação

Instale primeiro o PyTorch em versão CPU, para evitar o download das versões com CUDA:

```bash
python -m venv .venv
source .venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Uso

Converter um arquivo. Sem `-o`, o resultado é gravado ao lado da entrada (`relatorio.pdf` gera `relatorio.md`):

```bash
python converter.py <arquivo-de-entrada>
```

Escolher o arquivo de saída:

```bash
python converter.py <arquivo-de-entrada> -o <arquivo-de-saida>.md
```

Imprimir no terminal:

```bash
python converter.py <arquivo-de-entrada> --stdout
```

| Argumento | Obrigatório | Descrição |
| --- | --- | --- |
| `inputs` | Sim | Arquivos, pastas (sem recursão) ou padrões glob de entrada |
| `-o`, `--output` | Não | Arquivo de saída (entrada única que é arquivo) ou pasta de saída (pasta, glob ou várias entradas) |
| `--stdout` | Não | Imprime o resultado na saída padrão. Não combina com várias entradas, `-o` ou `--images` |
| `--force` | Não | Reconverte mesmo se a saída estiver atualizada |
| `--ocr` | Não | Ativa OCR para PDFs escaneados |
| `--ocr-lang` | Não | Idiomas do OCR separados por vírgula (ex.: `pt,en`) |
| `--images` | Não | Extrai as imagens do PDF para a pasta `<nome>_images` ao lado da saída |
| `--formulas` | Não | Enriquece fórmulas. Baixa um modelo extra na primeira execução |
| `--code` | Não | Enriquece blocos de código. Baixa um modelo extra na primeira execução |
| `--format` | Não | `markdown` (padrão), `json` ou `html` |

Observações:

- `--format json` e `--format html` funcionam apenas para PDFs. Em outros formatos o arquivo falha, pois o MarkItDown só gera Markdown.
- `--ocr`, `--ocr-lang`, `--images`, `--formulas` e `--code` não têm efeito em arquivos que não são PDF.
- `--ocr-lang` depende do motor de OCR e não foi validado em escaneamentos reais.
- Saídas com data igual ou mais recente que a entrada são puladas. Use `--force` para refazer.
- Códigos de saída: `0` sem falhas, `1` com alguma falha ou sem entradas, `2` erro de uso.

## Mudanças de comportamento

- Sem `-o`, a saída não vai mais para o terminal. Ela é gravada em arquivo ao lado da entrada. Use `--stdout` para o comportamento antigo.
- O OCR agora vem desligado por padrão. Um PDF sem texto extraído gera um aviso sugerindo `--ocr`.

## Converter vários arquivos

Todos os arquivos suportados da pasta atual:

```bash
python converter.py ./
```

Uma pasta, gravando o resultado em outra:

```bash
python converter.py pasta/ -o saida/
```

Arquivos numerados em sequência, como `aula-1.pdf` até `aula-5.pdf`:

```bash
python converter.py aula-*.pdf -o saida/
```

Um erro em um arquivo não interrompe os demais. O resumo final lista as falhas.

## Testes

Testes unitários, com conversor falso e sem carregar modelos:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Testes de integração, com Docling e MarkItDown reais (mais lentos):

```bash
python -m pytest -m integration --override-ini addopts=
```
