# ztoe

Графік відключень Житомиробленерго в терміналі.

## Встановлення

```bash
pipx install git+https://github.com/vladyslavkodenko/ztoe.git
```

## Використання

```bash
ztoe                          # збережені підчерги (або всі, якщо нічого не збережено)
ztoe 1.2 3.1                  # конкретні підчерги (разово)
ztoe -s, --save 1.1 1.2       # запам'ятати вибір
ztoe -r, --reset              # забути вибір
ztoe -a, --all                # усі підчерги
ztoe -h, --help               # довідка
```
