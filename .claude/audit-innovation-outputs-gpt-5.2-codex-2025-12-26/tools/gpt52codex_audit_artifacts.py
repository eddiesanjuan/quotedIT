#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class RouteFinding:
    module: str
    include_prefix: str
    method: str
    path: str
    full_path: str
    file: str
    decorator_line: int
    handler_name: str | None
    handler_line: int | None
    has_request_param: bool | None
    auth_hint: str  # "required" | "optional" | "none" | "unknown"
    rate_limit_hint: str  # "limited" | "unlimited" | "unknown"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _iter_repo_text_files() -> Iterable[Path]:
    skip_dirs = {
        ".git",
        "venv",
        "__pycache__",
        ".playwright-mcp",
        ".pytest_cache",
    }
    skip_files = {
        ".env",
    }
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in files:
            if fname in skip_files:
                continue
            path = Path(root) / fname
            # Ignore obvious binaries.
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
                continue
            yield path


def _load_main_router_prefixes(main_py: Path) -> dict[str, str]:
    """
    Parse `backend/main.py` for:
      app.include_router(<module>.router, prefix="/api/..")
    Returns mapping: module_name -> prefix
    """
    text = _read_text(main_py)
    include_re = re.compile(
        r'app\.include_router\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\.router\s*,\s*prefix\s*=\s*"([^"]+)"',
        re.MULTILINE,
    )
    return {m.group(1): m.group(2) for m in include_re.finditer(text)}


def _extract_route_decorators(text: str) -> list[tuple[int, str, str]]:
    """
    Returns list of (line_number_1based, method, path_literal) for @router.<method>("...")
    Best-effort: supports single-line decorators and simple multi-line decorators.
    """
    lines = text.splitlines()
    out: list[tuple[int, str, str]] = []
    i = 0
    start_re = re.compile(r"^\s*@router\.(get|post|put|delete|patch)\(")
    path_re = re.compile(r"""["']([^"']*)["']""")
    while i < len(lines):
        line = lines[i]
        m = start_re.match(line)
        if not m:
            i += 1
            continue
        method = m.group(1).upper()
        buf = line
        j = i
        # Accumulate up to 10 lines until we see a ")" to close decorator call.
        while ")" not in buf and (j - i) < 10 and (j + 1) < len(lines):
            j += 1
            buf += "\n" + lines[j]
        # First string literal is treated as the path.
        mpath = path_re.search(buf)
        if mpath:
            out.append((i + 1, method, mpath.group(1)))
        i = j + 1
    return out


def _find_next_handler_signature(text: str, start_line_1based: int) -> tuple[str | None, int | None, bool | None]:
    """
    After a decorator, find the next `def` / `async def` line and extract:
      - handler name
      - handler line number (1-based)
      - whether it has a `request` param (best-effort)
    """
    lines = text.splitlines()
    sig_re = re.compile(r"^\s*(async\s+def|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)")
    for idx in range(start_line_1based, min(len(lines), start_line_1based + 50)):
        m = sig_re.match(lines[idx])
        if not m:
            continue
        name = m.group(2)
        sig_tail = m.group(3)
        has_request = "request" in sig_tail
        return name, idx + 1, has_request
    return None, None, None


def _auth_hint_near_handler(text: str, handler_line_1based: int | None) -> str:
    if not handler_line_1based:
        return "unknown"
    lines = text.splitlines()
    window = "\n".join(lines[max(0, handler_line_1based - 5) : min(len(lines), handler_line_1based + 5)])
    if "Depends(get_current_user" in window or "Depends(get_current_contractor" in window:
        return "required"
    if "Depends(get_optional_user" in window or "Depends(get_optional_contractor" in window:
        return "optional"
    return "none"


def _rate_limit_hint_near_decorators(text: str, decorator_line_1based: int) -> str:
    lines = text.splitlines()
    window = "\n".join(lines[max(0, decorator_line_1based - 6) : min(len(lines), decorator_line_1based + 2)])
    if ".limit(" in window:
        return "limited"
    return "unlimited"


