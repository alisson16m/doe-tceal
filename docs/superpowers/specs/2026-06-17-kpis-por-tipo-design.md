# Design: KPIs por tipo de documento no índice

**Data:** 2026-06-17

## Objetivo

Substituir os badges genéricos (normativos, decisões, atos) nos cards do `index.html` por badges específicos por tipo de documento, permitindo visualizar de um relance quantos acórdãos, decisões monocráticas, pareceres prévios, pareceres ministeriais e outros foram publicados em cada edição do Diário Oficial.

## Arquitetura

### 1. `scripts/gerar_html.py` — `regenerar_index()`

Ao montar o dict de cada edição, substituir os campos `normativos_count`, `decisoes_count` e `atos_count` pelos seguintes campos calculados:

| Campo | Fonte | Critério |
|---|---|---|
| `normativos_count` | `normativos[]` | `len(normativos)` (mantido) |
| `acordaos_count` | `decisoes[]` | `tipo` contém `"Acórdão"` |
| `decisoes_monocraticas_count` | `decisoes[]` | `tipo` == `"Decisão Monocrática"` |
| `pareceres_previos_count` | `decisoes[]` | `tipo` contém `"Parecer Prévio"` |
| `pareceres_count` | `atos_administrativos[]` | `tipo` contém `"Parecer"` |
| `outros_count` | `decisoes[]` + `atos_administrativos[]` + `outros[]` | tudo que não se encaixa nas categorias acima |

**Regra para `outros_count`:** soma de:
- Items em `decisoes` cujo `tipo` não contém "Acórdão", "Decisão Monocrática" nem "Parecer Prévio"
- Items em `atos_administrativos` cujo `tipo` não contém "Parecer" (ex: Despacho, Extrato de Termo Aditivo, Portaria, Edital de Citação, Edital de Notificação)
- Todos os items em `outros[]`

### 2. `templates/index.html` — seção de badges

Substituir os 3 `{% if ... %}` de badges atuais por 6 condicionais, um por categoria. Cada badge só renderiza se a contagem for > 0.

**Badges e cores:**

| Badge | Texto | Cor de fundo | Cor de texto |
|---|---|---|---|
| Normativos | `N normativo(s)` | `#dde8f5` | `#1a3a5c` |
| Acórdãos | `N acórdão(s)` | `#d4edda` | `#155724` |
| Dec. Monocráticas | `N dec. monocrática(s)` | `#dff0df` | `#2d6a2d` |
| Parecer Prévio | `N parecer(es) prévio(s)` | `#e8d5f5` | `#5a2d82` |
| Pareceres | `N parecer(es)` | `#faebd7` | `#7a4000` |
| Outros | `N outro(s)` | `#e8e8e8` | `#555` |

### 3. Compatibilidade com testes

`tests/test_gerar_html.py` usa os campos antigos `normativos_count`, `decisoes_count` e `atos_count`. Os testes precisam ser atualizados para os novos campos.

## O que não muda

- Estrutura dos JSONs em `dados/` — nenhuma alteração
- Template `templates/edicao.html` — nenhuma alteração
- Pipeline `scripts/main.py` — nenhuma alteração
- Lógica de busca por texto e por data no `index.html`

## Escopo

Apenas `scripts/gerar_html.py`, `templates/index.html` e `tests/test_gerar_html.py`.
