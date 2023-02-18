# spotify-to-csv-export-webapp
Веб-приложение для экспорта сохраненных треков и плейлистов пользователя Spotify в формате CSV.

*Читать на других языках: [English](README.md), [Русский](README.ru.md).*

Стек: Flask, [Tekore](https://github.com/felix-hilden/tekore) _(Spotify веб-API клиент)_, Bootstrap 5.

[Scopes](https://developer.spotify.com/documentation/general/guides/authorization/scopes/) (области доступа приложения):
- user-library-read 
- playlist-read-collaborative 
- playlist-read-private

**Приложение не хранит пользовательских данных.** Токен Spotify хранится в cookie.

## Как использовать
1. Откройте [веб-сайт](https://spotify-csv-export-webapp.onrender.com).
2. Нажмите «Войти со Spotify».
3. Подтвердите доступ, нажав «ПРИНИМАЮ».
4. Появятся все ваши плейлисты Spotify. Здесь вы можете скачать отдельные плейлисты или просто скачать все.

Структура экспортированного `название_плейлиста.csv`:
- **track_uri**: URI трека Spotify, может использоваться для [реимпорта](#реимпорт-в-spotify).
- **track_name**: название трека.
- **artists**: список исполнителей.
- **album**: имя альбома.
- **duration**: продолжительность трека.

____
### Реимпорт в Spotify
:exclamation: **Работает только в "настольном" приложении Spotify**.

После сохранения плейлистов:
1. Создайте плейлист в Spotify.
2. Скопируйте из `название_плейлиста.csv` значения столбца `track_uri`
(пример значения: `spotify:track:2FJyRsWesaxh5nOTDQWBMw`).
3. Вставьте на страницу плейлиста Spotify.

____
#### :grey_exclamation: Обратите внимание, если вы используете MS Excel:
Если вы используете Excel для открытия `название_плейлиста.csv`, неанглийские символы могут отображаться в неправильной кодировке.
Чтобы это исправить — используйте другое приложение или попробуйте эти решения:
- https://stackoverflow.com/a/6488070
- [https://answers.microsoft.com/](https://answers.microsoft.com/en-us/msoffice/forum/all/how-to-open-utf-8-csv-file-in-excel-without-mis/1eb15700-d235-441e-8b99-db10fafff3c2)