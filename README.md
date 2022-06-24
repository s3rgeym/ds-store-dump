# ds-store-dump

Dump Files from `.DS_Store`.

Requires Python >= 3.10.x.

If you not Arch/Manjaro user install latest Python using [pyenv](https://github.com/pyenv/pyenv).

```bash
# Install

# For normal people
$ pipx install ds-store-dump

# For other
$ pip install ds-store-dump

# Usage
$ ds-store-dump -h
$ ds-store-dump https://site1.com https://site2.com ...
$ ds-store-dump < urls.txt
```

How to find `.DS_Store`:

```bash
httpx -l urls.txt -json -o output.json -sc -ct -ms 'Bud1' -mc 200 -path /.DS_Store
```
