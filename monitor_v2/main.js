function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Утилита для вывода статусов
 */
class Logger {
    constructor(elementId) {
        this.el = document.getElementById(elementId);
    }
    info(msg) { this.el.textContent = msg; this.el.style.color = "#888"; }
    success(msg) { this.el.textContent = msg; this.el.style.color = "#4caf50"; }
    error(msg) { this.el.textContent = msg; this.el.style.color = "#f44336"; }
}

/**
 * Компонент Карточки Игрока
 */
class UserCard {
    constructor(containerId) {
        this.el = document.getElementById(containerId);
        this.ui = {
            name: this.el.querySelector('#userName'),
            id: this.el.querySelector('#userId'),
            money: this.el.querySelector('#userMoney'),
            rawBlock: this.el.querySelector('#userRawBlock'),
            toggleJsonBtn: this.el.querySelector('#toggleJsonBtn')
        };
        this.isJsonVisible = false;
        this._initEvents();
    }

    _initEvents() {
        this.ui.toggleJsonBtn.onclick = () => this.toggleJson();
    }

    toggleJson() {
        this.isJsonVisible = !this.isJsonVisible;
        if (this.isJsonVisible) {
            this.ui.rawBlock.classList.add('active');
            this.ui.toggleJsonBtn.textContent = 'Скрыть JSON';
        } else {
            this.ui.rawBlock.classList.remove('active');
            this.ui.toggleJsonBtn.textContent = 'JSON';
        }
    }

    update(userData, rawJson) {
        if (this.el.style.opacity !== "1") {
            this.el.style.opacity = "1";
        }
        this.ui.name.textContent = userData.name;
        this.ui.id.textContent = `ID: ${userData.id}`;
        this.ui.money.textContent = userData.money.toLocaleString();
        this.ui.rawBlock.textContent = rawJson;
    }
}

/**
 * Компонент Панели Команд
 */
class CommandPanel {
    constructor(logger) {
        this.input = document.getElementById('cmdInput');
        this.btn = document.getElementById('sendBtn');
        this.logger = logger;
        this.ws = null;

        this.btn.onclick = () => this.send();
    }

    setInitialTemplate(fleetId) {
        if (!this.input.value) {
            this.input.value = `{"action": "act_name", "params": {"fleet_id": ${fleetId}}}`;
        }
    }

    setSocket(ws) {
        this.ws = ws;
        this.btn.disabled = !ws || ws.readyState !== WebSocket.OPEN;
    }

    send() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.logger.error("Ошибка: Нет соединения с сервером");
            return;
        }

        let rawValue = this.input.value.replace(/\/\/.*|\/\*[\s\S]*?\*\//g, "");
        try {
            JSON.parse(rawValue);
            this.ws.send(rawValue);
            this.logger.info(`[${new Date().toLocaleTimeString()}] Отправлено!`);
        } catch (e) {
            this.logger.error(`Ошибка: Невалидный JSON`);
        }
    }
}

/**
 * Компонент Авторизации
 */
class AuthPanel {
    constructor(logger, onLoginSuccess) {
        this.emailInput = document.getElementById('emailInput');
        this.passwordInput = document.getElementById('passwordInput');
        this.btn = document.getElementById('loginBtn');
        
        this.logger = logger;
        this.onLoginSuccess = onLoginSuccess;

        this.btn.onclick = () => this.login();
    }

