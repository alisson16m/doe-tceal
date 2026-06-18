# Dashboard de Decisões Diárias

## Objetivo

Adicionar um gráfico de linhas na página inicial (`index.html`) mostrando a evolução diária da quantidade de decisões por tipo: Acórdãos, Decisões Monocráticas e Pareceres Prévios.

## Decisões de design

- **Dados inline via Jinja2**: o Python monta os dados do gráfico e injeta como JSON no template. Zero requisições extras, funciona offline.
- **Chart.js v4 via CDN**: biblioteca leve, sem build necessário.
- **Posição**: dashboard acima da lista de cards, visível logo ao abrir a página.
- **3 séries**: Acórdãos, Dec. Monocráticas, Pareceres Prévios — cores alinhadas aos badges existentes.

## Alterações

### `scripts/gerar_html.py` — função `regenerar_index()`

Montar uma lista `dados_grafico` com dicts ordenados cronologicamente (mais antigo → mais recente):

```python
{
    "data": "2026-06-17",
    "data_formatada": "17/06/2026",
    "acordaos": 5,
    "monocraticas": 3,
    "previos": 1
}
```

Esses dados já são calculados no loop existente (`acordaos`, `monocraticas`, `previos`). Basta acumulá-los numa lista separada e passá-la ao template.

### `templates/index.html`

1. **CDN**: adicionar `<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>` no `<head>`.

2. **Seção dashboard**: inserir entre a `div.barra-busca` e o `<main>`:
   ```html
   <section class="dashboard">
     <h2>Decisões por Edição</h2>
     <canvas id="grafico-decisoes"></canvas>
   </section>
   ```
   Envolvido em `{% if edicoes %}`.

3. **CSS do dashboard**:
   - `max-width: 900px` (igual ao `main`)
   - `margin: 1.5rem auto 0`
   - `background: #fff`, `border-radius: 8px`, `border: 1px solid #ddd`
   - `padding: 1.25rem`

4. **JavaScript**: no bloco `<script>` existente, ler `{{ dados_grafico | tojson }}` e criar o gráfico:
   - Eixo X: datas formatadas
   - Série "Acórdãos": cor `#155724` (verde badge-acordaos)
   - Série "Dec. Monocráticas": cor `#2d6a2d` (verde badge-monocraticas)
   - Série "Pareceres Prévios": cor `#5a2d82` (roxo badge-previos)
   - `responsive: true`, `maintainAspectRatio: false` com altura fixa de ~300px

### Testes

- Testar que `regenerar_index()` inclui `dados_grafico` no render (mock do template).
- Testar que a lista `dados_grafico` está ordenada cronologicamente.
- Testar que as contagens batem com os dados dos JSONs.
