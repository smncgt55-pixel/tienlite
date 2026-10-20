import sys
import traceback


class TienLite6:
    def __init__(self):
        self.env = {
            "print": lambda *args: print(*args),
            "len": lambda x: len(x),
            "sum": lambda x: sum(x),
        }

    def run_file(self, path: str):
        with open(path, "r", encoding="utf-8") as handle:
            self.run(handle.read())

    def run(self, source: str):
        lines = source.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue
            if line.startswith("let "):
                name, expr = line[4:].split("=", 1)
                self.env[name.strip()] = self.eval_expr(expr.strip())
            elif line.startswith("print("):
                print(self.eval_expr(line[6:-1].strip()))
            elif line.startswith("if "):
                cond, rest = line[3:].split("{", 1)
                body, i = self._collect_block(lines, i + 1)
                if self.eval_condition(cond.strip()):
                    self.run(body)
            elif line.startswith("for "):
                var, after_var = line[4:].split(" in ", 1)
                iterable_expr, rest = after_var.split("{", 1)
                body, i = self._collect_block(lines, i + 1)
                iterable = self.eval_expr(iterable_expr.strip())
                for item in iterable:
                    local = self.env.copy()
                    local[var.strip()] = item
                    old_env = self.env
                    self.env = local
                    try:
                        self.run(body)
                    finally:
                        self.env = old_env
            elif line.startswith("fn "):
                signature = line[3:]
                name, params_part = signature.split("(", 1)
                params = [p.strip() for p in params_part.split(")")[0].split(",") if p.strip()]
                body, i = self._collect_block(lines, i + 1)
                self.env[name.strip()] = {"params": params, "body": body, "callable": True}
            elif line.startswith("return "):
                raise RuntimeError("return outside of function")
            elif line.startswith("import "):
                mod = line[7:].strip()
                with open(f"{mod}.tien", "r", encoding="utf-8") as handle:
                    self.run(handle.read())
            else:
                raise ValueError(f"Unsupported instruction: {line}")
            i += 1

    def _collect_block(self, lines, start_index):
        body_lines = []
        depth = 0
        i = start_index
        while i < len(lines):
            text = lines[i]
            if "{" in text:
                depth += 1
            if "}" in text:
                depth -= 1
                if depth == 0:
                    return "\n".join(body_lines), i
            if depth > 0:
                body_lines.append(text)
            i += 1
        raise ValueError("Unclosed block")

    def eval_condition(self, expr):
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
            value = self.env[expr]
            if isinstance(value, dict) and value.get("callable"):
                return value
            return value
        if expr.startswith("learn(") and expr.endswith(")"):
            inner = expr[6:-1]
            samples_part, degree_part = inner.split(",", 1)
            samples = self._parse_samples(samples_part.strip())
            degree = int(degree_part.strip())
            return self._train(samples, degree)
        if expr.startswith("[") and expr.endswith("]"):
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
                raise ValueError(f"Unknown expression: {expr}")

    def _parse_samples(self, samples_text: str):
        samples = []
        for chunk in samples_text.strip()[1:-1].split(")"):
            if not chunk.strip():
                continue
            item = chunk.strip().strip(",")
            if item.startswith("("):
                item = item[1:]
            if not item:
                continue
            x_str, y_str = item.split(",", 1)
            samples.append((float(x_str.strip()), float(y_str.strip())))
        return samples

    def _train(self, samples, degree):
        import numpy as np
        X = []
        y = []
        for x, target in samples:
            X.append([x ** p for p in range(degree + 1)])
            y.append(target)
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)

        def predict(value):
            vec = np.array([value ** p for p in range(degree + 1)], dtype=float)
            return float(np.dot(vec, coef))

        return predict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tienlite_v6.py <file.tien>")
        sys.exit(1)
    try:
        TienLite6().run_file(sys.argv[1])
    except Exception as exc:
        print(f"Error: {exc}")
        traceback.print_exc()
        sys.exit(1)
