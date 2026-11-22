import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# 👇 ВСТАВЬ ТОКЕН
TOKEN = "9003918789:AAFQCOXzx9MsHuUOXPWlEf047N8w2I6h-Sw"
# 👇 СЮДА ВСТАВИШЬ ССЫЛКУ НА САЙТ (когда задеплоишь на Railway)
WEBAPP_URL = "https://твой-сайт.up.railway.app" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
users = {} # База данных в памяти

# ==========================================
# 1. HTML и JS (САМО ПРИЛОЖЕНИЕ)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Хомяк Кликер</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #1c1c1e; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; user-select: none; }
        h1 { font-size: 40px; margin: 10px 0; }
        #hamster { font-size: 150px; cursor: pointer; transition: transform 0.1s; }
        #hamster:active { transform: scale(0.9); }
        .btn { background-color: #2ecc71; color: white; border: none; padding: 15px 30px; font-size: 20px; border-radius: 10px; margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <h1 id="score">0</h1>
    <div style="font-size: 20px; color: #888;">монет</div>
    
    <!-- Хомяк -->
    <div id="hamster">🐹</div>
    
    <br>
    <button class="btn" onclick="saveData()">Сохранить в бота</button>

    <script>
        let score = 0;
        let tg = window.Telegram.WebApp;
        tg.expand(); // Открыть на весь экран
        tg.ready();

        // Загружаем сохраненные данные из Telegram
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            let uid = tg.initDataUnsafe.user.id;
            fetch('/get_score?user_id=' + uid)
                .then(res => res.json())
                .then(data => {
                    score = data.score || 0;
                    document.getElementById('score').innerText = score;
                });
        }

        // Клик по хомяку
        document.getElementById('hamster').addEventListener('click', function() {
            score += 1;
            document.getElementById('score').innerText = score;
        });

        // Сохранение
        function saveData() {
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                let uid = tg.initDataUnsafe.user.id;
                fetch('/save_score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: uid, score: score })
                }).then(() => {
                    tg.showAlert("Сохранено! Играем дальше.");
                });
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# 2. СЕРВЕР (ОТДАЕТ HTML И СОХРАНЯЕТ ОЧКИ)
# ==========================================
async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def handle_get(request):
    uid = int(request.query.get('user_id', 0))
    score = users.get(uid, {}).get("score", 0)
    return web.json_response({"score": score})

async def handle_save(request):
    data = await request.json()
    uid = data['user_id']
    users[uid] = {"score": data['score']}
    return web.json_response({"status": "ok"})

# ==========================================
# 3. ЛОГИКА БОТА
# ==========================================
@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐹 Открыть Хомяка", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Жми кнопку ниже, чтобы начать кликать!", reply_markup=kb)

# ==========================================
# 4. ЗАПУСК ВСЕГО ВМЕСТЕ
# ==========================================
async def main():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/get_score', handle_get)
    app.router.add_post('/save_score', handle_save)
    
    runner = web.AppRunner(app)
    await runner.setup()
    # Railway автоматически выдает порт. Локально это 8080.
    site = web.TCPSite(runner, '0.0.0.0', 8080) 
    await site.start()

    dp.include_router(router)
    print("Сервер и бот запущены!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
