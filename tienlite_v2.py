def run(source: str):
    env = {}
    lines = source.strip().splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line or line.startswith("#"):
            idx += 1
            continue
        if line.startswith("let "):
            name, value = line[4:].split("=", 1)
            env[name.strip()] = eval_expr(value.strip(), env)
            idx += 1
            continue
        if line.startswith("print("):
            expr = line[6:-1].strip()
            print(eval_expr(expr, env))
            idx += 1
            continue
        if line.startswith("if "):
            cond_end = line.find("{")
            cond = line[3:cond_end].strip()
            block, idx = collect_block(lines, idx)
            if eval_condition(cond, env):
                run_block(block, env)
            continue
        if line.startswith("fn "):
            # fn name(arg1, arg2) { ... }
            fn_line = line
            name, rest = fn_line[3:].split("(", 1)
            args_text, body_block, idx = parse_function(lines, idx)
            env[name.strip()] = {"type": "function", "args": args_text, "body": body_block}
            continue
        if line.startswith("return "):
            raise RuntimeError("return must be used inside a function")
        raise ValueError(f"Unsupported statement: {line}")
    return env


def collect_block(lines, start_idx):
    start = start_idx
    depth = 0
    block_lines = []
    for i in range(start, len(lines)):
        l = lines[i]
        if "{" in l:
            depth += 1
        if "}" in l:
            depth -= 1
            if depth == 0:
                block_lines = lines[start + 1:i]
                return block_lines, i + 1
    raise ValueError("Unclosed block")


def parse_function(lines, start_idx):
    line = lines[start_idx].strip()
    name_part, params_part = line[3:].split("(", 1)
    name = name_part.strip()
    params = params_part.split(")", 1)[0].strip()
    args = [p.strip() for p in params.split(",") if p.strip()]
    block, idx = collect_block(lines, start_idx)
    return args, {"name": name, "body": block}, idx


def run_block(block_lines, env):
    for line in block_lines:
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if text.startswith("let "):
            name, value = text[4:].split("=", 1)
            env[name.strip()] = eval_expr(value.strip(), env)
        elif text.startswith("print("):
            print(eval_expr(text[6:-1].strip(), env))
        elif text.startswith("return "):
            return eval_expr(text[7:].strip(), env)
        else:
            raise ValueError(f"Unsupported block statement: {text}")


def eval_condition(expr: str, env: dict):
    ops = ["==", "!=", ">=", "<=", ">", "<"]
    for op in ops:
        if op in expr:
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
    return bool(eval_expr(expr, env))


def eval_expr(expr: str, env: dict):
    expr = expr.strip()
    if expr in env and isinstance(env[expr], dict):
        raise RuntimeError(f"Function {expr} is not callable yet")
    if expr in env:
        return env[expr]
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]
    if expr.startswith("(") and expr.endswith(")"):
        return eval_expr(expr[1:-1], env)
    for op in ["+", "-", "*", "/"]:
        if op in expr:
            left, right = expr.split(op, 1)
            left_val = eval_expr(left.strip(), env)
            right_val = eval_expr(right.strip(), env)
            if op == "+":
                return left_val + right_val
            if op == "-":
                return left_val - right_val
            if op == "*":
                return left_val * right_val
            if op == "/":
                return left_val / right_val
    try:
        return int(expr)
    except ValueError:
        try:
            return float(expr)
        except ValueError:
            raise ValueError(f"Unable to evaluate: {expr}")


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        print(run(handle.read()))
