import asyncio
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# 👇 ВСТАВЬ СВОЙ НОВЫЙ ТОКЕН СЮДА
TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН_ОТ_BOTFATHER"
# 👇 ТВОЯ ССЫЛКА ИЗ RAILWAY (должна быть https://...)
WEBAPP_URL = "https://hambot-production.up.railway.app" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
users = {} # Временная база данных (живет пока работает сервер)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Hamster Mega</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; user-select: none; }
        body { background-color: #121212; color: white; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
        
        /* Верхняя панель */
        .header { display: flex; justify-content: space-between; padding: 20px; background: rgba(0,0,0,0.3); border-bottom: 1px solid #2a2a2a; }
        .header div { font-size: 14px; font-weight: 600; color: #a0a0a0; }
        .header span { color: white; font-weight: 800; display: block; font-size: 18px; margin-top: 4px; }

        /* Экран */
        .screen { flex: 1; display: none; flex-direction: column; align-items: center; justify-content: center; padding: 20px; position: relative; }
        .screen.active { display: flex; }

        /* Кликер */
        .balance { font-size: 48px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 0 10px rgba(255,215,0,0.5); }
        .sub-balance { font-size: 16px; color: #a0a0a0; margin-bottom: 30px; }
        
        .circle-container { position: relative; width: 280px; height: 280px; display: flex; justify-content: center; align-items: center; }
        .glow-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: conic-gradient(from 0deg, #ffd700, #ff8c00, #ffd700); animation: spin 3s linear infinite; filter: blur(8px); opacity: 0.7; }
        .hamster-btn { position: relative; width: 260px; height: 260px; border-radius: 50%; background: #1e1e1e; border: 4px solid #2a2a2a; display: flex; justify-content: center; align-items: center; font-size: 120px; cursor: pointer; transition: transform 0.1s; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); z-index: 2; }
        .hamster-btn:active { transform: scale(0.92); }
        
        /* Всплывающие монеты */
        .coin-anim { position: absolute; font-size: 24px; font-weight: 800; color: #ffd700; pointer-events: none; animation: floatUp 0.8s ease-out forwards; z-index: 10; }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-100px) scale(1.5); } }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* Прогресс-бар */
        .progress-container { width: 90%; margin-top: 40px; }
        .progress-info { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 8px; }
        .progress-bg { width: 100%; height: 12px; background: #2a2a2a; border-radius: 6px; overflow: hidden; }
        .progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #ffd700, #ff8c00); border-radius: 6px; transition: width 0.3s; }

        /* Вкладки */
        .menu { display: flex; flex-direction: column; width: 100%; gap: 15px; }
        .card { background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 16px; padding: 20px; text-align: center; }
        .card h2 { font-size: 20px; margin-bottom: 10px; }
        .card p { font-size: 14px; color: #a0a0a0; margin-bottom: 15px; }
        .btn { background: #ffd700; color: black; font-weight: 800; border: none; padding: 15px 20px; border-radius: 12px; font-size: 16px; cursor: pointer; width: 100%; transition: 0.2s; }
        .btn:active { background: #ffb700; transform: scale(0.98); }
        
        /* Нижнее меню */
        .nav-bar { display: flex; justify-content: space-around; padding: 15px 10px; background: #1a1a1a; border-top: 1px solid #2a2a2a; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 12px; color: #666; cursor: pointer; transition: 0.2s; }
        .nav-item.active { color: #ffd700; }
        .nav-item span { font-size: 24px; margin-bottom: 4px; }
    </style>
</head>
<body>

    <!-- Верхняя панель -->
    <div class="header">
        <div>Уровень <span id="top-level">1</span></div>
        <div>Монеты <span id="top-balance">0</span></div>
    </div>

    <!-- Экран 1: Кликер -->
    <div id="screen-mine" class="screen active">
        <div class="balance" id="balance">0</div>
        <div class="sub-balance">монет</div>
        
        <div class="circle-container" id="click-area">
            <div class="glow-ring"></div>
            <div class="hamster-btn" id="hamster">🐹</div>
        </div>

        <div class="progress-container">
            <div class="progress-info">
                <span>До следующего уровня</span>
                <span id="progress-text">0 / 100</span>
            </div>
            <div class="progress-bg">
                <div class="progress-fill" id="progress-bar"></div>
            </div>
        </div>
    </div>

    <!-- Экран 2: Друзья -->
    <div id="screen-friends" class="screen">
        <div class="menu">
            <div class="card">
                <h2>👥 Приглашай друзей</h2>
                <p>За каждого друга ты получаешь <b>+25,000 монет</b> и мощный буст!</p>
                <button class="btn" onclick="inviteFriend()">Пригласить друга</button>
            </div>
            <div class="card">
                <h2>Твои рефералы</h2>
                <p>Приглашено друзей: <b id="friends-count">0</b></p>
            </div>
        </div>
    </div>

    <!-- Экран 3: Бусты -->
    <div id="screen-boosts" class="screen">
        <div class="menu">
            <div class="card">
                <h2>🚀 Турбо-клик</h2>
                <p>Увеличивает монеты за клик на +1. (Цена: <span id="boost-cost">1000</span> монет)</p>
                <button class="btn" id="btn-boost" onclick="buyBoost()">Купить буст</button>
            </div>
        </div>
    </div>

    <!-- Экран 4: Кошелек -->
    <div id="screen-wallet" class="screen">
        <div class="menu">
            <div class="card">
                <h2>💎 Кошелек</h2>
                <p>Вывод средств появится в следующем обновлении!</p>
                <button class="btn" style="background:#2a2a2a; color:white;">Скоро...</button>
            </div>
        </div>
    </div>

    <!-- Нижнее меню -->
    <div class="nav-bar">
        <div class="nav-item active" onclick="switchTab('mine', this)"><span>🏠</span>Майнинг</div>
        <div class="nav-item" onclick="switchTab('friends', this)"><span>👥</span>Друзья</div>
        <div class="nav-item" onclick="switchTab('boosts', this)"><span>🚀</span>Бусты</div>
        <div class="nav-item" onclick="switchTab('wallet', this)"><span>💎</span>Кошелек</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand(); // Открыть на весь экран
        tg.ready();

        // Состояние игрока
        let state = {
            balance: 0,
            level: 1,
            taps: 0,
            tapsRequired: 100,
            tapPower: 1,
            friends: 0,
            boostCost: 1000
        };

        let uid = tg.initDataUnsafe?.user?.id || 12345;
        let username = tg.initDataUnsafe?.user?.username || "player";

        // Загрузка данных при старте
        fetch('/api/load?user_id=' + uid)
            .then(r => r.json())
            .then(data => {
                if(data && data.balance !== undefined) {
                    state = Object.assign(state, data);
                }
                updateUI();
            })
            .catch(e => console.log("Оффлайн режим"));

        // Функция обновления интерфейса
        function updateUI() {
            document.getElementById('balance').innerText = state.balance.toLocaleString();
            document.getElementById('top-balance').innerText = state.balance.toLocaleString();
            document.getElementById('top-level').innerText = state.level;
            document.getElementById('friends-count').innerText = state.friends;
            document.getElementById('boost-cost').innerText = state.boostCost.toLocaleString();
            document.getElementById('progress-text').innerText = state.taps + " / " + state.tapsRequired;
            
            let percent = (state.taps / state.tapsRequired) * 100;
            if(percent > 100) percent = 100;
            document.getElementById('progress-bar').style.width = percent + "%";

            // Меняем хомяка в зависимости от уровня
            let hamsters = ["🐹", "🐭", "🦦", "🦫", "🦈", "🐳", "👑"];
            let idx = Math.min(state.level - 1, hamsters.length - 1);
            document.getElementById('hamster').innerText = hamsters[idx];
        }

        // Обработка клика
        document.getElementById('click-area').addEventListener('touchstart', function(e) {
            e.preventDefault();
            state.balance += state.tapPower;
            state.taps += 1;
            
            // Проверка на новый уровень
            if (state.taps >= state.tapsRequired) {
                state.taps = 0;
                state.level += 1;
                state.tapsRequired *= 10; // Каждый раз в 10 раз больше
                tg.showAlert("🎉 НОВЫЙ УРОВЕНЬ! Твой хомяк прокачался!");
            }

            // Анимация монетки
            let rect = document.getElementById('hamster').getBoundingClientRect();
            let coin = document.createElement('div');
            coin.className = 'coin-anim';
            coin.innerText = "+" + state.tapPower;
            coin.style.left = (e.touches[0].clientX - 10) + "px";
            coin.style.top = (e.touches[0].clientY - 20) + "px";
            document.body.appendChild(coin);
            setTimeout(() => coin.remove(), 800);

            updateUI();
        }, {passive: false});

        // Сохранение на сервер (каждые 3 секунды)
        setInterval(() => {
            fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid, data: state })
            });
        }, 3000);

        // Переключение вкладок
        function switchTab(tabId, el) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('screen-' + tabId).classList.add('active');
            el.classList.add('active');
        }

        // Приглашение друга
        function inviteFriend() {
            let refLink = "https://t.me/" + tg.initDataUnsafe.bot_username + "?start=" + uid;
            tg.openTelegramLink("https://t.me/share/url?url=" + refLink + "&text=Залетай в игру, там реально платят!");
        }

        // Покупка буста
        function buyBoost() {
            if(state.balance >= state.boostCost) {
                state.balance -= state.boostCost;
                state.tapPower += 1;
                state.boostCost = Math.floor(state.boostCost * 2.5); // Дорожает
                tg.showAlert("🚀 Буст куплен! Теперь за клик дают +" + state.tapPower);
                updateUI();
            } else {
                tg.showAlert("❌ Недостаточно монет!");
            }
        }
    </script>
</body>
</html>
"""

# ===== API ДЛЯ СОХРАНЕНИЯ ДАННЫХ =====
async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def handle_load(request):
    uid = request.query.get('user_id')
    if uid in users:
        return web.json_response(users[uid])
    return web.json_response({"balance": 0, "level": 1, "taps": 0, "tapsRequired": 100, "tapPower": 1, "friends": 0, "boostCost": 1000})

async def handle_save(request):
    data = await request.json()
    uid = str(data['user_id'])
    users[uid] = data['data']
    return web.json_response({"status": "ok"})

# ===== БОТ =====
@router.message(Command("start"))
async def cmd_start(message: Message, command: Command):
    # Логика реферальной ссылки (если перешли по ссылке друга)
    args = message.text.split()
    if len(args) > 1:
        inviter_id = args[1]
        if inviter_id in users and str(message.from_user.id) not in users:
            users[inviter_id]["balance"] += 25000
            users[inviter_id]["friends"] += 1
            await message.answer("🎁 Ты пришел по приглашению! Твой друг получил бонус.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐹 Играть", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Добро пожаловать в Hamster Mega! 🚀\nЖми кнопку ниже, чтобы начать зарабатывать миллионы.", reply_markup=kb)

async def main():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/load', handle_load)
    app.router.add_post('/api/save', handle_save)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port) 
    await site.start()

    dp.include_router(router)
    print(f"Сервер запущен на порту {port}!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
