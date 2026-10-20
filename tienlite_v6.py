import sys
import traceback


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


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
        self._run_block(lines, 0, self.env)

    def _run_block(self, lines, index, env):
        i = index
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue
            if line == "}":
                return i + 1
            if line.startswith("let "):
                name, expr = line[4:].split("=", 1)
                env[name.strip()] = self.eval_expr(expr.strip(), env)
                i += 1
                continue
            if line.startswith("print("):
                inner = line[6:-1].strip()
                print(self.eval_expr(inner, env))
                i += 1
                continue
            if line.startswith("if "):
                cond_text = line[3:line.index("{")].strip()
                body_lines, next_i, else_body_lines = self._collect_block_with_else(lines, i + 1)
                if self.eval_condition(cond_text, env):
                    self._run_block(body_lines, 0, env)
                elif else_body_lines is not None:
                    self._run_block(else_body_lines, 0, env)
                i = next_i
                continue
            if line.startswith("for "):
                rest = line[4:]
                var_name, after = rest.split(" in ", 1)
                iterable_expr = after.split("{", 1)[0].strip()
                body_lines, next_i, _ = self._collect_block_with_else(lines, i + 1)
                iterable = self.eval_expr(iterable_expr, env)
                for item in iterable:
                    local = dict(env)
                    local[var_name.strip()] = item
                    self._run_block(body_lines, 0, local)
                i = next_i
                continue
            if line.startswith("fn "):
                signature = line[3:]
                name, params_part = signature.split("(", 1)
                params = [p.strip() for p in params_part.split(")")[0].split(",") if p.strip()]
                body_lines, next_i, _ = self._collect_block_with_else(lines, i + 1)
                env[name.strip()] = {"params": params, "body": body_lines, "callable": True}
                i = next_i
                continue
            if line.startswith("return "):
                value = self.eval_expr(line[7:].strip(), env)
                raise ReturnSignal(value)
            if line.startswith("else "):
                i += 1
                continue
            if self._looks_like_call(line):
                self.eval_expr(line, env)
                i += 1
                continue
            raise ValueError(f"Unsupported instruction: {line}")

        return None

    def _collect_block_with_else(self, lines, start_index):
        body = []
        i = start_index
        while i < len(lines):
            text = lines[i].strip()
            if not text:
                i += 1
                continue
            if text == "}":
                return body, i + 1, None
            if text.startswith("else "):
                if text.startswith("else {"):
                    else_body, next_i = self._collect_else_body(lines, i + 1)
                    return body, i, else_body, next_i
                else:
                    i += 1
                    continue
            if "}" in text:
                before, _ = text.split("}", 1)
                if before.strip():
                    body.append(before.strip())
                return body, i + 1, None
            body.append(text)
            i += 1
        raise ValueError("Unclosed block")

    def _collect_else_body(self, lines, start_index):
        body = []
        i = start_index
        while i < len(lines):
            text = lines[i].strip()
            if not text:
                i += 1
                continue
            if text == "}":
                return body, i + 1
            if "}" in text:
                before, _ = text.split("}", 1)
                if before.strip():
                    body.append(before.strip())
                return body, i + 1
            body.append(text)
            i += 1
        raise ValueError("Unclosed else block")

    def eval_condition(self, expr, env):
        expr = expr.strip()
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

    def eval_expr(self, expr, env=None):
        env = self.env if env is None else env
        expr = expr.strip()
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr in env:
            return env[expr]
        if expr.startswith("learn(") and expr.endswith(")"):
            return self._train_learn(expr[6:-1], env)
        if expr.startswith("[") and expr.endswith("]"):
            inner = expr[1:-1]
            return [self.eval_expr(part.strip(), env) for part in inner.split(",") if part.strip()]
        if ".." in expr:
            start, end = expr.split("..", 1)
            return list(range(int(self.eval_expr(start.strip(), env)), int(self.eval_expr(end.strip(), env)) + 1))
        if self._looks_like_call(expr):
            func_name, args = self._parse_call(expr)
            callee = env.get(func_name)
            if callee is None:
                raise ValueError(f"Unknown function: {func_name}")
            if callable(callee):
                return callee(*[self.eval_expr(arg.strip(), env) for arg in args])
            if isinstance(callee, dict) and callee.get("callable"):
                local = dict(env)
                for param, value in zip(callee["params"], [self.eval_expr(arg.strip(), env) for arg in args]):
                    local[param] = value
                try:
                    self._run_block(callee["body"].splitlines(), 0, local)
                except ReturnSignal as rs:
                    return rs.value
                return None
            raise ValueError(f"Not callable: {func_name}")
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

    def _looks_like_call(self, expr):
        return expr.endswith(")") and "(" in expr and not expr.startswith('"')

    def _parse_call(self, expr):
        name, args_part = expr.split("(", 1)
        args = args_part[:-1]
        if not args.strip():
            return name.strip(), []
        parts = []
        current = []
        depth = 0
        for ch in args:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
            current.append(ch)
        if current:
            parts.append("".join(current).strip())
        return name.strip(), [p for p in parts if p]

    def _train_learn(self, inner, env):
        samples_part, degree_part = inner.split(",", 1)
        samples = self._parse_samples(samples_part.strip())
        degree = int(degree_part.strip())
        import numpy as np
        X = []
        y = []
        for x, target in samples:
            X.append([x ** p for p in range(degree + 1)])
            y.append(target)
        X = np.array(X, dtype=float)
        y = np.array(y, dtype=float)
        coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)

        def predict(value):
            vec = np.array([value ** p for p in range(degree + 1)], dtype=float)
            return float(np.dot(vec, coeffs))

        return predict

    def _parse_samples(self, samples_text):
        samples = []
        text = samples_text.strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        for item in text.split(")"):
            piece = item.strip().strip(",")
            if not piece:
                continue
            if piece.startswith("("):
                piece = piece[1:]
            if not piece:
                continue
            x_str, y_str = piece.split(",", 1)
            samples.append((float(x_str.strip()), float(y_str.strip())))
        return samples


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