    async login() {
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;

        if (!email || !password) {
            alert("Пожалуйста, заполните Email и Пароль!");
            return;
        }

        this.btn.disabled = true;
        this.btn.textContent = "Вход...";
        this.logger.info("Выполняется запрос авторизации...");

        try {
            const response = await fetch('http://localhost:4000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

            const data = await response.json();
            
            if (data.access_token && data.access_token.token) {
                this.logger.success(`Успешно авторизован как: ${data.user.name}`);
                if (this.onLoginSuccess) this.onLoginSuccess(data.access_token.token);
            } else {
                throw new Error("Не удалось извлечь токен из ответа.");
            }
        } catch (error) {
            console.error("Ошибка авторизации:", error);
            this.logger.error(`Ошибка входа: ${error.message}`);
        } finally {
            this.btn.disabled = false;
            this.btn.textContent = "Войти";
        }
    }
}

/**
 * Компонент Карточки Флотилии
 */
class FleetCard {
    constructor(containerId, onShipSelect) {
        this.el = document.getElementById(containerId);
        this.onShipSelect = onShipSelect; // сохраняем callback
        this.ui = {
            name: this.el.querySelector('#fleetName'),
            id: this.el.querySelector('#fleetId'),
            pos: this.el.querySelector('#fleetPos'),
            speed: this.el.querySelector('#fleetSpeed'),
            state: this.el.querySelector('#fleetState'),
            attached: this.el.querySelector('#fleetAttached'),
            command: this.el.querySelector('#fleetCommand'),
            shipsContainer: this.el.querySelector('#shipsContainer'),
            rawBlock: this.el.querySelector('#fleetRawBlock'),
            toggleJsonBtn: this.el.querySelector('#toggleFleetJsonBtn')
        };

        this.movingStates = {
            1: "Ожидание",
            2: "Движение",
            3: "Пришвартован",
            4: "Маневрирует",
            5: "Рыбачит"
        };

        this.isJsonVisible = false;
        this._initEvents();
    }

    _initEvents() {
        this.ui.toggleJsonBtn.onclick = () => this.toggleJson();
    }

    toggleJson() {
        this.isJsonVisible = !this.isJsonVisible;
        if (this.isJsonVisible) {
            this.ui.rawBlock.classList.add('active');
            this.ui.toggleJsonBtn.textContent = 'Скрыть JSON';
        } else {
            this.ui.rawBlock.classList.remove('active');
            this.ui.toggleJsonBtn.textContent = 'JSON';
        }
    }

    update(fleetData, rawJson) {
        if (this.el.style.opacity !== "1") {
            this.el.style.opacity = "1";
        }

        // 1. Обновляем основные текстовые поля флотилии
        this.ui.name.textContent = fleetData.name;
        this.ui.id.textContent = `ID: ${fleetData.id}`;
        this.ui.pos.textContent = `X: ${fleetData.position.x.toFixed(2)}, Y: ${fleetData.position.y.toFixed(2)}`;
        this.ui.speed.textContent = fleetData.max_speed.toFixed(1);
        this.ui.state.textContent = this.movingStates[fleetData.moving_state] || `Неизвестно (${fleetData.moving_state})`;
        
        // Обработка пришвартованности
        if (fleetData.attached_to_id) {
            this.ui.attached.textContent = `ID ${fleetData.attached_to_id} (Тип: ${fleetData.attached_to_type})`;
        } else {
            this.ui.attached.textContent = "Нет";
        }

        // Обработка команды
        this.ui.command.textContent = fleetData.command ? JSON.stringify(fleetData.command, null, 2) : "null";
        
        // Системный сырой JSON
        this.ui.rawBlock.textContent = rawJson;

        // 2. Обновляем список кораблей (перерисовываем только внутренности контейнера кораблей)
        this.updateShips(fleetData.ships);
    }

    updateShips(ships) {
        if (!ships || ships.length === 0) {
            this.ui.shipsContainer.innerHTML = '<div style="color: #666; font-style: italic;">Корабли отсутствуют</div>';
            return;
        }

        let html = '';
        ships.forEach(ship => {
            // Добавляем data-id для последующей идентификации клика
            html += `
                <div class="ship-card" data-id="${ship.id}">
                    <span class="ship-name">🚢 ${escapeHtml(ship.name)} (${ship.id})</span>
                    <span class="ship-meta">👥 Экипаж: ${ship.crew}</span>
                    <span class="ship-meta">⚡ ${ship.max_speed.toFixed(1)}</span>
                </div>
            `;
        });
        this.ui.shipsContainer.innerHTML = html;
        
        // Вешаем клики на новые элементы
        this._bindShipClicks();
    }

