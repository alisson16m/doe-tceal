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
        edicoes.append({
            "id": d["id"],
            "data": d.get("data", ""),
            "data_formatada": d.get("data_formatada", ""),
            "resumo_geral": d.get("resumo_geral", ""),
            "normativos_count": len(d.get("normativos", [])),
            "decisoes_count": len(d.get("decisoes", [])),
            "atos_count": len(d.get("atos_administrativos", [])),
        })

    template = _env().get_template("index.html")
    INDEX_PATH.write_text(template.render(edicoes=edicoes), encoding="utf-8")
