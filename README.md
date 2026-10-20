# TienLite

TienLite is a small programmable language designed for GitHub Codespaces. It is intentionally simple, readable, and trainable. It evolves across six versions from a basic calculator to a real language shell with learning features.

Project goals:
- executable in GitHub Codespaces
- easy to understand and extend
- trainable through simple regression models
- language progression from V1 to V6

## Versions

- V1: variables, arithmetic, conditionals
- V2: functions and return values
- V3: loops, ranges, lists
- V4: built-in learning engine
- V5: modules and import system
- V6: full runtime, REPL, CLI, and tooling

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tienlite_v6.py examples/demo.tien
```

## Example

```text
let x = 10
let y = 3
print(x + y)

if x > y {
  print("x is greater")
} else {
  print("y is greater")
}

fn add(a, b) {
  return a + b
}

print(add(2, 5))

for i in 0..4 {
  print(i)
}

let model = learn([(0,0), (1,1), (2,4), (3,9)], 2)
print(model(5))
```

## Development

This repository includes a Codespaces devcontainer, a Python environment, and six progressive implementations.

## Notes

The language is intentionally lightweight. It is not meant to replace Python, but to demonstrate how one can build a compact programmable language for local experimentation and education.
