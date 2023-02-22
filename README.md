![Badge](https://github.com/kalaluthien/yamlang/actions/workflows/unit_test.yaml/badge.svg)
![Badge](https://img.shields.io/badge/python-3.11-blue.svg)

# YamLang
A language in YAML to transform data in YAML.

Inspired by:
- [jq](https://github.com/stedolan/jq)
- [StrictYAML](https://github.com/crdoconnor/strictyaml)
- [GNU Smalltalk Programming Language](https://github.com/gnu-smalltalk/smalltalk)
- [Racket Programming Language](https://github.com/racket/racket)
- [The P Programming Language](https://github.com/p-org/P)

## Settings
```bash
git clone https://github.com/kalaluthien/yamlang.git
cd yamlang

conda create -n <environment-name> python=3.11
conda activate <environment-name>

pip install --upgrade pip
pip install -r requirements.txt
```

## Test
```bash
pip install pytest

pytest test/unit
```

## Development
```bash
pip install jupyter
pip install black
pip install isort
pip install pre-commit
```
