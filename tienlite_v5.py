import importlib.util
from pathlib import Path


class ModuleLoader:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)

    def load(self, module_name: str):
        path = self.root_dir / f"{module_name}.tien"
        if not path.exists():
            raise FileNotFoundError(f"Module not found: {module_name}")
        source = path.read_text(encoding="utf-8")
        return source


class TienLite5:
    def __init__(self, root_dir="."):
        self.env = {
            "print": lambda *args: print(*args),
            "len": lambda x: len(x),
            "sum": lambda x: sum(x),
        }
        self.loader = ModuleLoader(root_dir)

    def run(self, source: str):
        for line in source.splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if text.startswith("let "):
                name, expr = text[4:].split("=", 1)
                self.env[name.strip()] = self.eval_expr(expr.strip())
            elif text.startswith("print("):
                print(self.eval_expr(text[6:-1]))
            elif text.startswith("import "):
                mod = text[7:].strip()
                code = self.loader.load(mod)
                self.run(code)
            elif text.startswith("fn "):
                signature = text[3:]
                name, params_part = signature.split("(", 1)
                params = [p.strip() for p in params_part.split(")")[0].split(",") if p.strip()]
                self.env[name.strip()] = {"params": params, "body": []}
            elif text.startswith("if "):
                cond, rest = text[3:].split("{", 1)
                body = rest.rsplit("}", 1)[0].strip()
                if self.eval_condition(cond.strip()):
                    self.run_block(body)
            else:
                raise ValueError(f"Unsupported line: {text}")

    def run_block(self, block_text: str):
        for line in block_text.splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            if text.startswith("let "):
                name, expr = text[4:].split("=", 1)
                self.env[name.strip()] = self.eval_expr(expr.strip())
            elif text.startswith("print("):
                print(self.eval_expr(text[6:-1]))
            elif text.startswith("import "):
                mod = text[7:].strip()
                source = self.loader.load(mod)
                self.run(source)
            else:
                raise ValueError(f"Unsupported block line: {text}")

    def eval_condition(self, expr: str):
        for op in ["==", "!=", ">=", "<=", ">", "<"]:
            if op in expr:
                left, right = expr.split(op, 1)
                a = self.eval_expr(left.strip())
                b = self.eval_expr(right.strip())
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
        return bool(self.eval_expr(expr))

    def eval_expr(self, expr: str):
        expr = expr.strip()
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr in self.env:
            return self.env[expr]
        if "[" in expr and "]" in expr:
            inner = expr[1:-1]
            return [self.eval_expr(part.strip()) for part in inner.split(",") if part.strip()]
        if ".." in expr:
            start, end = expr.split("..", 1)
            return list(range(int(self.eval_expr(start.strip())), int(self.eval_expr(end.strip())) + 1))
        for op in ["+", "-", "*", "/"]:
            if op in expr:
                left, right = expr.split(op, 1)
                a = self.eval_expr(left.strip())
                b = self.eval_expr(right.strip())
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
                raise ValueError(f"Unable to evaluate: {expr}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tienlite_v5.py <file.tien>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        TienLite5().run(handle.read())
