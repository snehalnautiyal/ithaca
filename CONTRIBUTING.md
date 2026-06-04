# Contributing to Ithaca

Thanks for your interest! Help is welcome on all fronts.

## Getting Started

```bash
git clone https://github.com/snehalnautiyal/ithaca.git
cd ithaca
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Pull Requests

- Fork → branch → PR to `main`
- Keep PRs focused: one feature or fix per PR
- Include tests for new features
- Run `python -m pytest tests/` before submitting
- Use clear commit messages

## Good First Issues

- Fresh-install testing on different OS/hardware
- Mobile UI improvements
- Provider setup edge cases
- Documentation improvements
- Test coverage for edge cases

## Code Style

- Python: type hints, small focused modules, no god-files
- Frontend: vanilla JS, no framework, modular files under `static/js/`
- Tests required for every route and core module

## Security Issues

Please report security issues privately — see [SECURITY.md](SECURITY.md).
