import numpy as np


class TienLite4:
    def __init__(self):
        self.env = {
            "print": lambda *args: print(*args),
            "len": lambda x: len(x),
            "sum": lambda x: sum(x),
        }

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
            elif text.startswith("if "):
                cond, body = text[3:].split("{", 1)
                body = body.rsplit("}", 1)[0].strip()
                if self.eval_condition(cond.strip()):
                    self.run_block(body)
            elif text.startswith("fn "):
                signature = text[3:]
                name, params_part = signature.split("(", 1)
                params = [p.strip() for p in params_part.split(")")[0].split(",") if p.strip()]
                self.env[name.strip()] = {"params": params, "body": []}
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
            elif text.startswith("return "):
                return self.eval_expr(text[7:])
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
        if expr.startswith("learn(") and expr.endswith(")"):
            inner = expr[6:-1]
            samples_part, degree_part = inner.split(",", 1)
            samples = self._parse_samples(samples_part.strip())
            degree = int(degree_part.strip())
            return self._train_model(samples, degree)
        if "[" in expr and "]" in expr:
            inner = expr[1:-1]
            items = [self.eval_expr(part.strip()) for part in inner.split(",") if part.strip()]
            return items
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
        for item in samples_text.strip()[1:-1].split(")"):
            if not item.strip():
                continue
            if item.startswith("("):
                item = item[1:]
            value = item.strip().strip(",")
            if not value:
                continue
            x_str, y_str = value.split(",", 1)
            samples.append((float(x_str.strip()), float(y_str.strip())))
        return samples

    def _train_model(self, samples, degree):
        X = []
        y = []
        for x, target in samples:
            row = [x ** p for p in range(degree + 1)]
            X.append(row)
            y.append(target)
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

        def predict(value):
            vec = np.array([value ** p for p in range(degree + 1)], dtype=float)
            return float(np.dot(vec, coef))

        return predict


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tienlite_v4.py <file.tien>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        TienLite4().run(handle.read())
