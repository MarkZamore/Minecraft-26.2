# Обновление существующего профиля 26.2 → 26.3

Подготовлено 28 октября 2026 года из `MarkZamore/Minecraft-26.2`, коммит `e492258f968171eb79d710ca48bd5226889f1129`, в отдельной независимой копии. Личные миры не копировались и не открывались. Исходные SHA-256 всех Git blobs, включая JAR и пресет, сохранены в `upgrades/minecraft-26.2-baseline.json`; отличающиеся Windows CRLF checkout-хеши подписаны отдельно. В прежнем авторском репозитории не было config/kubejs/scripts/defaultconfigs.

## Точные замены

| Компонент | Было | Стало | Причина |
| --- | --- | --- | --- |
| Minecraft | 26.2 | 26.3 | Последний официальный release в [Mojang version manifest](https://piston-meta.mojang.com/mc/game/version_manifest_v2.json) на дату подготовки |
| NeoForge | 26.2.0.84 | 26.3.0.99 | Версия для выбранного 26.3 из [официального Maven](https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml) |
| EMI, тот же порт link-fgfgui | `1.1.24-b60b8f8+26.2+neoforge`, Alpha build+59 | `1.1.24-e7edb3a+26.3+neoforge`, Alpha build+62 | Актуальный файл того же автора для 26.3, без смены проекта на одноимённый форк |
| e4steam, управляется лаунчером | 0.3.2, MC `[1.20.2,26.3)` | 0.3.4, MC `[1.20.2,26.4)` | Старый диапазон исключает 26.3; выбран новый авторский JAR с подтверждённым диапазоном |

| Файл | Размер | SHA-256 |
| --- | ---: | --- |
| Прежний `emi-1.1.24-b60b8f8+26.2+neoforge.jar` | 1107376 | `72e4e63f3ba39c149d15681a864282c116d3cc064e978f0848958cd1bf71058e` |
| Новый `emi-1.1.24-e7edb3a+26.3+neoforge.jar` | 1111167 | `a74ffcc975700740b16169e96ed179c88fc121a41f84345c34ed6e4f513296db` |
| Прежний управляемый `e4steam-neoforge-mc1.20.2-26.2-v0.3.2.jar` | 3734370 | `4f182b2560a6e001f248cd59cc063dd1c99d92a9b1b38ef099bc8ee822fe0418` |
| Новый управляемый `e4steam-neoforge-mc1.20.2-26.3-v0.3.4.jar` | 3815800 | `b7c388393b7c27d188c17981073a2471c7ac52b95d5cff8b8dc8f19946d67be0` |
| Официальный клиент Mojang 26.3, не включён в pack assets | 41483720 | `4508d006323f24fa02876310c192d739af56516eb259000ac50f0909a68c9a2d` |
| NeoForge 26.3.0.99 installer, не включён в pack assets | Из официального Maven | `7eeb74544422b757aa1611f6487a74bf9f4a8c7e04b2023c2080a6e637dfd218` |

Прежний EMI повторно скачан как авторский CurseForge [file 8616659](https://www.curseforge.com/minecraft/mc-mods/emi-unofficial-port-unstable/files/8616659): SHA совпал с исходным JAR. Новый [file 9242955](https://www.curseforge.com/minecraft/mc-mods/emi-unofficial-port-unstable/files/9242955) у того же проекта 1544558 заявляет Minecraft 26.3, NeoForge и Alpha. [Сравнение авторских исходников](https://github.com/link-fgfgui/emi/compare/b60b8f8f24260f1fc4aeef4a4e05f34a75b569ce...e7edb3aa4d7619eaaa03e01084fe01bb3db567e7) связывает прежний и новый build. Авторский mod ID остаётся `emi`. Обязательная зависимость JAR — NeoForge `[20.4.72-beta,)`, side BOTH; Minecraft-target проверен по авторскому файлу, а не выведен из этого широкого dependency range.

EMI содержит существующие серверные пути выдачи предметов и заполнения рецептов. Проверка source diff не выявила нового источника изменения terrain/chunk/palette, новой caster/owner-механики или отложенных разрушений. Сохранены прежние ограничения команды/creative перед выдачей и очисткой инвентаря и проверки текущего меню, container ID, slot range, mayPickup/mayPlace с возвратом остатков. Это не декларация «строго client-only». Собственный Safety-мод в этот лёгкий профиль не добавлен; обновление exact-SHA модулей Modified Safety не требуется, поскольку эта другая сборка и её JAR не меняются. Runtime-защита не объявлена проверенной.

e4steam 0.3.4 получен из [авторского release](https://github.com/Kamilhik/e4steam/releases/tag/v0.3.4); размер и SHA сверены с release digest и `SHA256SUMS.txt`. Транспорт остаётся ответственностью `SteamTransportCatalog`/`ManagedComponentService` лаунчера. В этом репозитории не публикуется второй e4steam и не расширяется диапазон старого JAR.

## Активный состав и перенос

`tools/distribution-lock.json` содержит только новый EMI; генератор сверяет список JAR, байты и фактические mod ID. Старый JAR находится только в отдельном `tools/legacy-files.json`, который превращается в `legacyFiles` манифеста. Исторические записи не включаются в `files`, `assets`, счётчик модов или library bundle. Перемещение профиля и каталога выполняет обновлённый лаунчер; стабильный library ID `minecraft-26-2` сохранён.

Меняется базовая игровая версия и базовый JAR EMI, поэтому это не обновление «только аддонами». Новые JAR не подменяют registry ID других игровых модов: активным остаётся только `emi`. Обновление формата самого Minecraft и перенос старых миров без потерь не проверялись; успешный packer не подтверждает их. Миры, UUID, инвентарь и личные настройки не редактировались при подготовке.

## Проверки без запуска игры

```powershell
python -B tools/keybinds/scan_keys.py --client <actual-26.3-client.jar> --javap C:/Tools/jdk-25.0.2/bin/javap.exe --verify
python -B tools/keybinds/build_preset.py --check
python -B tools/keybinds/check_preset.py
python -B -m unittest discover -s tools/keybinds -p test_preset.py
python -B -m unittest discover -s tools -p test_pack_library.py
python -B -m unittest discover -s tools -p test_manifest_upgrade.py
python -B tools/generate_manifest.py --pack . --out dist --revision <commit>
python -B tools/generate_manifest.py --pack . --out dist --verify-only
```

Проверено 62 ванильных назначения, 60 назначенных клавиш и 18 точных штатных пересечений. Единственное новое назначение — `key.debug.improvedTransparency` на X; реальный `KeyboardHandler` вызывает его внутри `handleDebugKeys`, gated через `keyDebugModifier` (F3). Поэтому добавлено только соответствующее исключение пары с creative toolbar X. По таблице самого клиента подтверждены новые SDL-числа клавиатуры и кнопок мыши; прежняя GLFW-таблица не использовалась. EMI новых `KeyMapping` не создаёт.

Проведены 8 проверок пресета, 10 библиотечных тестов и 3 проверки upgrade manifest. Последние отклоняют изменённые байты JAR, случайно оставленный старый JAR, active/legacy collision и обход пути. Подготовленный манифест содержит три активных файла, один mod ID и один exact-hash legacy file; staged payload и library archive проходят проверку размера и SHA.

По последнему решению пользователя **Minecraft не запускался**. Полный клиент, мир, Steam overlay, второй клиент, собственный/чужой скин и первый вид не объявляются PASS. Этот протокол подтверждает подготовку, происхождение, offline-проверки и состав публикации; он не заменяет игровые испытания.
