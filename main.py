import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# 👇 ТВОЙ ТОКЕН (СОВЕТУЮ ПОМЕНЯТЬ В BOTFATHER!)
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
        
        .header { display: flex; justify-content: space-between; padding: 15px 20px; background: rgba(0,0,0,0.5); border-bottom: 1px solid #2a2a2a; }
        .header div { font-size: 12px; font-weight: 600; color: #a0a0a0; }
        .header span { color: white; font-weight: 800; display: block; font-size: 16px; margin-top: 4px; }

        .screen { flex: 1; display: none; flex-direction: column; align-items: center; padding: 20px 15px; position: relative; overflow-y: auto; }
        .screen.active { display: flex; }

        .balance { font-size: 48px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 0 10px rgba(255,215,0,0.5); margin-top: 10px; cursor: pointer; }
        .sub-balance { font-size: 14px; color: #a0a0a0; margin-bottom: 20px; }
        
        .circle-container { position: relative; width: 240px; height: 240px; display: flex; justify-content: center; align-items: center; }
        .glow-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; background: conic-gradient(from 0deg, #ffd700, #ff8c00, #ffd700); animation: spin 3s linear infinite; filter: blur(10px); opacity: 0.8; }
        .hamster-btn { position: relative; width: 220px; height: 220px; border-radius: 50%; background: #1e1e1e; border: 4px solid #2a2a2a; display: flex; justify-content: center; align-items: center; font-size: 110px; cursor: pointer; transition: transform 0.1s; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); z-index: 2; }
        .hamster-btn:active { transform: scale(0.92); }
        
        .coin-anim { position: absolute; font-size: 24px; font-weight: 800; color: #ffd700; pointer-events: none; animation: floatUp 0.8s ease-out forwards; z-index: 10; text-shadow: 0 0 5px black; }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-100px) scale(1.5); } }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        .progress-container { width: 90%; margin-top: 30px; }
        .progress-info { display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 8px; }
        .progress-bg { width: 100%; height: 10px; background: #2a2a2a; border-radius: 5px; overflow: hidden; }
        .progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #ffd700, #ff8c00); border-radius: 5px; transition: width 0.3s; }

        .menu { display: flex; flex-direction: column; width: 100%; gap: 15px; }
        .card { background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 16px; padding: 15px; text-align: center; }
        .card h2 { font-size: 18px; margin-bottom: 8px; }
        .card p { font-size: 13px; color: #a0a0a0; margin-bottom: 12px; }
        .btn { background: #ffd700; color: black; font-weight: 800; border: none; padding: 12px 15px; border-radius: 10px; font-size: 15px; cursor: pointer; width: 100%; transition: 0.2s; }
        .btn:active { background: #ffb700; transform: scale(0.98); }
        .btn:disabled { background: #2a2a2a; color: #666; cursor: not-allowed; transform: none; }

        .wheel-wrapper { position: relative; width: 220px; height: 220px; margin: 15px auto; }
        .wheel { width: 100%; height: 100%; border-radius: 50%; border: 5px solid #ffd700; background: conic-gradient(#ff4757 0 60deg, #2ed573 60deg 120deg, #1e90ff 120deg 180deg, #ffa502 180deg 240deg, #9b59b6 240deg 300deg, #ff4757 300deg 360deg); transition: transform 4s cubic-bezier(0.25, 0.1, 0.25, 1); }
        .wheel-pointer { position: absolute; top: -15px; left: 50%; transform: translateX(-50%); font-size: 30px; z-index: 10; }

        .task-item { display: flex; justify-content: space-between; align-items: center; background: #1e1e1e; padding: 12px; border-radius: 10px; margin-bottom: 8px; width: 100%; }
        .task-info { text-align: left; }
        .task-info h4 { font-size: 14px; margin-bottom: 2px; }
        .task-info p { font-size: 11px; color: #888; }

        .shop-tabs { display: flex; width: 100%; margin-bottom: 15px; gap: 5px; }
        .shop-tab { flex: 1; padding: 10px; background: #1e1e1e; color: #888; border: none; border-radius: 8px; font-weight: 600; }
        .shop-tab.active { background: #ffd700; color: black; }
        .shop-content { width: 100%; display: none; flex-direction: column; gap: 10px; }
        .shop-content.active { display: flex; }
        .shop-item { display: flex; align-items: center; justify-content: space-between; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 12px; padding: 10px; }
        .shop-emoji { font-size: 35px; width: 50px; text-align: center; }
        .shop-info { flex: 1; margin-left: 10px; text-align: left; }
        .shop-info h3 { font-size: 14px; margin-bottom: 3px; }
        .shop-info p { font-size: 12px; color: #ffd700; font-weight: 800; }
        .buy-btn { width: auto; padding: 8px 12px; font-size: 12px; border-radius: 6px; }
        .equip-btn { background: #00b894; color: white; }

        .nav-bar { display: flex; justify-content: space-around; padding: 10px 2px; background: #1a1a1a; border-top: 1px solid #2a2a2a; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 9px; color: #666; cursor: pointer; transition: 0.2s; width: 20%; }
        .nav-item.active { color: #ffd700; }
        .nav-item span { font-size: 20px; margin-bottom: 2px; }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 100; justify-content: center; align-items: center; flex-direction: column; }
        .modal input { padding: 12px; font-size: 18px; border-radius: 8px; border: 2px solid #ffd700; text-align: center; background: #1a1a1a; color: white; width: 180px; margin-bottom: 15px; }
    </style>
</head>
<body>

    <div class="header">
        <div>Уровень <span id="top-level">1</span></div>
        <div>Пассив: <span id="top-passive">0</span>/сек</div>
        <div>Монеты <span id="top-balance">0</span></div>
    </div>

    <!-- 1. Кликер -->
    <div id="screen-mine" class="screen active">
        <div class="balance" id="balance" onclick="secretClick()">0</div>
        <div class="sub-balance">монет</div>
        <div class="circle-container" id="click-area">
            <div class="glow-ring"></div>
            <div class="hamster-btn" id="hamster">🐹</div>
        </div>
        <div class="progress-container">
            <div class="progress-info">
                <span>До след. уровня</span>
                <span id="progress-text">0 / 100</span>
            </div>
            <div class="progress-bg"><div class="progress-fill" id="progress-bar"></div></div>
        </div>
    </div>

    <!-- 2. Рулетка -->
    <div id="screen-games" class="screen">
        <h2 style="margin-bottom: 5px;">🎰 Колесо Фортуны</h2>
        <p style="font-size: 12px; color: #888; margin-bottom: 15px;">Крути за 1000 монет и выигрывай до 50 000!</p>
        <div class="wheel-wrapper">
            <div class="wheel-pointer">🔻</div>
            <div class="wheel" id="wheel"></div>
        </div>
        <button class="btn" style="margin-top: 20px;" id="btn-spin" onclick="spinWheel()">Крутить (1000 💰)</button>
    </div>

    <!-- 3. Задания -->
    <div id="screen-tasks" class="screen">
        <h2 style="margin-bottom: 15px;">📋 Задания и Бонус</h2>
        <div class="card" style="width: 100%; margin-bottom: 15px;">
            <h2>🎁 Ежедневный подарок</h2>
            <div style="font-size: 50px; margin: 10px 0; cursor: pointer;" id="daily-box" onclick="openDailyBox()">🎁</div>
            <button class="btn" id="btn-daily" onclick="openDailyBox()">Открыть</button>
            <p class="timer-text" id="timer-text" style="font-size: 12px; margin-top: 8px; color: #ffd700;"></p>
        </div>
        <div style="width: 100%; text-align: left;">
            <h3 style="font-size: 14px; margin-bottom: 10px; color: #888;">Ежедневные задания:</h3>
            <div id="tasks-list"></div>
        </div>
    </div>

    <!-- 4. Магазин -->
    <div id="screen-shop" class="screen">
        <div class="shop-tabs">
            <button class="shop-tab active" onclick="switchShopTab('skins', this)">Скины</button>
            <button class="shop-tab" onclick="switchShopTab('boosts', this)">Бусты</button>
            <button class="shop-tab" onclick="switchShopTab('cards', this)">Карты</button>
        </div>
        
        <div id="shop-skins" class="shop-content active"></div>
        
        <div id="shop-boosts" class="shop-content">
            <div class="card">
                <h2>🚀 Турбо-клик</h2>
                <p>+1 к силе клика. (Цена: <span id="boost-cost">1000</span>)</p>
                <button class="btn" onclick="buyBoost()">Купить</button>
            </div>
        </div>

        <div id="shop-cards" class="shop-content"></div>
    </div>

    <!-- 5. Друзья -->
    <div id="screen-friends" class="screen">
        <div class="menu">
            <div class="card">
                <h2>👥 Приглашай друзей</h2>
                <p>За друга ты получаешь <b>+50,000 монет</b> и +5 к пассиву!</p>
                <button class="btn" onclick="inviteFriend()">Пригласить друга</button>
            </div>
            <div class="card">
                <h2>Твои рефералы</h2>
                <p>Приглашено: <b id="friends-count">0</b></p>
            </div>
        </div>
    </div>

    <!-- АДМИНКА -->
    <div id="screen-admin" class="screen">
        <h2 style="margin-bottom: 20px; color: #ffd700;">🔧 Админ-панель</h2>
        <div class="menu">
            <button class="btn" onclick="adminAddCoins()">💰 Выдать 1 000 000 монет</button>
            <button class="btn" onclick="adminUnlockSkins()">👑 Открыть все скины</button>
            <button class="btn" onclick="adminMaxPower()">⚡️ +100 к силе клика</button>
            <button class="btn" onclick="adminMaxPassive()">📈 +100 к пассиву</button>
            <button class="btn" onclick="adminResetTasks()">🔄 Сбросить задания</button>
            <button class="btn" style="background:#e74c3c; color:white;" onclick="adminReset()">🗑 Полный сброс</button>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-item active" onclick="switchTab('mine', this)"><span>🏠</span>Майнинг</div>
        <div class="nav-item" onclick="switchTab('games', this)"><span>🎰</span>Рулетка</div>
        <div class="nav-item" onclick="switchTab('tasks', this)"><span>📋</span>Таски</div>
        <div class="nav-item" onclick="switchTab('shop', this)"><span>🛒</span>Магазин</div>
        <div class="nav-item" onclick="switchTab('friends', this)"><span>👥</span>Друзья</div>
        <div class="nav-item" id="nav-admin" style="display:none;" onclick="switchTab('admin', this)"><span>🔧</span>Админ</div>
    </div>

    <div id="secret-modal" class="modal">
        <h2 style="margin-bottom: 20px;">Секретный код</h2>
        <input type="password" id="secret-input" placeholder="******">
        <button class="btn" style="width: 180px;" onclick="checkSecret()">Войти</button>
        <button class="btn" style="width: 180px; background: #2a2a2a; color: white; margin-top: 10px;" onclick="closeSecretModal()">Отмена</button>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        const skins = [
            { id: "default", name: "Обычный хомяк", emoji: "🐹", price: 0 },
            { id: "rich", name: "Богатый хомяк", emoji: "🤑", price: 50000 },
            { id: "ninja", name: "Хомяк-Ниндзя", emoji: "🥷", price: 500000 },
            { id: "king", name: "Король хомяков", emoji: "👑", price: 5000000 },
            { id: "cyborg", name: "Кибер-хомяк", emoji: "🤖", price: 100000000 }
        ];
        
        const cards = [
            { id: "card1", name: "Ферма", emoji: "🌾", price: 100000, income: 5 },
            { id: "card2", name: "Завод", emoji: "🏭", price: 500000, income: 50 },
            { id: "card3", name: "Крипто-биржа", emoji: "🪙", price: 2000000, income: 300 },
            { id: "card4", name: "Космическая станция", emoji: "🚀", price: 10000000, income: 2000 }
        ];

        const tasksData = [
            { id: "t1", name: "Тапнуть 1000 раз", goal: 1000, type: "totalTaps", reward: 10000 },
            { id: "t2", name: "Купить 3 буста", goal: 3, type: "boostsBought", reward: 50000 },
            { id: "t3", name: "Пригласить друга", goal: 1, type: "friends", reward: 100000 }
        ];

        const levelEmojis = ["🐹", "🐭", "🦦", "🦫", "🐻", "🦁"];

        let state = {
            balance: 0, level: 1, taps: 0, tapsRequired: 100, tapPower: 1, 
            friends: 0, boostCost: 1000, lastDaily: 0,
            inventory: ["default"], equippedSkin: "default",
            lastLogin: Date.now(), passiveIncome: 0, 
            cardsOwned: [], claimedTasks: [],
            totalTaps: 0, boostsBought: 0
        };

        let uid = tg.initDataUnsafe?.user?.id || 12345;
        let secretTapCount = 0;
        let secretTapTimer = null;
        let isWheelSpinning = false;

        fetch('/api/load?user_id=' + uid)
            .then(r => r.json())
            .then(data => {
                if(data && data.balance !== undefined) {
                    state = Object.assign(state, data);
                    if (!state.inventory) state.inventory = ["default"];
                    if (!state.equippedSkin) state.equippedSkin = "default";
                    if (!state.claimedTasks) state.claimedTasks = [];
                    if (!state.cardsOwned) state.cardsOwned = [];
                }
                
                let now = Date.now();
                let offlineSeconds = Math.floor((now - state.lastLogin) / 1000);
                if (offlineSeconds > 10 && state.passiveIncome > 0) {
                    let earned = offlineSeconds * state.passiveIncome;
                    state.balance += earned;
                    setTimeout(() => tg.showAlert(`💤 Пока тебя не было, хомяки заработали: ${earned.toLocaleString()} 💰`), 1000);
                }
                state.lastLogin = now;

                updateUI();
                startPassiveIncome();
            })
            .catch(e => { console.log(e); updateUI(); });

        function startPassiveIncome() {
            setInterval(() => {
                if (state.passiveIncome > 0) {
                    state.balance += state.passiveIncome;
                    document.getElementById('balance').innerText = state.balance.toLocaleString();
                    document.getElementById('top-balance').innerText = state.balance.toLocaleString();
                }
            }, 1000);
        }

        function updateUI() {
            document.getElementById('balance').innerText = state.balance.toLocaleString();
            document.getElementById('top-balance').innerText = state.balance.toLocaleString();
            document.getElementById('top-level').innerText = state.level;
            document.getElementById('top-passive').innerText = state.passiveIncome.toLocaleString();
            document.getElementById('friends-count').innerText = state.friends;
            document.getElementById('boost-cost').innerText = state.boostCost.toLocaleString();
            document.getElementById('progress-text').innerText = state.taps + " / " + state.tapsRequired;
            
            let percent = (state.taps / state.tapsRequired) * 100;
            if(percent > 100) percent = 100;
            document.getElementById('progress-bar').style.width = percent + "%";

            let activeEmoji = "🐹";
            if (state.equippedSkin && state.equippedSkin !== "default") {
                let skin = skins.find(s => s.id === state.equippedSkin);
                if (skin) activeEmoji = skin.emoji;
            } else {
                activeEmoji = levelEmojis[Math.min(state.level - 1, levelEmojis.length - 1)];
            }
            document.getElementById('hamster').innerText = activeEmoji;

            updateDailyUI();
            renderTasks();
            renderShopSkins();
            renderShopCards();
        }

        document.getElementById('click-area').addEventListener('touchstart', function(e) {
            e.preventDefault();
            state.balance += state.tapPower;
            state.taps += 1;
            state.totalTaps += 1;
            
            if (state.taps >= state.tapsRequired) {
                state.taps = 0;
                state.level += 1;
                state.tapsRequired *= 10; 
                tg.showAlert("🎉 НОВЫЙ УРОВЕНЬ!");
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

        function saveGame() {
            state.lastLogin = Date.now();
            fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid, data: state })
            });
        }
        setInterval(saveGame, 5000);

        function switchTab(tabId, el) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('screen-' + tabId).classList.add('active');
            el.classList.add('active');
        }

        // ===== КОЛЕСО ФОРТУНЫ =====
        function spinWheel() {
            if (isWheelSpinning) return;
            if (state.balance < 1000) return tg.showAlert("❌ Нужно 1000 монет!");
            
            state.balance -= 1000;
            updateUI();
            isWheelSpinning = true;
            document.getElementById('btn-spin').innerText = "Крутим...";
            
            const wheel = document.getElementById('wheel');
            const randomDeg = Math.floor(Math.random() * 360) + 720; 
            wheel.style.transform = `rotate(${randomDeg}deg)`;

            setTimeout(() => {
                let prize = 0;
                let deg = randomDeg % 360;
                
                if (deg >= 0 && deg < 60) prize = 1000;
                else if (deg >= 60 && deg < 120) prize = 0;
                else if (deg >= 120 && deg < 180) prize = 5000;
                else if (deg >= 180 && deg < 240) prize = 100;
                else if (deg >= 240 && deg < 300) prize = 50000;
                else prize = 500;

                state.balance += prize;
                isWheelSpinning = false;
                document.getElementById('btn-spin').innerText = "Крутить (1000 💰)";
                
                if (prize > 0) tg.showAlert(`🎉 Ты выиграл ${prize.toLocaleString()} монет!`);
                else tg.showAlert(`😢 Пусто! Попробуй еще раз.`);
                
                updateUI();
                saveGame();
            }, 4200);
        }

        // ===== ЗАДАНИЯ =====
        function renderTasks() {
            let list = document.getElementById('tasks-list');
            list.innerHTML = "";
            tasksData.forEach(t => {
                let current = state[t.type] || 0;
                let isClaimed = state.claimedTasks.includes(t.id);
                let isDone = current >= t.goal;

                let btnHtml = "";
                if (isClaimed) btnHtml = `<span style="color: #2ed573; font-weight: bold;">✅ Получено</span>`;
                else if (isDone) btnHtml = `<button class="btn buy-btn" onclick="claimTask('${t.id}')">Забрать</button>`;
                else btnHtml = `<span style="color: #666; font-size: 12px;">В процессе</span>`;

                let item = document.createElement('div');
                item.className = 'task-item';
                item.innerHTML = `
                    <div class="task-info">
                        <h4>${t.name}</h4>
                        <p>Награда: ${t.reward.toLocaleString()} 💰</p>
                        <p>Прогресс: ${Math.min(current, t.goal)} / ${t.goal}</p>
                    </div>
                    ${btnHtml}
                `;
                list.appendChild(item);
            });
        }

        function claimTask(id) {
            let t = tasksData.find(x => x.id === id);
            if (t && !state.claimedTasks.includes(id)) {
                state.claimedTasks.push(id);
                state.balance += t.reward;
                tg.showAlert(`✅ Награда ${t.reward.toLocaleString()} монет получена!`);
                updateUI();
                saveGame();
            }
        }

        function updateDailyUI() {
            let now = Date.now();
            let cooldown = 24 * 60 * 60 * 1000; 
            let timePassed = now - state.lastDaily;
            let btn = document.getElementById('btn-daily');
            let timerText = document.getElementById('timer-text');
            
            if (timePassed >= cooldown) {
                btn.disabled = false;
                btn.innerText = "Открыть подарок 🎁";
                timerText.innerText = "Подарок доступен!";
            } else {
                let remaining = cooldown - timePassed;
                let hours = Math.floor(remaining / (1000 * 60 * 60));
                let minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((remaining % (1000 * 60)) / 1000);
                btn.disabled = true;
                btn.innerText = "Уже открыто";
                timerText.innerText = `Следующий через: ${hours}ч ${minutes}м ${seconds}с`;
            }
        }
        setInterval(updateDailyUI, 1000);

        function openDailyBox() {
            let now = Date.now();
            if (now - state.lastDaily >= 24 * 60 * 60 * 1000) {
                let reward = Math.floor(Math.random() * 9000) + 1000; 
                state.balance += reward;
                state.lastDaily = now;
                tg.showAlert(`🎁 Ты нашел ${reward.toLocaleString()} монет!`);
                updateUI();
                saveGame();
            }
        }

        // ===== МАГАЗИН =====
        function switchShopTab(tab, el) {
            document.querySelectorAll('.shop-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.shop-content').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('shop-' + tab).classList.add('active');
        }

        function renderShopSkins() {
            let container = document.getElementById('shop-skins');
            container.innerHTML = "";
            skins.forEach(skin => {
                let owned = state.inventory.includes(skin.id);
                let equipped = state.equippedSkin === skin.id;
                let btnHtml = "";
                
                if (equipped) btnHtml = `<button class="btn buy-btn" disabled style="background:#2a2a2a; color:#666;">Надет</button>`;
                else if (owned) btnHtml = `<button class="btn buy-btn equip-btn" onclick="equipSkin('${skin.id}')">Надеть</button>`;
                else btnHtml = `<button class="btn buy-btn" onclick="buySkin('${skin.id}', ${skin.price})">${skin.price.toLocaleString()} 💰</button>`;

                let item = document.createElement('div');
                item.className = 'shop-item';
                item.innerHTML = `
                    <div class="shop-emoji">${skin.emoji}</div>
                    <div class="shop-info"><h3>${skin.name}</h3><p>${owned ? "Куплено" : "Не куплено"}</p></div>
                    ${btnHtml}
                `;
                container.appendChild(item);
            });
        }

        function buySkin(id, price) {
            if (state.balance >= price) {
                state.balance -= price;
                state.inventory.push(id);
                state.equippedSkin = id;
                tg.showAlert("🛍️ Скин куплен и надет!");
                updateUI(); saveGame();
            } else tg.showAlert("❌ Недостаточно монет!");
        }

        function equipSkin(id) {
            state.equippedSkin = id;
            updateUI(); saveGame();
        }

        function renderShopCards() {
            let container = document.getElementById('shop-cards');
            container.innerHTML = "";
            cards.forEach(card => {
                let owned = state.cardsOwned.includes(card.id);
                let btnHtml = owned 
                    ? `<button class="btn buy-btn" disabled style="background:#2a2a2a; color:#666;">Куплено</button>`
                    : `<button class="btn buy-btn" onclick="buyCard('${card.id}', ${card.price}, ${card.income})">${card.price.toLocaleString()} 💰</button>`;

                let item = document.createElement('div');
                item.className = 'shop-item';
                item.innerHTML = `
                    <div class="shop-emoji">${card.emoji}</div>
                    <div class="shop-info">
                        <h3>${card.name}</h3>
                        <p>+${card.income.toLocaleString()} 💰/сек</p>
                    </div>
                    ${btnHtml}
                `;
                container.appendChild(item);
            });
        }

        function buyCard(id, price, income) {
            if (state.balance >= price) {
                state.balance -= price;
                state.cardsOwned.push(id);
                state.passiveIncome += income;
                tg.showAlert(`🏭 Куплено! Теперь пассив: +${state.passiveIncome.toLocaleString()}/сек`);
                updateUI(); saveGame();
            } else tg.showAlert("❌ Недостаточно монет!");
        }

        function buyBoost() {
            if(state.balance >= state.boostCost) {
                state.balance -= state.boostCost;
                state.tapPower += 1;
                state.boostsBought += 1;
                state.boostCost = Math.floor(state.boostCost * 2.5);
                updateUI(); saveGame();
            } else tg.showAlert("❌ Недостаточно монет!");
        }

        // ===== СЕКРЕТНАЯ АДМИНКА =====
        function secretClick() {
            secretTapCount++;
            clearTimeout(secretTapTimer);
            if (secretTapCount >= 5) {
                document.getElementById('secret-modal').style.display = 'flex';
                secretTapCount = 0;
            } else {
                secretTapTimer = setTimeout(() => { secretTapCount = 0; }, 1500);
            }
        }

        function checkSecret() {
            let code = document.getElementById('secret-input').value;
            if (code === "505050") {
                document.getElementById('nav-admin').style.display = 'flex';
                closeSecretModal();
                tg.showAlert("✅ Доступ разрешен!");
            } else {
                tg.showAlert("❌ Неверный код!");
            }
            document.getElementById('secret-input').value = "";
        }

        function closeSecretModal() { document.getElementById('secret-modal').style.display = 'none'; }

        function adminAddCoins() { state.balance += 1000000; updateUI(); saveGame(); }
        function adminUnlockSkins() { skins.forEach(s => { if (!state.inventory.includes(s.id)) state.inventory.push(s.id); }); updateUI(); saveGame(); tg.showAlert("👑 Все скины открыты!"); }
        function adminMaxPower() { state.tapPower += 100; updateUI(); saveGame(); }
        function adminMaxPassive() { state.passiveIncome += 100; updateUI(); saveGame(); }
        function adminResetTasks() { state.claimedTasks = []; updateUI(); saveGame(); tg.showAlert("🔄 Задания сброшены!"); }
        
        function adminReset() {
            state = { balance: 0, level: 1, taps: 0, tapsRequired: 100, tapPower: 1, friends: 0, boostCost: 1000, lastDaily: 0, inventory: ["default"], equippedSkin: "default", lastLogin: Date.now(), passiveIncome: 0, cardsOwned: [], claimedTasks: [], totalTaps: 0, boostsBought: 0 };
            updateUI(); saveGame(); tg.showAlert("🗑 Аккаунт сброшен!");
        }

        function inviteFriend() {
            let refLink = "https://t.me/" + tg.initDataUnsafe.bot_username + "?start=" + uid;
            tg.openTelegramLink("https://t.me/share/url?url=" + refLink + "&text=Залетай в игру, там реально платят!");
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
        "lastDaily": 0, "inventory": ["default"], "equippedSkin": "default",
        "lastLogin": 0, "passiveIncome": 0, "cardsOwned": [], "claimedTasks": [],
        "totalTaps": 0, "boostsBought": 0
    })

async def handle_save(request):
    data = await request.json()
    uid = str(data['user_id'])
    users[uid] = data['data']
    return web.json_response({"status": "ok"})

# ===== БОТ =====
@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐹 Играть", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Добро пожаловать в Hamster Mega! 🚀\nЖми кнопку ниже, чтобы начать.", reply_markup=kb)

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