def build_route_inventory() -> list[RouteFinding]:
    main_py = REPO_ROOT / "backend" / "main.py"
    prefixes = _load_main_router_prefixes(main_py)
    findings: list[RouteFinding] = []

    for module, include_prefix in sorted(prefixes.items()):
        api_file = REPO_ROOT / "backend" / "api" / f"{module}.py"
        if not api_file.exists():
            # Some routers live in nested modules; skip silently.
            continue
        text = _read_text(api_file)
        for decorator_line, method, path in _extract_route_decorators(text):
            handler_name, handler_line, has_request_param = _find_next_handler_signature(text, decorator_line)
            auth_hint = _auth_hint_near_handler(text, handler_line)
            rate_limit_hint = _rate_limit_hint_near_decorators(text, decorator_line)
            full_path = include_prefix.rstrip("/") + "/" + path.lstrip("/")
            findings.append(
                RouteFinding(
                    module=module,
                    include_prefix=include_prefix,
                    method=method,
                    path=path,
                    full_path=full_path,
                    file=str(api_file.relative_to(REPO_ROOT)),
                    decorator_line=decorator_line,
                    handler_name=handler_name,
                    handler_line=handler_line,
                    has_request_param=has_request_param,
                    auth_hint=auth_hint,
                    rate_limit_hint=rate_limit_hint,
                )
            )

    return findings


