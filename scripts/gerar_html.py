import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path("templates")
EDICOES_DIR = Path("edicoes")
DADOS_DIR = Path("dados")
INDEX_PATH = Path("index.html")


def _env() -> Environment:
    return Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)


def salvar_edicao(dados: dict) -> None:
    """Write edition HTML and JSON to disk, then rebuild index."""
    EDICOES_DIR.mkdir(exist_ok=True)
    DADOS_DIR.mkdir(exist_ok=True)

    dados["url_pdf"] = f"https://doe.tceal.tc.br/api/api/editions/viewPdf/{dados['id']}"

    json_path = DADOS_DIR / f"{dados['id']}.json"
    json_path.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")

    template = _env().get_template("edicao.html")
    html = template.render(**dados)
    (EDICOES_DIR / f"{dados['id']}.html").write_text(html, encoding="utf-8")

    regenerar_index()


def regenerar_index() -> None:
    """Rebuild index.html from all JSON files in dados/."""
    edicoes = []
    for json_file in sorted(DADOS_DIR.glob("*.json"), reverse=True):
        if json_file.name == "estado.json":
            continue
        d = json.loads(json_file.read_text(encoding="utf-8"))

        decisoes = d.get("decisoes", [])
        atos = d.get("atos_administrativos", [])
        outros = d.get("outros", [])

        acordaos = sum(1 for x in decisoes if "Acórdão" in x.get("tipo", ""))
        monocraticas = sum(1 for x in decisoes if x.get("tipo") == "Decisão Monocrática")
        previos = sum(1 for x in decisoes if "Parecer Prévio" in x.get("tipo", ""))
        pareceres = sum(1 for x in atos if "Parecer" in x.get("tipo", ""))

        outros_decisoes = sum(
            1 for x in decisoes
            if "Acórdão" not in x.get("tipo", "")
            and x.get("tipo") != "Decisão Monocrática"
            and "Parecer Prévio" not in x.get("tipo", "")
        )
        outros_atos = sum(1 for x in atos if "Parecer" not in x.get("tipo", ""))

        edicoes.append({
            "id": d["id"],
            "data": d.get("data", ""),
            "data_formatada": d.get("data_formatada", ""),
            "resumo_geral": d.get("resumo_geral", ""),
            "normativos_count": len(d.get("normativos", [])),
            "acordaos_count": acordaos,
            "decisoes_monocraticas_count": monocraticas,
            "pareceres_previos_count": previos,
            "pareceres_count": pareceres,
            "outros_count": outros_decisoes + outros_atos + len(outros),
        })

    dados_grafico = sorted(
        [
            {
                "data": ed["data"],
                "data_formatada": ed["data_formatada"],
                "acordaos": ed["acordaos_count"],
                "monocraticas": ed["decisoes_monocraticas_count"],
                "previos": ed["pareceres_previos_count"],
            }
            for ed in edicoes
        ],
        key=lambda x: x["data"],
    )

    template = _env().get_template("index.html")
    INDEX_PATH.write_text(
        template.render(edicoes=edicoes, dados_grafico=dados_grafico),
        encoding="utf-8",
    )
