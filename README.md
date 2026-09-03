# Resume Builder

## Відновлення пароля через email

У режимі розробки посилання для відновлення пароля виводиться в терміналі, де запущений Django-сервер. Щоб надсилати листи насправді, налаштуйте SMTP перед запуском сервера.

Для Gmail потрібно створити **App Password** і виконати в PowerShell на Acer:

```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_USE_TLS="True"
$env:EMAIL_HOST_USER="ваша-пошта@gmail.com"
$env:EMAIL_HOST_PASSWORD="пароль-додатка-gmail"
$env:DEFAULT_FROM_EMAIL="ваша-пошта@gmail.com"
python.exe manage.py runserver 0.0.0.0:8000
```

Не записуйте пароль пошти у файли проєкту та не надсилайте його в чат.

## Українська

### Перегляд з телефона або іншого ноутбука через Acer

Сайт потрібно запускати саме на ноутбуці **Acer Aspire 3 A315-35**. Телефон або інший ноутбук лише підключається до Acer через ту саму Wi-Fi мережу.

1. Підключіть Acer і другий пристрій до однієї Wi-Fi мережі.
2. На Acer відкрийте PowerShell у папці проєкту та запустіть:

```powershell
python.exe manage.py runserver 0.0.0.0:8000
```

3. На Acer виконайте команду `ipconfig` і знайдіть його IPv4-адресу, наприклад `192.168.31.133`.
4. На телефоні або іншому ноутбуці відкрийте адресу `http://192.168.31.133:8000/`, замінивши адресу на IPv4-адресу Acer.
5. Не закривайте PowerShell, поки переглядаєте сайт.

Якщо сайт не відкривається, дозвольте порт 8000 у Windows Firewall у PowerShell від імені адміністратора:

```powershell
New-NetFirewallRule -DisplayName "Resume Builder 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Запуск на Windows

Відкрийте PowerShell у папці проєкту та виконайте:

```powershell
python.exe manage.py migrate
python.exe manage.py runserver 0.0.0.0:8000
```

Якщо у вас створено віртуальне середовище `.venv`, замініть `python.exe` у командах на `.venv\Scripts\python.exe`.

Після запуску відкрийте сайт на цьому ноутбуці за адресою:

```text
http://127.0.0.1:8000/
```

Щоб відкрити сайт на іншому пристрої, наприклад на MacBook учителя:

1. Підключіть обидва пристрої до тієї самої Wi-Fi мережі.
2. На ноутбуці виконайте `ipconfig` і знайдіть IPv4-адресу, наприклад `192.168.31.133`.
3. На MacBook відкрийте `http://192.168.31.133:8000/`.
4. Не закривайте PowerShell, поки сайт має працювати.

Команда `0.0.0.0:8000` дозволяє підключатися до сервера з інших пристроїв. Її не потрібно вводити в браузері.

Дізнайтеся IP ноутбука:

```powershell
ipconfig
```

Знайдіть IPv4, наприклад `192.168.31.133`. Учитель на MacBook повинен підключитися до тієї самої Wi-Fi мережі та відкрити:

```text
http://192.168.31.133:8000/
```

Якщо Windows блокує підключення, відкрийте PowerShell від імені адміністратора:

```powershell
New-NetFirewallRule -DisplayName "Resume Builder 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Доступ з будь-якої мережі

IP `192.168.x.x` працює лише у вашій локальній мережі. Для доступу вчителя з іншої мережі використайте хостинг або тунель Cloudflare Tunnel/ngrok. Не публікуйте Django `runserver` з `DEBUG = True` у production.

### Доступ учителя з іншого інтернету через Cloudflare Tunnel

Встановіть Cloudflare Tunnel на Windows:

```powershell
winget install Cloudflare.cloudflared
```

У першому вікні PowerShell запустіть сайт:

```powershell
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

У другому вікні PowerShell запустіть тунель:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare покаже посилання на кшталт `https://random-name.trycloudflare.com`. Надішліть це посилання вчителю: воно працюватиме з MacBook та іншої мережі. Тримайте обидва вікна відкритими. Для завершення натисніть `Ctrl+C` у кожному вікні.

## English

### Run on Windows

Open PowerShell in the project folder and run:

```powershell
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

`0.0.0.0:8000` makes the server listen on all network interfaces. It is only a server binding address and should not be entered in the browser.

Find the laptop IP address:

```powershell
ipconfig
```

For example, if the IPv4 address is `192.168.31.133`, the teacher should connect the MacBook to the same Wi-Fi network and open:

```text
http://192.168.31.133:8000/
```

If Windows Firewall blocks the connection, run PowerShell as Administrator:

```powershell
New-NetFirewallRule -DisplayName "Resume Builder 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Access from any network

An address such as `192.168.x.x` works only inside the local network. For access from another network, use hosting or a tunnel such as Cloudflare Tunnel/ngrok. Do not expose Django `runserver` with `DEBUG = True` as a production server.

### Teacher access from another internet connection with Cloudflare Tunnel

Install Cloudflare Tunnel on Windows:

```powershell
winget install Cloudflare.cloudflared
```

Run the site in the first PowerShell window:

```powershell
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Run the tunnel in a second PowerShell window:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare will print a URL such as `https://random-name.trycloudflare.com`. Send that URL to the teacher. It works from a MacBook on another network. Keep both windows open and press `Ctrl+C` in both windows to stop.

## Русский

### Запуск на Windows

Откройте PowerShell в папке проекта и выполните:

```powershell
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

`0.0.0.0:8000` означает, что сервер принимает подключения через все сетевые интерфейсы. Это адрес привязки сервера, его не нужно вводить в браузере.

Узнайте IP ноутбука:

```powershell
ipconfig
```

Например, если IPv4 равен `192.168.31.133`, учитель должен подключить MacBook к той же Wi-Fi сети и открыть:

```text
http://192.168.31.133:8000/
```

Если Windows Firewall блокирует подключение, запустите PowerShell от имени администратора:

```powershell
New-NetFirewallRule -DisplayName "Resume Builder 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Доступ из любой сети

Адрес `192.168.x.x` работает только внутри локальной сети. Для доступа учителя из другой сети нужен хостинг или туннель Cloudflare Tunnel/ngrok. Не публикуйте встроенный Django `runserver` с `DEBUG = True` как постоянный production-сервер.

### Доступ учителя из другой сети через Cloudflare Tunnel

Установите Cloudflare Tunnel на Windows:

```powershell
winget install Cloudflare.cloudflared
```

В первом окне PowerShell запустите сайт:

```powershell
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Во втором окне PowerShell запустите туннель:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare покажет ссылку вида `https://random-name.trycloudflare.com`. Отправьте её учителю: ссылка будет работать на MacBook из другой сети. Оба окна должны оставаться открытыми. Для остановки нажмите `Ctrl+C` в каждом окне.