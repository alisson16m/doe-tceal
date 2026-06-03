import json
import re
import google.generativeai as genai

MODELO = "gemini-2.5-flash"

PROMPT_TEMPLATE = """Você é um assistente especializado em Direito Administrativo e controle externo público.

Analise o seguinte texto do Diário Oficial Eletrônico do TCE/AL (Tribunal de Contas do Estado de Alagoas) e produza um resumo estruturado.

ESTRUTURA DO DIÁRIO:
O texto é dividido em seções identificadas por cabeçalhos como "GABINETE DO CONSELHEIRO(A) [Nome]", "PRESIDÊNCIA", "MINISTÉRIO PÚBLICO DE CONTAS — [Nª] PROCURADORIA DO MINISTÉRIO PÚBLICO DE CONTAS" e "DIRETORIA [Nome]". Todos os itens dentro de uma seção pertencem ao conselheiro, procurador ou diretor responsável por aquela seção. Para itens do Ministério Público de Contas, o nome do procurador assina ao final do documento.

TEXTO DO DIÁRIO:
{texto}

Responda APENAS com um objeto JSON válido, sem texto adicional antes ou depois, no seguinte formato:
{{
  "resumo_geral": "Resumo em 3 a 5 frases destacando os pontos mais relevantes para um auditor de controle externo: multas aplicadas e seus valores, decisões que identificaram irregularidades, determinações de ressarcimento, processos com impacto financeiro significativo, normativos publicados e qualquer fato de destaque no controle da administração pública.",
  "destaques_auditor": [
    {{
      "topico": "Categoria do destaque — use exatamente um dos valores: Prestação de Contas de Governo | Prestação de Contas de Gestão | Novos Normativos | SIAP | Multas e Sanções | Irregularidades e Ressarcimento | Outro",
      "titulo": "Título curto e direto do que aconteceu (máx. 12 palavras)",
      "resumo": "Explicação em 2 a 4 frases do que o auditor precisa saber: o que foi decidido/publicado, quem é o responsável, qual o impacto prático e se há alguma ação necessária.",
      "processos": ["lista de números de processo relacionados, se houver"]
    }}
  ],
  "normativos": [
    {{
      "tipo": "Resolução|Instrução Normativa|Portaria Normativa|outro",
      "numero": "número/ano do ato",
      "secao": "nome do conselheiro, diretoria ou presidência responsável pela seção",
      "ementa": "ementa oficial se disponível",
      "resumo": "resumo em linguagem clara do que o ato determina"
    }}
  ],
  "decisoes": [
    {{
      "tipo": "Acórdão|Decisão Monocrática|Despacho|Deliberação|outro",
      "numero": "número/ano",
      "processo": "número do processo (ex: TC Nº 4911/2023)",
      "assunto": "assunto do processo conforme consta no cabeçalho da decisão",
      "interessados": "partes ou órgão envolvido",
      "unidade": "unidade ou órgão responsável se disponível",
      "secao": "nome do conselheiro responsável pela seção onde esta decisão foi publicada",
      "relator": "nome do relator se disponível",
      "resumo": "resumo da decisão em linguagem clara"
    }}
  ],
  "atos_administrativos": [
    {{
      "tipo": "Despacho|Portaria|Nomeação|Exoneração|Designação|Aposentadoria|Parecer|outro",
      "numero": "número do ato se disponível",
      "processo": "número do processo se disponível",
      "assunto": "assunto conforme consta no cabeçalho do ato",
      "interessado": "nome do servidor ou entidade interessada",
      "secao": "nome do conselheiro, procurador, diretoria ou presidência responsável pela seção",
      "resumo": "resumo do ato em linguagem clara"
    }}
  ],
  "outros": [
    {{
      "tipo": "tipo da publicação",
      "secao": "seção onde foi publicado",
      "resumo": "resumo do conteúdo"
    }}
  ]
}}

Regras IMPORTANTES:
- SEÇÃO: para cada item, identifique em qual seção do diário ele foi publicado e registre no campo "secao". Use o nome completo do conselheiro(a) (ex: "Conselheira Rosa Maria Ribeiro de Albuquerque"), ou "Presidência", ou "2ª Procuradoria do Ministério Público de Contas", ou "Diretoria-Geral", etc.
- NORMATIVOS: inclua APENAS atos que são PUBLICADOS nesta edição (novas resoluções, portarias normativas, instruções normativas). NÃO inclua leis ou normas citadas apenas como fundamento legal dentro de outros documentos.
- DECISÕES: inclua acórdãos, decisões monocrátivas e despachos decisórios. Extraia "assunto" da tabela de cabeçalho quando disponível.
- ATOS ADMINISTRATIVOS: inclua despachos de encaminhamento, pareceres, portarias e demais atos. Para cada ato com tabela de cabeçalho, extraia processo, assunto e interessado.
- RESUMO GERAL: destaque especialmente multas e valores financeiros, irregularidades identificadas, determinações de ressarcimento e processos relevantes para o controle externo.
- DESTAQUES DO AUDITOR: Analise criticamente a edição do ponto de vista de um Auditor de Controle Externo do TCE/AL. Inclua APENAS itens genuinamente relevantes — não crie destaques genéricos nem repita o resumo_geral. Priorize:
  * Prestação de Contas de Governo: decisões sobre contas de prefeitos, governadores ou chefes do Executivo municipal/estadual
  * Prestação de Contas de Gestão: contas de gestores, secretários, diretores, responsáveis por recursos públicos
  * Novos Normativos: resoluções, instruções normativas, portarias normativas publicadas nesta edição com impacto direto no trabalho de auditoria
  * SIAP (Sistema Integrado de Auditoria Pública): qualquer menção, determinação, prazo ou instrução relacionada ao SIAP
  * Multas e Sanções: imputação de débito, multa com valor, inabilitação para cargo público
  * Irregularidades e Ressarcimento: determinação de ressarcimento ao erário, identificação de irregularidade grave, medida cautelar
  * Se nenhuma publicação se enquadrar em algum tópico, NÃO inclua esse tópico. Se nada for relevante para o auditor, use lista vazia [].
- Se uma categoria não tiver publicações, use lista vazia []
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
