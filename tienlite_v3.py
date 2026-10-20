import ast


class TienLite3:
    def __init__(self):
        self.env = {}

    def run(self, source: str):
        for line in source.splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            self.exec_line(text)

    def exec_line(self, text: str):
        if text.startswith("let "):
            name, expr = text[4:].split("=", 1)
            self.env[name.strip()] = self.eval_expr(expr.strip())
            return
        if text.startswith("print("):
            print(self.eval_expr(text[6:-1]))
            return
        if text.startswith("fn "):
            fn_signature = text[3:]
            name, params_part = fn_signature.split("(", 1)
            params = [p.strip() for p in params_part.split(")")[0].split(",") if p.strip()]
            body_lines = []
            # context intentionally simple for learner version
            self.env[name.strip()] = {"params": params, "body": body_lines}
            return
        if text.startswith("for "):
            # for i in 0..4 { ... }
            rest = text[4:]
            var, after_var = rest.split(" in ", 1)
            range_expr, body = after_var.split("{", 1)
            body_text = body.rsplit("}", 1)[0].strip()
            start, end = self.eval_range(range_expr.strip())
            for i in range(start, end + 1):
                local = self.env.copy()
                local[var.strip()] = i
                self.run_block(body_text, local)
            return
        if text.startswith("if "):
            cond, rest = text[3:].split("{", 1)
            body = rest.rsplit("}", 1)[0].strip()
            if self.eval_condition(cond.strip()):
                self.run_block(body, self.env)
            return
        raise ValueError(f"Unsupported line: {text}")

    def run_block(self, block_text: str, local_env):
        for line in block_text.splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if text.startswith("let "):
                name, expr = text[4:].split("=", 1)
                local_env[name.strip()] = self.eval_expr(expr.strip(), local_env)
            elif text.startswith("print("):
                print(self.eval_expr(text[6:-1], local_env))
            elif text.startswith("if "):
                cond, rest = text[3:].split("{", 1)
                body = rest.rsplit("}", 1)[0].strip()
                if self.eval_condition(cond.strip(), local_env):
                    self.run_block(body, local_env)
            else:
                raise ValueError(f"Unsupported block line: {text}")

    def eval_range(self, expr: str):
        if ".." in expr:
            a, b = expr.split("..", 1)
            return int(self.eval_expr(a.strip())), int(self.eval_expr(b.strip()))
        raise ValueError(f"Range expected: {expr}")

    def eval_condition(self, expr: str, env=None):
        env = self.env if env is None else env
        for op in ["==", "!=", ">=", "<=", ">", "<"]:
            if op in expr:
                left, right = expr.split(op, 1)
                a = self.eval_expr(left.strip(), env)
                b = self.eval_expr(right.strip(), env)
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
        return bool(self.eval_expr(expr, env))

    def eval_expr(self, expr: str, env=None):
        env = self.env if env is None else env
        expr = expr.strip()
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr in env:
            return env[expr]
        if "[" in expr and "]" in expr:
            inner = expr[1:-1]
            items = [self.eval_expr(part.strip(), env) for part in inner.split(",") if part.strip()]
            return items
        if ".." in expr:
            start, end = expr.split("..", 1)
            return list(range(int(self.eval_expr(start.strip(), env)), int(self.eval_expr(end.strip(), env)) + 1))
        for op in ["+", "-", "*", "/"]:
            if op in expr:
                left, right = expr.split(op, 1)
                a = self.eval_expr(left.strip(), env)
                b = self.eval_expr(right.strip(), env)
                if op == "+":
                    return a + b
                if op == "-":
                    return a - b
                if op == "*":
                    return a * b
                if op == "/":
                    return a / b
        try:
            return int(expr)
        except ValueError:
            try:
                return float(expr)
            except ValueError:
                raise ValueError(f"Unknown expression: {expr}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tienlite_v3.py <file.tien>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        TienLite3().run(handle.read())