    _bindShipClicks() {
        const cards = this.ui.shipsContainer.querySelectorAll('.ship-card');
        cards.forEach(card => {
            card.onclick = () => {
                const shipId = parseInt(card.getAttribute('data-id'), 10);
                if (this.onShipSelect && !isNaN(shipId)) {
                    this.onShipSelect(shipId);
                }
            };
        });
    }
}

/**
 * Компонент Детальной Карточки Корабля
 */
class ShipDetailCard {
    constructor(containerId) {
        this.el = document.getElementById(containerId);
        this.ui = {
            name: this.el.querySelector('#shipDetailName'),
            id: this.el.querySelector('#shipDetailId'),
            crew: this.el.querySelector('#shipDetailCrew'),
            hp: this.el.querySelector('#shipDetailHp'),
            speed: this.el.querySelector('#shipDetailSpeed'),
            hunger: this.el.querySelector('#shipDetailHunger'),
            weightFloat: this.el.querySelector('#shipDetailWeightFloat'),
            power: this.el.querySelector('#shipDetailPower'),
            volume: this.el.querySelector('#shipDetailVolume'),
            storage: this.el.querySelector('#shipDetailStorage'),
            rawBlock: this.el.querySelector('#shipDetailRawBlock'),
            toggleJsonBtn: this.el.querySelector('#toggleShipJsonBtn')
        };

        this.isJsonVisible = false;
        this._initEvents();
    }

    _initEvents() {
        this.ui.toggleJsonBtn.onclick = () => this.toggleJson();
    }

    toggleJson() {
        this.isJsonVisible = !this.isJsonVisible;
        if (this.isJsonVisible) {
            this.ui.rawBlock.classList.add('active');
            this.ui.toggleJsonBtn.textContent = 'Скрыть JSON';
        } else {
            this.ui.rawBlock.classList.remove('active');
            this.ui.toggleJsonBtn.textContent = 'JSON';
        }
    }

    update(shipData, rawJson) {
        if (this.el.style.opacity !== "1") {
            this.el.style.opacity = "1";
        }

        // Основные характеристики
        this.ui.name.textContent = `🚢 ${shipData.name}`;
        this.ui.id.textContent = `ID: ${shipData.id}`;
        this.ui.crew.textContent = shipData.crew;
        this.ui.hp.textContent = shipData.hp;
        this.ui.speed.textContent = `${shipData.max_speed.toFixed(1)} / ${shipData.max_speed.toFixed(1)}`; // Текущая/Макс (если текущей в схеме нет, пишем макс)
        this.ui.hunger.textContent = shipData.hunger.toFixed(4);
        this.ui.weightFloat.textContent = `${shipData.weight.toFixed(1)} / ${shipData.floatage}`;
        
        // Потребление / Выработка из кортежа power
        const [consumption, generation] = shipData.power;
        this.ui.power.textContent = `${consumption.toFixed(1)} / ${generation.toFixed(1)}`;
        
        // Объем трюма
        this.ui.volume.textContent = `${shipData.volume.toFixed(1)} / ${shipData.max_volume.toFixed(1)}`;

        // Отрисовка трюма (Storage)
        this.updateStorage(shipData.storage);

        // Сырой JSON
        this.ui.rawBlock.textContent = rawJson;
    }

    updateStorage(storage) {
        const keys = Object.keys(storage);
        if (keys.length === 0) {
            this.ui.storage.innerHTML = '<li style="color: #666; font-style: italic;">Трюм пуст</li>';
            return;
        }

        let html = '';
        for (const [key, val] of Object.entries(storage)) {
            html += `<li><strong>${escapeHtml(key)}</strong>: ${val}</li>`;
        }
        this.ui.storage.innerHTML = html;
    }
}

/**
 * Главный менеджер соединений и диспетчер данных
 */
class ConnectionManager {
    // Добавили shipDetailCard в конструктор
    constructor(logger, commandPanel, userCard, fleetCard, shipDetailCard) {
        this.tokenInput = document.getElementById('tokenInput');
        this.fleetIdInput = document.getElementById('fleetIdInput');
        this.connectBtn = document.getElementById('connectBtn');
        
        this.logger = logger;
        this.commandPanel = commandPanel;
        this.userCard = userCard;
        this.fleetCard = fleetCard;
        this.shipDetailCard = shipDetailCard; // Сохраняем ссылку на карточку деталей корабля
        this.ws = null;

        this.connectBtn.onclick = () => this.connect();

        this.commandPanel.setInitialTemplate(this.fleetIdInput.value.trim() || "1");
    }

