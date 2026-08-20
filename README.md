# Resume Builder

## Запуск в локальной сети

На компьютере, где находится проект, выполните:

```powershell
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

Другие устройства в той же Wi-Fi сети открывают адрес:

```text
http://192.168.31.133:8000/
```

IP `192.168.31.133` нужно заменить на текущий IPv4-адрес компьютера. Узнать его можно командой `ipconfig`. Адрес `0.0.0.0:8000` используется только для запуска сервера и не открывается как адрес сайта в браузере. `192.0.0.1` обычно является адресом роутера, а не ноутбука.

Если Windows Firewall блокирует подключение, в PowerShell от имени администратора выполните:

```powershell
New-NetFirewallRule -DisplayName "Resume Builder 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

## Доступ через интернет

Локальный IP (`192.168.x.x`) доступен только внутри вашей сети. Для доступа из интернета нужен публичный сервер или туннель, например Cloudflare Tunnel/ngrok. Не публикуйте встроенный Django `runserver` с `DEBUG = True` на постоянный публичный адрес.

Для домена или HTTPS можно указать доверенные адреса перед запуском:

```powershell
$env:CSRF_TRUSTED_ORIGINS = "https://your-domain.example,https://www.your-domain.example"
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```