"""Check catalog totals against the current summary in project documents."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = ("README.md", "README.fa.md", "AGENTS.md", "llms.txt")


def validate(catalog: list[dict], docs: dict[str, str]) -> list[str]:
    errors = []
    names = set()
    for server in catalog:
        name = server["name"]
        if name in names:
            errors.append(f"{name}: duplicate server name")
        names.add(name)
        if server["tool_count"] != len(server["tools"]):
            errors.append(f"{name}: tool_count does not match tools")

    servers = len(catalog)
    tools = sum(len(server["tools"]) for server in catalog)
    persian = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    expected = {
        "README.md": f'alt="iran-mcp: {servers} MCP servers and {tools} tools',
        "README.fa.md": f'alt="iran-mcp: {str(servers).translate(persian)} سرور MCP و {str(tools).translate(persian)} ابزار',
        "AGENTS.md": f"{servers} MCP servers for Iranian websites, {tools} tools",
        "llms.txt": f"> {servers} MCP servers ({tools} tools)",
    }
    for name, text in expected.items():
        if text not in docs.get(name, ""):
            errors.append(f"{name}: current catalog totals are missing or incorrect")
    return errors


def main() -> None:
    catalog = json.loads((ROOT / "servers.json").read_text(encoding="utf-8"))
    docs = {name: (ROOT / name).read_text(encoding="utf-8") for name in DOCUMENTS}
    errors = validate(catalog, docs)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Catalog totals match {len(DOCUMENTS)} documents")


if __name__ == "__main__":
    main()
