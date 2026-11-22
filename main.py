import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# 👇 ВСТАВЬ СВОЙ НОВЫЙ ТОКЕН СЮДА
TOKEN = "9003918789:AAFQCOXzx9MsHuUOXPWlEf047N8w2I6h-Sw"
# 👇 ТВОЯ ССЫЛКА ИЗ RAILWAY (должна быть https://...)
WEBAPP_URL = "https://hambot-production.up.railway.app" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
users = {} 

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
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; user-select: none; -webkit-tap-highlight-color: transparent; }
        body { background-color: #121212; color: white; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
        
        /* Верхняя панель */
        .header { display: flex; justify-content: space-between; padding: 20px; background: rgba(0,0,0,0.3); border-bottom: 1px solid #2a2a2a; }
        .header div { font-size: 14px; font-weight: 600; color: #a0a0a0; }
        .header span { color: white; font-weight: 800; display: block; font-size: 18px; margin-top: 4px; }

        /* Экран */
        .screen { flex: 1; display: none; flex-direction: column; align-items: center; padding: 20px; position: relative; overflow-y: auto; }
        .screen.active { display: flex; }

        /* Кликер */
        .balance { font-size: 48px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 0 10px rgba(255,215,0,0.5); margin-top: 20px;}
        .sub-balance { font-size: 16px; color: #a0a0a0; margin-bottom: 30px; }
        
        .circle-container { position: relative; width: 260px; height: 260px; display: flex; justify-content: center; align-items: center; margin-top: 10px; }
        .glow-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: conic-gradient(from 0deg, #ffd700, #ff8c00, #ffd700); animation: spin 3s linear infinite; filter: blur(10px); opacity: 0.8; }
        
        /* Кнопка с хомяком */
        .hamster-btn { position: relative; width: 240px; height: 240px; border-radius: 50%; background: #1e1e1e; border: 4px solid #2a2a2a; display: flex; justify-content: center; align-items: center; font-size: 120px; cursor: pointer; transition: transform 0.1s; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); z-index: 2; }
        .hamster-btn:active { transform: scale(0.92); }
        
        /* Всплывающие монеты */
        .coin-anim { position: absolute; font-size: 24px; font-weight: 800; color: #ffd700; pointer-events: none; animation: floatUp 0.8s ease-out forwards; z-index: 10; text-shadow: 0 0 5px black; }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-100px) scale(1.5); } }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* Прогресс-бар */
        .progress-container { width: 90%; margin-top: 30px; }
        .progress-info { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 8px; }
        .progress-bg { width: 100%; height: 12px; background: #2a2a2a; border-radius: 6px; overflow: hidden; }
        .progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #ffd700, #ff8c00); border-radius: 6px; transition: width 0.3s; }

        /* Карточки (вкладки) */
        .menu { display: flex; flex-direction: column; width: 100%; gap: 15px; margin-top: 20px;}
        .card { background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 16px; padding: 20px; text-align: center; }
        .card h2 { font-size: 20px; margin-bottom: 10px; }
        .card p { font-size: 14px; color: #a0a0a0; margin-bottom: 15px; }
        .btn { background: #ffd700; color: black; font-weight: 800; border: none; padding: 15px 20px; border-radius: 12px; font-size: 16px; cursor: pointer; width: 100%; transition: 0.2s; }
        .btn:active { background: #ffb700; transform: scale(0.98); }
        .btn:disabled { background: #2a2a2a; color: #666; cursor: not-allowed; transform: none; }
        
        /* Ежедневный бонус */
        .bonus-box { font-size: 100px; margin: 10px 0; cursor: pointer; transition: transform 0.2s; }
        .bonus-box:active { transform: scale(1.1); }
        .timer-text { font-size: 14px; color: #ffd700; margin-top: 10px; font-weight: 600; }

        /* МАГАЗИН */
        .shop-item { display: flex; align-items: center; justify-content: space-between; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 12px; padding: 10px 15px; margin-bottom: 10px; }
        .shop-emoji { font-size: 40px; }
        .shop-info { flex: 1; margin-left: 15px; text-align: left; }
        .shop-info h3 { font-size: 16px; margin-bottom: 4px; }
        .shop-info p { font-size: 12px; color: #ffd700; font-weight: 800; }
        .buy-btn { width: auto; padding: 10px 15px; font-size: 14px; border-radius: 8px; }
        .equip-btn { background: #00b894; color: white; }
        .equipped-btn { background: #2a2a2a; color: #666; }

        /* Нижнее меню */
        .nav-bar { display: flex; justify-content: space-around; padding: 15px 5px; background: #1a1a1a; border-top: 1px solid #2a2a2a; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 10px; color: #666; cursor: pointer; transition: 0.2s; width: 20%; }
        .nav-item.active { color: #ffd700; }
        .nav-item span { font-size: 22px; margin-bottom: 4px; }
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

    <!-- Экран 2: Ежедневный бонус -->
    <div id="screen-games" class="screen">
        <div class="menu">
            <div class="card">
                <h2>🎁 Ежедневный подарок</h2>
                <p>Открывай раз в 24 часа и получай от 1 000 до 5 000 монет!</p>
                <div class="bonus-box" id="daily-box" onclick="openDailyBox()">🎁</div>
                <button class="btn" id="btn-daily" onclick="openDailyBox()">Открыть подарок</button>
                <p class="timer-text" id="timer-text"></p>
            </div>
        </div>
    </div>

    <!-- Экран 3: Магазин -->
    <div id="screen-shop" class="screen">
        <h2 style="margin-bottom: 15px; font-weight: 800;">Магазин скинов</h2>
        <div style="width: 100%;" id="shop-list">
            <!-- Сюда JS будет добавлять товары -->
        </div>
    </div>

    <!-- Экран 4: Друзья -->
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

    <!-- Экран 5: Бусты -->
    <div id="screen-boosts" class="screen">
        <div class="menu">
            <div class="card">
                <h2>🚀 Турбо-клик</h2>
                <p>Увеличивает монеты за клик на +1. (Цена: <span id="boost-cost">1000</span> монет)</p>
                <button class="btn" id="btn-boost" onclick="buyBoost()">Купить буст</button>
            </div>
        </div>
    </div>

    <!-- Нижнее меню -->
    <div class="nav-bar">
        <div class="nav-item active" onclick="switchTab('mine', this)"><span>🏠</span>Майнинг</div>
        <div class="nav-item" onclick="switchTab('games', this)"><span>🎁</span>Бонус</div>
        <div class="nav-item" onclick="switchTab('shop', this)"><span>🛒</span>Магазин</div>
        <div class="nav-item" onclick="switchTab('friends', this)"><span>👥</span>Друзья</div>
        <div class="nav-item" onclick="switchTab('boosts', this)"><span>🚀</span>Бусты</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        // Скины для магазина
        const skins = [
            { id: "default", name: "Обычный хомяк", emoji: "🐹", price: 0 },
            { id: "rich", name: "Богатый хомяк", emoji: "🤑", price: 50000 },
            { id: "ninja", name: "Хомяк-Ниндзя", emoji: "🥷", price: 500000 },
            { id: "king", name: "Король хомяков", emoji: "👑", price: 5000000 },
            { id: "cyborg", name: "Кибер-хомяк", emoji: "🤖", price: 100000000 }
        ];

        // Базовые эмодзи для уровней (если не надет скин)
        const levelEmojis = ["🐹", "🐭", "🦦", "🦫", "🐻", "🦁"];

        let state = {
            balance: 0,
            level: 1,
            taps: 0,
            tapsRequired: 100,
            tapPower: 1,
            friends: 0,
            boostCost: 1000,
            lastDaily: 0,
            inventory: ["default"], // Купленные скины
            equippedSkin: "default" // Надетый скин
        };

        let uid = tg.initDataUnsafe?.user?.id || 12345;

        // Загрузка данных
        fetch('/api/load?user_id=' + uid)
            .then(r => r.json())
            .then(data => {
                if(data && data.balance !== undefined) {
                    state = Object.assign(state, data);
                    // Защита для старых сохранений (если вдруг нет полей магазина)
                    if (!state.inventory) state.inventory = ["default"];
                    if (!state.equippedSkin) state.equippedSkin = "default";
                }
                updateUI();
            })
            .catch(e => console.log("Оффлайн режим"));

        // Обновление интерфейса
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

            // Установка хомяка (Если куплен скин - ставим его, иначе - по уровню)
            let activeEmoji = "🐹";
            if (state.equippedSkin && state.equippedSkin !== "default") {
                let skin = skins.find(s => s.id === state.equippedSkin);
                if (skin) activeEmoji = skin.emoji;
            } else {
                let idx = Math.min(state.level - 1, levelEmojis.length - 1);
                activeEmoji = levelEmojis[idx];
            }
            document.getElementById('hamster').innerText = activeEmoji;

            updateDailyUI();
            renderShop();
        }

        // Клик
        document.getElementById('click-area').addEventListener('touchstart', function(e) {
            e.preventDefault();
            state.balance += state.tapPower;
            state.taps += 1;
            
            if (state.taps >= state.tapsRequired) {
                state.taps = 0;
                state.level += 1;
                state.tapsRequired *= 10; 
                tg.showAlert("🎉 НОВЫЙ УРОВЕНЬ! Твой хомяк вырос!");
            }

            let coin = document.createElement('div');
            coin.className = 'coin-anim';
            coin.innerText = "+" + state.tapPower;
            coin.style.left = (e.touches[0].clientX - 10) + "px";
            coin.style.top = (e.touches[0].clientY - 20) + "px";
            document.body.appendChild(coin);
            setTimeout(() => coin.remove(), 800);

            updateUI();
        }, {passive: false});

        // СОХРАНЕНИЕ
        function saveGame() {
            fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid, data: state })
            });
        }
        setInterval(saveGame, 3000);

        // ВКЛАДКИ
        function switchTab(tabId, el) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('screen-' + tabId).classList.add('active');
            el.classList.add('active');
        }

        // ===== МАГАЗИН =====
        function renderShop() {
            let container = document.getElementById('shop-list');
            container.innerHTML = ""; // Очищаем

            skins.forEach(skin => {
                let owned = state.inventory.includes(skin.id);
                let equipped = state.equippedSkin === skin.id;
                
                let btnHtml = "";
                if (equipped) {
                    btnHtml = `<button class="btn buy-btn equipped-btn" disabled>Надет</button>`;
                } else if (owned) {
                    btnHtml = `<button class="btn buy-btn equip-btn" onclick="equipSkin('${skin.id}')">Надеть</button>`;
                } else {
                    btnHtml = `<button class="btn buy-btn" onclick="buySkin('${skin.id}', ${skin.price})">${skin.price.toLocaleString()} 💰</button>`;
                }

                let item = document.createElement('div');
                item.className = 'shop-item';
                item.innerHTML = `
                    <div class="shop-emoji">${skin.emoji}</div>
                    <div class="shop-info">
                        <h3>${skin.name}</h3>
                        <p>${owned ? "Куплено" : "Не куплено"}</p>
                    </div>
                    ${btnHtml}
                `;
                container.appendChild(item);
            });
        }

        function buySkin(id, price) {
            if (state.balance >= price) {
                state.balance -= price;
                state.inventory.push(id);
                state.equippedSkin = id; // Сразу надеваем при покупке
                tg.showAlert("🛍️ Покупка успешна! Скин надет.");
                updateUI();
                saveGame();
            } else {
                tg.showAlert("❌ Недостаточно монет для покупки!");
            }
        }

        function equipSkin(id) {
            state.equippedSkin = id;
            updateUI();
            saveGame();
            tg.showAlert("✅ Скин надет!");
        }

        // ===== ЕЖЕДНЕВНЫЙ БОНУС =====
        function updateDailyUI() {
            let now = Date.now();
            let cooldown = 24 * 60 * 60 * 1000; 
            let timePassed = now - state.lastDaily;
            
            let btn = document.getElementById('btn-daily');
            let timerText = document.getElementById('timer-text');
            let box = document.getElementById('daily-box');

            if (timePassed >= cooldown) {
                btn.disabled = false;
                btn.innerText = "Открыть подарок 🎁";
                timerText.innerText = "Подарок доступен!";
                timerText.style.color = "#ffd700";
                box.innerText = "🎁";
            } else {
                let remaining = cooldown - timePassed;
                let hours = Math.floor(remaining / (1000 * 60 * 60));
                let minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((remaining % (1000 * 60)) / 1000);
                
                btn.disabled = true;
                btn.innerText = "Уже открыто";
                timerText.innerText = `Следующий через: ${hours}ч ${minutes}м ${seconds}с`;
                timerText.style.color = "#a0a0a0";
                box.innerText = "🔒";
            }
        }
        setInterval(updateDailyUI, 1000);

        function openDailyBox() {
            let now = Date.now();
            let cooldown = 24 * 60 * 60 * 1000;
            
            if (now - state.lastDaily >= cooldown) {
                let reward = Math.floor(Math.random() * 4000) + 1000; 
                state.balance += reward;
                state.lastDaily = now;
                
                tg.showAlert(`🎉 Ура! Ты нашел ${reward} монет в подарке!`);
                updateUI();
                saveGame();
            } else {
                tg.showAlert("⏳ Ты уже открыл подарок сегодня. Приходи завтра!");
            }
        }

        // ПРИГЛАШЕНИЕ
        function inviteFriend() {
            let refLink = "https://t.me/" + tg.initDataUnsafe.bot_username + "?start=" + uid;
            tg.openTelegramLink("https://t.me/share/url?url=" + refLink + "&text=Залетай в игру, там реально платят!");
        }

        // БУСТ
        function buyBoost() {
            if(state.balance >= state.boostCost) {
                state.balance -= state.boostCost;
                state.tapPower += 1;
                state.boostCost = Math.floor(state.boostCost * 2.5);
                tg.showAlert("🚀 Буст куплен! Теперь за клик дают +" + state.tapPower);
                updateUI();
                saveGame();
            } else {
                tg.showAlert("❌ Недостаточно монет!");
            }
        }
    </script>
</body>
</html>
"""

# ===== API =====
async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def handle_load(request):
    uid = request.query.get('user_id')
    if uid in users:
        return web.json_response(users[uid])
    return web.json_response({
        "balance": 0, "level": 1, "taps": 0, 
        "tapsRequired": 100, "tapPower": 1, 
        "friends": 0, "boostCost": 1000, 
        "lastDaily": 0, "inventory": ["default"], "equippedSkin": "default"
    })

async def handle_save(request):
    data = await request.json()
    uid = str(data['user_id'])
    users[uid] = data['data']
    return web.json_response({"status": "ok"})

# ===== БОТ =====
@router.message(Command("start"))
async def cmd_start(message: Message):
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
