import math


def run(source: str):
    env = {}
    lines = source.strip().splitlines()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("let "):
            name, value = line[4:].split("=", 1)
            env[name.strip()] = eval_expr(value.strip(), env)
            continue
        if line.startswith("print("):
            expr = line[6:-1].strip()
            print(eval_expr(expr, env))
            continue
        if line.startswith("if "):
            cond_end = line.find("{")
            cond = line[3:cond_end].strip()
            block = extract_block(lines, raw)
            if eval_condition(cond, env):
                run_block(block, env)
            continue
        raise ValueError(f"Unsupported statement: {line}")


def extract_block(lines, current_line):
    idx = lines.index(current_line)
    start = idx
    depth = 0
    block_lines = []
    for i in range(start, len(lines)):
        line = lines[i]
        if "{" in line:
            depth += 1
        if "}" in line:
            depth -= 1
            if depth == 0:
                block_lines = lines[start + 1:i]
                break
    return block_lines


def run_block(block_lines, env):
    for line in block_lines:
        l = line.strip()
        if not l or l.startswith("#"):
            continue
        if l.startswith("let "):
            name, value = l[4:].split("=", 1)
            env[name.strip()] = eval_expr(value.strip(), env)
        elif l.startswith("print("):
            print(eval_expr(l[6:-1].strip(), env))
        else:
            raise ValueError(f"Unsupported block line: {l}")


def eval_condition(expr: str, env: dict):
    expr = expr.strip()
    ops = ["==", "!=", ">=", "<=", ">", "<"]
    op = None
    for token in ops:
        if token in expr:
            op = token
            break
    if not op:
        return bool(eval_expr(expr, env))
    left, right = expr.split(op, 1)
    a = eval_expr(left.strip(), env)
    b = eval_expr(right.strip(), env)
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == "<":
        return a < b
    raise ValueError(f"Unsupported operator: {op}")


def eval_expr(expr: str, env: dict):
    expr = expr.strip()
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]
    if expr in env:
        return env[expr]
    try:
        return int(expr)
    except ValueError:
        pass
    try:
        return float(expr)
    except ValueError:
        pass
    if "+" in expr:
        a, b = expr.split("+", 1)
        return eval_expr(a.strip(), env) + eval_expr(b.strip(), env)
    if "-" in expr:
        a, b = expr.split("-", 1)
        return eval_expr(a.strip(), env) - eval_expr(b.strip(), env)
    if "*" in expr:
        a, b = expr.split("*", 1)
        return eval_expr(a.strip(), env) * eval_expr(b.strip(), env)
    if "/" in expr:
        a, b = expr.split("/", 1)
        return eval_expr(a.strip(), env) / eval_expr(b.strip(), env)
    raise ValueError(f"Unable to evaluate expression: {expr}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tienlite_v1.py <file.tien>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        run(handle.read())
