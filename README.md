# ds-store-dump

Dump backups and another files using `.DS_Store`.

> Любишь мак, люби ходить к проктологу...

Я не знаю откуда берутся долбоебы, которые считают, что гейбук идеально подходит для программирования, но благодаря ним можно заработать лишнюю копеечку.

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
$ ds-store-dump url1 url2 url3 > output
$ ds-store-dump < urls.txt
```

How to find `.DS_Store`:

```bash
httpx -rl 50 -l urls.txt -json -o output.json -sc -ct -ms 'Bud1' -mc 200 -path /.DS_Store
```
