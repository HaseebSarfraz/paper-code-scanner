import argparse, hashlib, json, os, re, textwrap, time
from typing import Dict, Any, List
import requests

BASE_DEFAULT = "http://127.0.0.1:5000"
SMOKE_RE = re.compile(r'^\s*def\s+test_smoke_import\s*\(', re.M)
TEST_RE  = re.compile(r'^\s*def\s+test(?!_smoke_import)\w*\s*\(', re.M)

def now_ms(): return int(time.perf_counter() * 1000)
def sha12(s: str) -> str: return hashlib.sha256((s or "").encode()).hexdigest()[:12]

def call_run_tests(base: str, code: str, objective: str, timeout_s: int) -> Dict[str, Any]:
    t0 = now_ms()
    r = requests.post(f"{base}/api/run_tests",
                      json={"code": code, "objective": objective},
                      timeout=timeout_s)
    t1 = now_ms()
    r.raise_for_status()
    j = r.json()
    summ = j.get("summary", {}) or {}
    passed = int(summ.get("passed", 0))
    total  = passed + int(summ.get("failed", 0)) + int(summ.get("errors", 0)) + int(summ.get("skipped", 0))
    tests = j.get("tests", "") or ""
    output = j.get("output", "") or ""
    return {
        "elapsed_ms": t1 - t0,
        "summary": summ,
        "passed": passed, "total": total,
        "tests": tests, "output": output,
        "tests_len": len(tests),
        "test_count": len(TEST_RE.findall(tests)) + (1 if SMOKE_RE.search(tests) else 0),
        "has_parametrize": ("pytest.mark.parametrize" in tests),
        "smoke_only": bool(SMOKE_RE.search(tests) and not TEST_RE.search(tests)),
        "collection_error": ("ERROR collecting tests/test_solution.py" in output),
        "tests_sha12": sha12(tests),
        "compile_ok_tests": _compile_ok(tests),
    }

def _compile_ok(src: str) -> bool:
    try:
        compile(src or "", "tests/test_solution.py", "exec"); return True
    except Exception:
        return False

TASKS: List[Dict[str, str]] = [
    { "name": "square", "objective": "Return the square of integer x.",
      "code": "def func(x: int) -> int:\n    return x*x\n" },

    { "name": "nested_sum", "objective": "Recursively sum integers in a possibly nested list; if int return it; else raise TypeError.",
      "code": textwrap.dedent("""
          def add(x):
              if isinstance(x, int):
                  return x
              if isinstance(x, list):
                  return sum(add(e) for e in x)
              raise TypeError("only int or list")
      """).strip() },

    { "name": "factorial", "objective": "Return n! for non-negative ints using recursion; raise TypeError otherwise.",
      "code": textwrap.dedent("""
          def fact(n):
              if not isinstance(n, int) or n < 0:
                  raise TypeError("non-negative int required")
              if n in (0, 1):
                  return 1
              return n * fact(n - 1)
      """).strip() },

    { "name": "fibonacci", "objective": "Return nth Fibonacci (0-indexed) using recursion; n >= 0.",
      "code": textwrap.dedent("""
          def fib(n):
              if not isinstance(n, int) or n < 0:
                  raise TypeError("n >= 0 int required")
              if n < 2:
                  return n
              return fib(n-1) + fib(n-2)
      """).strip() },

    { "name": "gcd", "objective": "Return gcd(a,b) using Euclid; non-negative integers.",
      "code": textwrap.dedent("""
          def gcd(a, b):
              if a < 0 or b < 0:
                  raise TypeError("non-negative only")
              while b:
                  a, b = b, a % b
              return a
      """).strip() },

    { "name": "transpose", "objective": "Transpose a rectangular matrix (list of equal-length lists).",
      "code": textwrap.dedent("""
          def transpose(m):
              if not m:
                  return []
              w = len(m[0])
              for row in m:
                  if len(row) != w:
                      raise ValueError("rectangular only")
              return [list(row) for row in zip(*m)]
      """).strip() },
]

def run_suite(base: str, timeout_s: int, out_path: str) -> Dict[str, Any]:
    results = []
    for t in TASKS:
        r1 = call_run_tests(base, t["code"], t["objective"], timeout_s)
        r2 = call_run_tests(base, t["code"], t["objective"], timeout_s)
        deterministic = (r1["tests_sha12"] == r2["tests_sha12"])
        pass_rate = (r1["passed"] / r1["total"]) if r1["total"] else 0.0
        row = {
            "name": t["name"],
            "pass_rate": pass_rate,
            "deterministic": deterministic,
            "has_parametrize": r1["has_parametrize"],
            "smoke_only": r1["smoke_only"],
            "collection_error": r1["collection_error"],
            "test_count": r1["test_count"],
            "elapsed_ms": r1["elapsed_ms"],
            "tests_sha12": r1["tests_sha12"],
            "first": r1, "second": r2,
        }
        results.append(row)

    tasks_ok = sum(1 for r in results
                   if r["pass_rate"] == 1.0 and not r["smoke_only"] and not r["collection_error"])
    det_ok   = sum(1 for r in results if r["deterministic"])
    suite = {
        "base": base,
        "total_tasks": len(results),
        "tasks_ok": tasks_ok,
        "deterministic_tasks": det_ok,
        "acceptance": {
            "all_passed": (tasks_ok == len(results)),
            "determinism_ge_all": (det_ok == len(results)),
        }
    }
    report = {"suite": suite, "results": results}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report

def print_table(report: Dict[str, Any]) -> None:
    rows = report["results"]
    print("\nGEN validation")
    print("-" * 78)
    print("{:<14} {:<6} {:<5} {:<5} {:<6} {:<6} {:<10} {:<12}".format(
        "task","pass","det","param","smoke","err","tests","ms"))
    print("-" * 78)
    for r in rows:
        pr = f'{int(r["first"]["passed"])}/{int(r["first"]["total"])}'
        print("{:<14} {:<6} {:<5} {:<6} {:<6} {:<10} {:<12} ".format(
            r["name"][:14],
            pr,
            "Y" if r["deterministic"] else "-",
            "Y" if r["has_parametrize"] else "-",
            "Y" if r["smoke_only"] else "-",
            "Y" if r["collection_error"] else "-",
            str(r["test_count"]),
            str(r["elapsed_ms"]),
        ))
    s = report["suite"]
    print("-" * 78)
    print(f'OK: {s["tasks_ok"]}/{s["total_tasks"]} | Deterministic: {s["deterministic_tasks"]}/{s["total_tasks"]}')
    print("Report: gen_report.json\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("PCS_BASE", BASE_DEFAULT))
    ap.add_argument("--out", default="gen_report.json")
    ap.add_argument("--timeout", type=int, default=300, help="per-call HTTP timeout (seconds)")
    args = ap.parse_args()
    rep = run_suite(args.base, args.timeout, args.out)
    print_table(rep)
    ok = rep["suite"]["tasks_ok"] == rep["suite"]["total_tasks"]
    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