def write_route_inventory(findings: list[RouteFinding], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(
        json.dumps([f.__dict__ for f in findings], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    public_unlimited = [
        f for f in findings if f.auth_hint in {"none", "unknown"} and f.rate_limit_hint != "limited"
    ]
    public_total = [f for f in findings if f.auth_hint in {"none", "unknown"}]

    lines: list[str] = []
    lines.append("# API Route Inventory (GPT-5.2-Codex)\n")
    lines.append(f"- Generated from `backend/main.py` + `backend/api/*` at `{REPO_ROOT}`")
    lines.append(f"- Routes discovered: **{len(findings)}**")
    lines.append(f"- Public/unknown-auth routes: **{len(public_total)}**")
    lines.append(f"- Public/unknown-auth + no rate limit: **{len(public_unlimited)}**\n")

    lines.append("## Top Risk Slice (Public + No Rate Limit)\n")
    if not public_unlimited:
        lines.append("- None detected by static heuristics.\n")
    else:
        lines.append("| Method | Full Path | File:Line | Auth Hint | Rate Limit Hint | Handler |")
        lines.append("|---|---|---:|---|---|---|")
        for f in sorted(public_unlimited, key=lambda x: (x.full_path, x.method))[:50]:
            loc = f"{f.file}:{f.decorator_line}"
            handler = f"{f.handler_name or '?'}:{f.handler_line or '?'}"
            lines.append(
                f"| `{f.method}` | `{f.full_path}` | `{loc}` | `{f.auth_hint}` | `{f.rate_limit_hint}` | `{handler}` |"
            )
        if len(public_unlimited) > 50:
            lines.append(f"\n- Truncated to 50 of {len(public_unlimited)} rows.\n")

    lines.append("\n## Full Inventory\n")
    lines.append("| Method | Full Path | File:Line | Auth Hint | Rate Limit Hint | Handler |")
    lines.append("|---|---|---:|---|---|---|")
    for f in sorted(findings, key=lambda x: (x.full_path, x.method)):
        loc = f"{f.file}:{f.decorator_line}"
        handler = f"{f.handler_name or '?'}:{f.handler_line or '?'}"
        lines.append(
            f"| `{f.method}` | `{f.full_path}` | `{loc}` | `{f.auth_hint}` | `{f.rate_limit_hint}` | `{handler}` |"
        )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pip_audit_summary(pip_audit_json: Path, out_md: Path) -> None:
    data = json.loads(_read_text(pip_audit_json))
    deps = data.get("dependencies", [])
    vulns = []
    for dep in deps:
        if not dep.get("vulns"):
            continue
        for v in dep["vulns"]:
            vulns.append(
                {
                    "package": dep.get("name"),
                    "installed": dep.get("version"),
                    "id": v.get("id"),
                    "aliases": v.get("aliases") or [],
                    "fix_versions": v.get("fix_versions") or [],
                }
            )

    vulns_sorted = sorted(vulns, key=lambda x: (x["package"] or "", x["id"] or ""))

    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Dependency Vulnerability Summary (pip-audit) — GPT-5.2-Codex\n")
    lines.append(f"- Source: `{pip_audit_json.relative_to(REPO_ROOT)}`")
    lines.append(f"- Findings: **{len(vulns_sorted)} vulnerabilities**\n")

    lines.append("| Package | Installed | Vulnerability | Fix Versions | Aliases |")
    lines.append("|---|---:|---|---|---|")
    for v in vulns_sorted:
        aliases = ", ".join(v["aliases"]) if v["aliases"] else ""
        fixes = ", ".join(v["fix_versions"]) if v["fix_versions"] else ""
        lines.append(
            f"| `{v['package']}` | `{v['installed']}` | `{v['id']}` | `{fixes}` | {aliases} |"
        )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_secret_fingerprint_scan(out_md: Path) -> None:
    """
    Best-effort secret scan that only reports file + line numbers (no secret values).
    This intentionally avoids printing matching lines to prevent leakage in logs.
    """

    patterns: list[tuple[str, re.Pattern[str]]] = [
        # Stripe keys are strictly alphanumeric after the prefix in practice; keeping this
        # tight prevents false positives from variable names like `sk_test_mode`.
        ("stripe_secret_key", re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}")),
        ("stripe_restricted_key", re.compile(r"rk_(?:live|test)_[A-Za-z0-9]{16,}")),
        ("stripe_publishable_key", re.compile(r"pk_(?:live|test)_[A-Za-z0-9]{16,}")),
        # Resend keys may include `_` or `-`; require length and digits to reduce false positives
        # from variables like `re_compile` / `re_pattern`.
        ("resend_api_key", re.compile(r"re_[A-Za-z0-9_-]{24,}")),
        ("github_pat", re.compile(r"ghp_[A-Za-z0-9]{30,}")),
        ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
    ]

    findings: list[dict[str, Any]] = []
    for path in _iter_repo_text_files():
        try:
            text = _read_text(path)
        except Exception:
            continue
        for label, pat in patterns:
            for m in pat.finditer(text):
                # Extra filter for resend patterns: must contain at least one digit.
                if label == "resend_api_key":
                    s = m.group(0)
                    if not any(ch.isdigit() for ch in s):
                        continue
                # Convert match index -> line number without exposing content.
                line_no = text.count("\n", 0, m.start()) + 1
                findings.append(
                    {
                        "label": label,
                        "file": str(path.relative_to(REPO_ROOT)),
                        "line": line_no,
                    }
                )

    findings_sorted = sorted(findings, key=lambda x: (x["label"], x["file"], x["line"]))

    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Secret Fingerprint Scan (Redacted) — GPT-5.2-Codex\n")
    lines.append("- This scan reports only `file:line` locations (no secret values) to avoid leaking credentials.\n")
    lines.append(f"- Findings: **{len(findings_sorted)}**\n")

    if findings_sorted:
        lines.append("| Type | File:Line |")
        lines.append("|---|---:|")
        for f in findings_sorted:
            lines.append(f"| `{f['label']}` | `{f['file']}:{f['line']}` |")
    else:
        lines.append("- No matches found for the configured patterns.\n")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate GPT-5.2-Codex audit artifacts for Quoted.")
    parser.add_argument("--out-dir", default=str(REPO_ROOT / ".claude" / "audit-innovation-outputs-gpt-5.2-codex-2025-12-26" / "artifacts"))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    route_findings = build_route_inventory()
    write_route_inventory(
        route_findings,
        out_json=out_dir / "api-routes.json",
        out_md=out_dir / "api-routes.md",
    )

    pip_audit_json = REPO_ROOT / ".claude" / "audit-innovation-outputs-gpt-5.2-codex-2025-12-26" / "pip-audit.json"
    if pip_audit_json.exists():
        write_pip_audit_summary(
            pip_audit_json=pip_audit_json,
            out_md=out_dir / "pip-audit-summary.md",
        )

    write_secret_fingerprint_scan(out_md=out_dir / "secret-fingerprint-scan.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
