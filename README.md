# Minecraft 26.2

Ванильный Minecraft 26.2 для лаунчера LANMinecraft, и один-единственный мод: просмотрщик рецептов EMI.

Клиент игры сборка с собой не несёт — лаунчер берёт официальный у Mojang по номеру версии из
`portable-pack.json`. Поэтому в репозитории лежит ровно то, чего у Mojang нет: манифест и джарник мода.

## Что внутри

| | |
|---|---|
| Minecraft | 26.2 |
| Загрузчик | NeoForge 26.2.0.84 |
| Модов | 1 |

`mods/emi-1.1.24-b60b8f8+26.2+neoforge.jar` — неофициальный порт EMI 1.1.24 под 26.2, собранный
link-fgfgui (исходники: https://github.com/link-fgfgui/emi, страница:
https://www.curseforge.com/minecraft/mc-mods/emi-unofficial-port-unstable).

Своей сборки EMI под 26.x у автора мода нет: последняя официальная — 1.1.24 от 13 мая 2026, и её
потолок 1.21.1. Порт проверен по байтам: 452 класса, все в пакете `dev/emi/emi`, лицензия MIT,
идентификатор мода `emi`, из зависимостей только NeoForge. Он собран под официальные имена классов
26.2 и пользуется новым Fabric Recipe Sync API — тем самым, из-за отсутствия которого оригинал и
остановился на 1.21.1.

Автор порта помечает сборки под 26.2 как альфа. Если он подведёт, замена — один файл: JEI под 26.2
выходит регулярно, зависимостей у него тоже нет, и он работает только на клиенте.

## Как это публикуется

Пуш в `main` запускает `.github/workflows/publish.yml`: он собирает манифест и выкладывает его
вместе с активами в релиз `pack-latest`. Лаунчер читает именно этот релиз.


## Launcher library

`library/content.json` owns the player-facing description, stable identity, additional library IDs and curated addon relationships; `library/preview.jpg` is the original menu background resized for cards and the detail banner. `tools/pack_library.py` reads the actual shipped jars and builds a deterministic, content-addressed library bundle. The optional `library` field of `pack-manifest.json` names its size, SHA-256 and revision. It is published before the manifest, separately from installed game files, and ignored by older launchers.

## Пресет управления

`launcher/controls-preset.txt` возвращает все 61 назначение Minecraft 26.2 к стандартной ванильной раскладке, включая клавиши отладки F3 и режим наблюдателя. Клавиши EMI остаются в его собственном `config/emi.css`. Решения, источники, проверка полноты и публикация описаны в [tools/keybinds/design.md](tools/keybinds/design.md). Пресет применяется по кнопке лаунчера; личные настройки не меняются при загрузке обновления.
