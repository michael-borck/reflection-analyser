# basic_usage

Minimal ways to run reflection-analyser.

## Install

```bash
pip install reflection-analyser
```

## CLI

```bash
reflection-analyser journal.md --json
```

Pass a file path, or `-` to read text from stdin. Without `--json` it prints a human-readable summary.

## Python

```python
from reflection_analyser import ReflectionAnalyser

result = ReflectionAnalyser().analyse("journal.md")
print(result.model_dump_json(indent=2))
```

## HTTP

```bash
reflection-analyser serve            # http://localhost:8015
curl -F file=@journal.md http://localhost:8015/analyse
```
