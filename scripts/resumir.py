import json
import re
import google.generativeai as genai

MODELO = "gemini-2.5-flash"

PROMPT_TEMPLATE = """Você é um assistente especializado em Direito Administrativo e controle externo público.

Analise o seguinte texto do Diário Oficial Eletrônico do TCE/AL (Tribunal de Contas do Estado de Alagoas) e produza um resumo estruturado.

TEXTO DO DIÁRIO:
{texto}

Responda APENAS com um objeto JSON válido, sem texto adicional antes ou depois, no seguinte formato:
{{
  "resumo_geral": "Uma frase resumindo os principais acontecimentos desta edição",
  "normativos": [
    {{
      "tipo": "Resolução|Instrução Normativa|Portaria Normativa|outro",
      "numero": "número/ano do ato",
      "ementa": "ementa oficial se disponível",
      "resumo": "resumo em linguagem clara do que o ato determina"
    }}
  ],
  "decisoes": [
    {{
      "tipo": "Acórdão|Despacho|Deliberação|outro",
      "numero": "número/ano",
      "processo": "número do processo se disponível",
      "interessados": "partes ou órgão envolvido",
      "relator": "nome do relator se disponível",
      "resumo": "resumo da decisão em linguagem clara"
    }}
  ],
  "atos_administrativos": [
    {{
      "tipo": "Nomeação|Exoneração|Designação|Aposentadoria|Portaria|outro",
      "numero": "número do ato se disponível",
      "servidor": "nome do servidor se aplicável",
      "cargo": "cargo envolvido se aplicável",
      "resumo": "resumo do ato"
    }}
  ],
  "outros": [
    {{
      "tipo": "tipo da publicação",
      "resumo": "resumo do conteúdo"
    }}
  ]
}}

Regras:
- Se uma categoria não tiver publicações, use lista vazia []
- Use linguagem clara e objetiva
- Para cada item, extraia as informações mais relevantes para um auditor de controle externo
- Se alguma informação não estiver disponível no texto, omita o campo
"""


def resumir_edicao(texto: str, metadados: dict, api_key: str) -> dict:
    """Send gazette text to Gemini and return structured summary dict."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODELO)

    prompt = PROMPT_TEMPLATE.format(texto=texto)
    resposta = model.generate_content(prompt)

    texto_resposta = resposta.text.strip()

    # Remove markdown code fences if Gemini wrapped the JSON in ```json ... ```
    texto_resposta = re.sub(r"^```(?:json)?\s*", "", texto_resposta)
    texto_resposta = re.sub(r"\s*```$", "", texto_resposta)

    try:
        dados = json.loads(texto_resposta)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini retornou resposta inválida (não é JSON): {e}") from e

    dados["data"] = metadados.get("data")
    dados["data_formatada"] = metadados.get("data_formatada")

    return dados
