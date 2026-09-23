"""Export a temporary CodeGraph index plus AST-checked Python dependencies.

Run: uv run python docs/codegraph/export_graph.py /path/to/indexed-source-copy
The copy must contain the application's source files and .codegraph/codegraph.db.
This script does not import or execute application code.
"""

import argparse
import ast
import hashlib
import json
import shutil
import sqlite3
import tomllib
from collections import Counter, defaultdict
from pathlib import Path


def definitions(tree):
    result = []

    def visit(node, scope=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{scope}.{child.name}" if scope else child.name
                item = {
                    "name": name,
                    "line": child.lineno,
                    "end_line": child.end_lineno,
                    "kind": "class" if isinstance(child, ast.ClassDef) else "function",
                }
                if isinstance(child, ast.ClassDef):
                    item["bases"] = [ast.unparse(base) for base in child.bases]
                result.append(item)
                visit(child, name)
            else:
                visit(child, scope)

    visit(tree)
    return result


def python_imports(path, tree, modules):
    result = []
    package = path.removesuffix(".py").split("/")[:-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports = [(alias.name, alias.name, alias.asname) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            prefix = package[: len(package) - node.level + 1] if node.level else []
            module = ".".join(prefix + ([node.module] if node.module else []))
            imports = [(module, alias.name, alias.asname) for alias in node.names]
        else:
            continue
        for module, name, alias in imports:
            candidate = f"{module}.{name}"
            target = modules.get(candidate) or modules.get(module)
            # Standalone scripts can import a sibling after modifying sys.path.
            if not target:
                sibling = str(Path(path).parent / (module.replace(".", "/") + ".py"))
                if sibling in modules.values():
                    target = sibling
            result.append(
                {"source": path, "module": module, "name": name, "alias": alias, "line": node.lineno, "target": target}
            )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    parser.add_argument("--prepare", action="store_true", help="Copy current source to a new snapshot directory")
    args = parser.parse_args()
    if args.prepare:
        repository = Path(__file__).resolve().parents[2]
        args.snapshot.mkdir(parents=True, exist_ok=False)
        paths = [repository / "pyproject.toml", repository / "uv.lock"]
        for folder in ("aveli", "examples", "scripts", "tests", "deploy", ".github"):
            paths.extend(
                p
                for p in (repository / folder).rglob("*")
                if p.is_file()
                and (p.suffix in {".py", ".js", ".html", ".css", ".toml", ".yml"} or p.name == "Dockerfile")
            )
        for path in paths:
            target = args.snapshot / path.relative_to(repository)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        print(f"Copied {len(paths)} source files to {args.snapshot}; run codegraph init there next.")
        return
    db = args.snapshot / ".codegraph/codegraph.db"
    with sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        raw = {
            table: [dict(row) for row in connection.execute(f"SELECT * FROM {table}")]
            for table in ("files", "nodes", "edges", "unresolved_refs")
        }
    for row in raw["files"]:
        content = (args.snapshot / row["path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != row["content_hash"]:
            raise ValueError(f"Index is stale: {row['path']}")
    for table in raw.values():
        for row in table:
            for key in ("updated_at", "indexed_at", "modified_at"):
                row.pop(key, None)
    files = sorted(
        p.relative_to(args.snapshot).as_posix()
        for p in args.snapshot.rglob("*")
        if p.is_file()
        and ".codegraph" not in p.parts
        and (p.suffix in {".py", ".js", ".html", ".css", ".toml", ".yml"} or p.name == "Dockerfile")
    )
    contents = {path: (args.snapshot / path).read_text() for path in files}
    trees = {path: ast.parse(text) for path, text in contents.items() if path.endswith(".py")}
    modules = {path.removesuffix(".py").replace("/", ".").removesuffix(".__init__"): path for path in trees}
    imports = [item for path, tree in trees.items() for item in python_imports(path, tree, modules)]
    decls = {path: definitions(tree) for path, tree in trees.items()}
    adjacency = {path: set() for path in trees}
    for item in imports:
        if item["target"]:
            adjacency[item["source"]].add(item["target"])
    reverse = defaultdict(set)
    for path, targets in adjacency.items():
        for target in targets:
            reverse[target].add(path)
    reach = {path: set(targets) for path, targets in adjacency.items()}
    for path in reach:
        todo = list(reach[path])
        while todo:
            for target in adjacency[todo.pop()]:
                if target not in reach[path]:
                    reach[path].add(target)
                    todo.append(target)
    cycles = sorted({tuple(sorted({p} | {q for q in reach[p] if p in reach[q]})) for p in reach if p in reach[p]})
    by_id = {node["id"]: node for node in raw["nodes"]}
    for edge in raw["edges"]:
        if edge["source"] not in by_id or edge["target"] not in by_id:
            raise ValueError("Dangling graph edge")
    indexed_defs = {
        (n["file_path"], n["start_line"]) for n in raw["nodes"] if n["kind"] in {"function", "method", "class"}
    }
    missing = [{"file": path, **d} for path, ds in decls.items() for d in ds if (path, d["line"]) not in indexed_defs]
    if missing:
        raise ValueError(f"Python definitions missing from CodeGraph: {missing}")
    stats = {
        "source_files": len(files),
        "indexed_files": len(raw["files"]),
        "python_definitions": sum(map(len, decls.values())),
        "python_javascript_lines": sum(
            len(text.splitlines()) for p, text in contents.items() if p.endswith((".py", ".js"))
        ),
        "nodes": dict(sorted(Counter(n["kind"] for n in raw["nodes"]).items())),
        "edges": dict(sorted(Counter(e["kind"] for e in raw["edges"]).items())),
        "unresolved_references": len(raw["unresolved_refs"]),
        "internal_import_file_edges": sum(map(len, adjacency.values())),
        "python_import_cycles": cycles,
    }
    lock_bytes = (args.snapshot / "uv.lock").read_bytes()
    locked_packages = tomllib.loads(lock_bytes.decode())["package"]
    stats["locked_packages"] = len(locked_packages)
    graph = {
        "lock_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "locked_packages": locked_packages,
        "method": "CodeGraph raw static graph; Python imports/declarations checked with ast. "
        "Raw call targets are hypotheses, not a verified execution trace.",
        "stats": stats,
        "source_sha256": {p: hashlib.sha256((args.snapshot / p).read_bytes()).hexdigest() for p in files},
        "python_imports": imports,
        "python_declarations": decls,
        **raw,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "graph.json").write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Generated source and import inventory",
        "",
        "Generated by `export_graph.py`.",
        "",
        "Imports include function-local/lazy imports and tests. Arrows point from consumer to dependency.",
        "A direct importer of the package facade is not necessarily a caller of every exported symbol.",
        "",
        "```json",
        json.dumps(stats, indent=2),
        "```",
        "",
    ]
    for path in files:
        lines += [f"## `{path}`", "", f"Lines: {len(contents[path].splitlines())}.", ""]
        if path in trees:
            local = sorted(adjacency[path])
            external = sorted({i["module"] for i in imports if i["source"] == path and not i["target"]})
            users = sorted(reverse[path])
            lines += [
                "- Internal imports: " + (", ".join(f"`{s}`" for s in local) or "none"),
                "- External/standard-library imports: " + (", ".join(f"`{s}`" for s in external) or "none"),
                "- Direct importers: " + (", ".join(f"`{s}`" for s in users) or "none"),
                "",
            ]
            lines += ["| Definition | Lines | Bases |", "|---|---:|---|"]
            for d in decls[path]:
                bases = ", ".join(d.get("bases", [])) or "—"
                lines.append(f"| `{d['name']}` ({d['kind']}) | {d['line']}–{d['end_line']} | {bases} |")
        elif path.endswith(".js"):
            lines += [
                f"- `{n['qualified_name']}`: {n['start_line']}–{n['end_line']}"
                for n in raw["nodes"]
                if n["file_path"] == path and n["kind"] == "function"
            ]
            if path.endswith("snapshot.js"):
                lines += ["- CodeGraph does not expose the IIFE's nested helpers; see the main report."]
        else:
            lines += ["Non-Python/JavaScript asset; runtime/configuration links are in the main report."]
        lines += [""]
    (args.output / "inventory.md").write_text("\n".join(lines))
    ids = {path: f"f{i}" for i, path in enumerate(trees)}
    diagram = ["flowchart LR"] + [f'  {ids[p]}["{p}"]' for p in trees]
    diagram += [f"  {ids[p]} --> {ids[t]}" for p in trees for t in sorted(adjacency[p])]
    (args.output / "imports.mmd").write_text("\n".join(diagram) + "\n")
    calls = [
        "# Raw CodeGraph callable relationships",
        "",
        "**Not a verified runtime trace.** Dynamic dispatch can be missing or misresolved.",
        "For example, worker.execute's runner.run is misresolved to Agent.run.",
        "Use the main report for verified chains; graph.json retains all edge kinds and unresolved references.",
        "",
    ]
    for path in files:
        symbols = [n for n in raw["nodes"] if n["file_path"] == path and n["kind"] in {"function", "method", "class"}]
        if not symbols:
            continue
        calls += [f"## `{path}`", ""]
        for n in symbols:
            targets = sorted(
                {
                    f"{by_id[e['target']]['file_path']}:{by_id[e['target']]['start_line']} "
                    f"{by_id[e['target']]['qualified_name']} ({e['kind']})"
                    for e in raw["edges"]
                    if e["source"] == n["id"] and e["kind"] in {"calls", "instantiates", "extends"}
                }
            )
            calls += [f"### `{n['qualified_name']}` · line {n['start_line']}", ""]
            calls += [f"- `{t}`" for t in targets] or ["No resolved outgoing call/type edge."]
            calls += [""]
    (args.output / "calls.md").write_text("\n".join(calls))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