    // Метод для отправки экшена выбора корабля в сокет
    selectShip(shipId) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.logger.error("Ошибка: Нет активного соединения для выбора корабля!");
            return;
        }
        
        const actionPayload = {
            action: "select_ship",
            ship_id: shipId
        };
        
        this.ws.send(JSON.stringify(actionPayload));
        this.logger.info(`Запрошены детальные данные для корабля ID: ${shipId}`);
    }

    setToken(token) {
        this.tokenInput.value = token;
    }

    connect() {
        const token = this.tokenInput.value.trim();
        const fleetId = this.fleetIdInput.value.trim();

        if (!token) {
            alert("Пожалуйста, сначала получите токен через форму входа!");
            return;
        }
        if (!fleetId) {
            alert("Пожалуйста, укажите ID флотилии!");
            return;
        }

        if (this.ws) {
            this.ws.close();
        }

        this.logger.info(`Установка соединения для флотилии ${fleetId}...`);
        
        const wsUrl = `ws://localhost:4000/ws/${fleetId}?token=${encodeURIComponent(token)}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.logger.info(`Соединение установлено (Флотилия ${fleetId})`);
            this.commandPanel.setSocket(this.ws);
        };

        this.ws.onmessage = (event) => this.handleMessage(event);

        this.ws.onclose = (event) => {
            this.commandPanel.setSocket(null);
            if (event.code === 4001) {
                this.logger.error("Ошибка: Неверный или просроченный токен");
            } else {
                this.logger.info(`Соединение закрыто (Код: ${event.code})`);
            }
        };

        this.ws.onerror = () => {
            this.logger.error("Ошибка WebSocket соединения");
            this.commandPanel.setSocket(null);
        };
    }

    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.out_type === 'entity') {
                if (data.entity_type === 'fleet') {
                    this.fleetCard.update(data, JSON.stringify(data, null, 2));
                } else if (data.entity_type === 'user') {
                    this.userCard.update(data, JSON.stringify(data, null, 2));
                } else if (data.entity_type === 'ship') {
                    // Обработка новой сущности - деталей корабля
                    this.shipDetailCard.update(data, JSON.stringify(data, null, 2));
                }
            }
        } catch (e) {
            console.error("Ошибка парсинга входящего сообщения", e);
        }
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener("DOMContentLoaded", () => {
    const logger = new Logger('log');
    const userCard = new UserCard('userCard');
    const shipDetailCard = new ShipDetailCard('shipDetailCard'); // Создаем карточку деталей корабля
    
    // Создаем менеджер (пока передаем null вместо fleetCard, так как они ссылаются друг на друга)
    const connectionManager = new ConnectionManager(logger, commandPanelInstancePlaceHolder(), userCard, null, shipDetailCard);
    
    // Инициализируем карточку флотилии, прокидывая колбэк на выбор корабля
    const fleetCard = new FleetCard('fleetCard', (shipId) => {
        connectionManager.selectShip(shipId);
    });
    
    // Связываем fleetCard обратно с менеджером
    connectionManager.fleetCard = fleetCard;

    const commandPanel = new CommandPanel(logger);
    connectionManager.commandPanel = commandPanel; // обновляем панель команд

    new AuthPanel(logger, (token) => {
        connectionManager.setToken(token);
    });
    
    // Вспомогательная заглушка для первого прохода конструктора менеджера
    function commandPanelInstancePlaceHolder() {
        return { setInitialTemplate: () => {} };
    }
});