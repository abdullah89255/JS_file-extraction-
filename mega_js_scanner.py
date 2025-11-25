#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MEGA JS SCANNER – Multi-Mode JavaScript Security Scanner
Modes:
  --mode big
  --mode deep
  --mode professional
  --mode dom
  --mode gau
"""

import os
import re
import sys
import json
import argparse
import subprocess
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime

# Third-party required (auto-installed)
try:
    from tqdm import tqdm
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
except ImportError:
    class Fore:
        CYAN = RED = GREEN = YELLOW = ""
    class Style:
        RESET_ALL = ""
    print("[!] Missing colorama/tqdm. Install with: pip3 install colorama tqdm")


# ============================================================
#  🔧 PRINTING HELPERS
# ============================================================

def info(msg):
    print(Fore.CYAN + "[INFO] " + Style.RESET_ALL + msg)

def success(msg):
    print(Fore.GREEN + "[SUCCESS] " + Style.RESET_ALL + msg)

def warn(msg):
    print(Fore.YELLOW + "[WARN] " + Style.RESET_ALL + msg)

def error(msg):
    print(Fore.RED + "[ERROR] " + Style.RESET_ALL + msg)


# ============================================================
#  📁 DIRECTORY STRUCTURE (Professional Pentest Layout)
# ============================================================

DIRS = {
    "base": "results",
    "recon": "results/recon",
    "recon_gau": "results/recon/gau",
    "recon_js": "results/recon/js",

    "analysis": "results/analysis",
    "analysis_ast": "results/analysis/ast",
    "analysis_dom": "results/analysis/dom",
    "analysis_deep": "results/analysis/deep",

    "findings": "results/findings",
    "findings_secrets": "results/findings/secrets",
    "findings_vulns": "results/findings/vulns",
    "findings_xss": "results/findings/xss",

    "browser": "results/browser-tests",
    "reports": "results/reports",
    "logs": "results/logs",
    "merges": "results/merges",
}


def ensure_directories():
    """Create the full directory structure."""
    for key, path in DIRS.items():
        os.makedirs(path, exist_ok=True)
    success("Directory structure initialized.")


# ============================================================
#  🌐 ASYNC DOWNLOADER FOR JS FILES
# ============================================================

async def download_js_file(session, url, out_path):
    """Download a JS file and save it."""
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                text = await resp.text()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(text, encoding="utf-8", errors="ignore")
                return True
    except Exception:
        return False
    return False


async def download_js_bulk(urls, output_dir):
    """Download multiple JS URLs asynchronously."""
    success("Starting async JS download ...")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            filename = url.split("/")[-1]
            if not filename.endswith(".js"):
                filename += ".js"
            out_path = Path(output_dir) / filename
            tasks.append(download_js_file(session, url, out_path))

        results = await asyncio.gather(*tasks)
        success(f"Downloaded {sum(results)} / {len(urls)} JS files.")


# ============================================================
#  🔍 BASIC SECRET REGEX ENGINE
# ============================================================

SECRET_PATTERNS = [
    r"api[_\-]?key\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})",
    r"secret\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})",
    r"token\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})",
    r"auth\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{8,})",
    r"bearer\s+([A-Za-z0-9_\-]{10,})",
    r"password\s*[:=]\s*[\"']?(.+)",
    r"pwd\s*[:=]\s*[\"']?(.+)",
    r"access[_\-]?token\s*[:=]\s*[\"']?(.+)",
]


def find_secrets_in_js(js_content):
    """Return all secret-like matches from JavaScript."""
    findings = []
    for pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, js_content, flags=re.IGNORECASE)
        for match in matches:
            findings.append((pattern, match))
    return findings


def save_secrets_to_file(file_path, secrets):
    """Save extracted secrets to the findings folder."""
    out = Path(DIRS["findings_secrets"]) / f"{Path(file_path).name}.secrets.txt"
    with open(out, "w") as f:
        for pattern, match in secrets:
            f.write(f"[PATTERN] {pattern}\n[MATCH] {match}\n\n")
    success(f"Secrets saved: {out}")


# ============================================================
#  📚 JS FILE COLLECTOR
# ============================================================

def collect_js_files(dirs):
    """Return list of all JS files inside multiple directories."""
    files = []
    for d in dirs:
        d = Path(d)
        if d.exists():
            for fp in d.rglob("*.js"):
                files.append(str(fp))
    return files


# ============================================================
#  🧰 RUNNING GAU WRAPPER (Mode: gau)
# ============================================================

def run_gau(domain, output_file):
    """Run GAU externally and save results."""
    try:
        cmd = ["gau", "--threads", "50", domain]
        with open(output_file, "w") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL)
        success(f"GAU results saved to {output_file}")
    except FileNotFoundError:
        error("GAU not installed. Install with: go install github.com/lc/gau/v2/cmd/gau@latest")


# ============================================================
#  🧭 ARGUMENT PARSER
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description="MEGA JavaScript Security Scanner (5 modes)",
        epilog="Modes: big, deep, professional, dom, gau"
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["big", "deep", "professional", "dom", "gau"],
        help="Select scanner mode"
    )

    parser.add_argument(
        "--target",
        required=False,
        help="Domain or directory depending on mode"
    )

    parser.add_argument(
        "--jsdir",
        required=False,
        help="Directory of JS files to analyze"
    )

    parser.add_argument(
        "--burp",
        required=False,
        help="Path to BurpSuite Proxy History JSON"
    )

    parser.add_argument(
        "--threads",
        default=50,
        type=int,
        help="Threads / concurrency setting"
    )

    return parser


# ============================================================
#  BIG MODE – FAST SECRETS + ENDPOINT DISCOVERY
# ============================================================

URL_REGEX = r"(https?:\/\/[^\s\"\'<>]+)"


def extract_endpoints(js_code):
    """Extract URLs, endpoints, API paths."""
    return re.findall(URL_REGEX, js_code)


def run_big_mode(args):
    info("Running BIG MODE (fast recon)...")

    if not args.jsdir:
        error("--jsdir required for BIG mode")
        return

    js_files = collect_js_files([args.jsdir])
    info(f"Found {len(js_files)} JS files.")

    for fp in js_files:
        try:
            js_code = Path(fp).read_text(errors="ignore")
        except:
            continue

        # Secret detection
        secrets = find_secrets_in_js(js_code)
        if secrets:
            save_secrets_to_file(fp, secrets)

        # Endpoint extraction
        endpoints = extract_endpoints(js_code)
        if endpoints:
            out = Path(DIRS["findings_vulns"]) / f"{Path(fp).name}.endpoints.txt"
            out.write_text("\n".join(endpoints))
            success(f"Endpoints saved: {out}")

    success("BIG MODE completed.")


# ============================================================
#  DEEP MODE – AST-LEVEL STATIC ANALYSIS
# ============================================================

try:
    import esprima
    ESPRIMA_AVAILABLE = True
except ImportError:
    ESPRIMA_AVAILABLE = False
    warn("esprima not installed. Install with: pip3 install esprima")

DANGEROUS_SINKS = [
    "eval",
    "setTimeout",
    "setInterval",
    "Function",
    "document.write",
    "document.writeln",
    "innerHTML",
    "outerHTML",
    "insertAdjacentHTML",
    "location.assign",
    "location.replace"
]


def ast_find_dangerous_calls(tree):
    """Return list of dangerous JS function calls."""
    findings = []

    def visit_node(node):
        if not hasattr(node, 'type'):
            return
        
        # CallExpression: eval(), setTimeout()
        if node.type == "CallExpression":
            callee = getattr(node.callee, "name", None)
            if callee in DANGEROUS_SINKS:
                line = getattr(node.loc.start, 'line', 0) if hasattr(node, 'loc') else 0
                findings.append(("CallExpression", callee, line))

        # AssignmentExpression: x.innerHTML = ...
        if node.type == "AssignmentExpression":
            try:
                prop = node.left.property.name
                if prop in ["innerHTML", "outerHTML"]:
                    line = getattr(node.loc.start, 'line', 0) if hasattr(node, 'loc') else 0
                    findings.append(("AssignmentExpression", prop, line))
            except:
                pass

        # Recursively visit children
        for key, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    visit_node(item)
            elif hasattr(value, 'type'):
                visit_node(value)

    visit_node(tree)
    return findings


def run_deep_mode(args):
    info("Running DEEP MODE (AST static analysis)...")

    if not ESPRIMA_AVAILABLE:
        error("esprima not installed. Cannot run DEEP mode.")
        return

    if not args.jsdir:
        error("--jsdir required for DEEP mode")
        return

    js_files = collect_js_files([args.jsdir])

    for fp in js_files:
        code = Path(fp).read_text(errors="ignore")

        try:
            tree = esprima.parseScript(code, loc=True)
        except Exception as e:
            warn(f"AST parse failed for {fp}: {e}")
            continue

        findings = ast_find_dangerous_calls(tree)

        if findings:
            out = Path(DIRS["analysis_ast"]) / f"{Path(fp).name}.ast.txt"
            with open(out, "w") as f:
                for ftype, name, line in findings:
                    f.write(f"[{ftype}] {name} at line {line}\n")
            success(f"AST findings: {out}")

    success("DEEP MODE completed.")


# ============================================================
#  DOM MODE – DOM XSS SOURCE → SINK FLOW
# ============================================================

DOM_SOURCES = [
    r"location\.hash",
    r"location\.search",
    r"document\.URL",
    r"document\.documentURI",
    r"document\.location",
    r"window\.name",
    r"localStorage\.getItem",
    r"sessionStorage\.getItem",
]

DOM_SINKS = [
    r"innerHTML",
    r"outerHTML",
    r"document\.write",
    r"insertAdjacentHTML",
    r"eval",
    r"Function",
]


def find_sources(js):
    matches = []
    for s in DOM_SOURCES:
        res = re.findall(s, js)
        if res:
            matches.append((s, res))
    return matches


def find_sinks(js):
    matches = []
    for s in DOM_SINKS:
        res = re.findall(s, js)
        if res:
            matches.append((s, res))
    return matches


def run_dom_mode(args):
    info("Running DOM MODE (DOM-XSS detection)...")

    if not args.jsdir:
        error("--jsdir required for DOM mode")
        return

    js_files = collect_js_files([args.jsdir])

    for fp in js_files:
        js = Path(fp).read_text(errors="ignore")

        sources = find_sources(js)
        sinks = find_sinks(js)

        if sources or sinks:
            out = Path(DIRS["analysis_dom"]) / f"{Path(fp).name}.domxss.txt"
            with open(out, "w") as f:
                f.write("=== DOM SOURCES ===\n")
                for p, m in sources:
                    f.write(f"[SOURCE] {p} → {m}\n")

                f.write("\n=== DOM SINKS ===\n")
                for p, m in sinks:
                    f.write(f"[SINK] {p} → {m}\n")

                # Simple source → sink correlation
                if sources and sinks:
                    f.write("\n!!! POSSIBLE DOM XSS !!!\n")

            success(f"DOM-XSS results: {out}")

    success("DOM MODE completed.")


# ============================================================
#  GAU MODE – RECON + JS DOWNLOADER
# ============================================================

def extract_js_urls_from_gau(file_path):
    """Pull all .js files from gau output."""
    urls = []
    try:
        for line in open(file_path, "r", errors="ignore"):
            if line.strip().endswith(".js"):
                urls.append(line.strip())
    except Exception as e:
        error(f"Failed to read GAU file: {e}")
    return urls


def run_gau_mode(args):
    info("Running GAU MODE (collector)...")

    if not args.target:
        error("--target example.com required for GAU mode")
        return

    gau_out = Path(DIRS["recon_gau"]) / f"{args.target}.txt"

    # Run gau command
    run_gau(args.target, str(gau_out))

    # Extract JS URLs
    js_urls = extract_js_urls_from_gau(gau_out)
    success(f"Extracted {len(js_urls)} JS URLs")

    # Download JS files
    if js_urls:
        asyncio.run(download_js_bulk(js_urls, DIRS["recon_js"]))

    success("GAU MODE finished.")


# ============================================================
#  PROFESSIONAL MODE – COMPREHENSIVE SCAN
# ============================================================

def run_professional_mode(args):
    info("Running PROFESSIONAL MODE (comprehensive scan)...")

    if not args.jsdir:
        error("--jsdir required for PROFESSIONAL mode")
        return

    # Run all analysis modes
    info("Running secrets scan...")
    run_big_mode(args)
    
    if ESPRIMA_AVAILABLE:
        info("Running AST analysis...")
        run_deep_mode(args)
    
    info("Running DOM-XSS analysis...")
    run_dom_mode(args)

    success("PROFESSIONAL MODE completed.")


# ============================================================
#  🚀 MAIN
# ============================================================

def main():
    parser = build_parser()
    args = parser.parse_args()

    ensure_directories()  # create folder structure

    mode = args.mode.lower()

    if mode == "big":
        run_big_mode(args)

    elif mode == "deep":
        run_deep_mode(args)

    elif mode == "dom":
        run_dom_mode(args)

    elif mode == "professional":
        run_professional_mode(args)

    elif mode == "gau":
        run_gau_mode(args)

    else:
        error("Invalid mode.")


if __name__ == "__main__":
    main()
