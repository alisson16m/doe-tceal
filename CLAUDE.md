# DOE TCE/AL — Monitor do Diário Oficial

## Visão Geral

Pipeline automatizado que baixa o PDF do Diário Oficial Eletrônico do TCE/AL, extrai texto, resume com Gemini 2.5 Flash e publica HTML no GitHub Pages. O pipeline roda via GitHub Actions todo dia útil às 07h00 BRT, processando a edição do dia anterior.

## Comandos

### Instalar dependências
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Rodar testes
```bash
pytest tests/ -v
```

### Executar pipeline manualmente (requer chave do Gemini)
```bash
GEMINI_API_KEY=sua_chave python -m scripts.main
```

### Regenerar index.html a partir dos JSONs existentes
```bash
python -c "from scripts.gerar_html import regenerar_index; regenerar_index()"
```

## Arquitetura

Pipeline linear em 4 etapas, orquestrado por `scripts/main.py`:

1. `scripts/descobrir_edicao.py` — descobre IDs novos por tentativa sequencial a partir de `dados/estado.json`
2. `scripts/extrair_texto.py` — extrai texto e metadados (data, número da edição) do PDF com pdfplumber
3. `scripts/resumir.py` — envia texto ao Gemini 2.5 Flash, retorna dict estruturado com normativos/decisões/atos/outros
4. `scripts/gerar_html.py` — renderiza templates Jinja2 e salva HTML + JSON em disco

`dados/estado.json` só é atualizado após sucesso completo de todas as etapas.

## Estrutura de Arquivos

| Arquivo/Pasta | Propósito |
|---|---|
| `dados/estado.json` | Último ID de edição processado com sucesso |
| `dados/{id}.json` | Dados estruturados de cada edição (para busca, filtros e estatísticas futuras) |
| `edicoes/{id}.html` | Página HTML de cada edição |
| `index.html` | Índice de todas as edições (raiz do GitHub Pages) |
| `templates/` | Templates Jinja2 — não editar HTML gerado em `edicoes/` diretamente |

## Convenções

- Comentários e logs em português
- Nomes de variáveis e funções em português
- Mensagens de commit em português com prefixo semântico: `feat:`, `fix:`, `chore:`
- Testes com pytest; APIs externas (Gemini, HTTP) sempre mockadas em testes unitários
- Nunca editar manualmente arquivos em `edicoes/` ou `index.html` — são gerados automaticamente

## Configuração

- `GEMINI_API_KEY`: chave da API do Gemini. Em produção, configurada como GitHub Secret. Para testes locais, exportar como variável de ambiente.
- Modelo: `gemini-2.5-flash` (definido em `scripts/resumir.py`)
- Agendamento: cron `0 10 * * 1-5` no workflow `.github/workflows/diario.yml` (07h BRT = 10h UTC)

## Evolução Futura

Os JSONs em `dados/` são o "banco de dados" do sistema. Futuras extensões não requerem refatoração:
- Notificações (e-mail, Telegram): novo step no workflow
- Busca e filtros: JavaScript no frontend consumindo os JSONs
- Estatísticas mensais: script separado que agrega `dados/*.json`
- Alertas por órgão específico: parâmetro no prompt em `scripts/resumir.py`
