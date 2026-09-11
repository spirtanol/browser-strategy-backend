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
    constructor(containerId, onFleetSelect) {
        this.el = document.getElementById(containerId);
        this.onFleetSelect = onFleetSelect;
        this.selectedFleetId = null;
        this.ui = {
            name: this.el.querySelector('#userName'),
            id: this.el.querySelector('#userId'),
            money: this.el.querySelector('#userMoney'),
            fleetsContainer: this.el.querySelector('#fleetsContainer'),
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
        this.updateFleets(userData.fleets);
    }

    setSelectedFleetId(fleetId) {
        this.selectedFleetId = fleetId;
        this._refreshSelectedHighlight();
    }

    updateFleets(fleets) {
        if (!fleets || fleets.length === 0) {
            this.ui.fleetsContainer.innerHTML = '<div style="color: #666; font-style: italic;">Флотилии отсутствуют</div>';
            return;
        }

        let html = '';
        fleets.forEach(fleet => {
            const selectedClass = fleet.id === this.selectedFleetId ? ' selected' : '';
            html += `
                <div class="ship-card${selectedClass}" data-id="${fleet.id}">
                    <span class="ship-name">${escapeHtml(fleet.name)} (${fleet.id})</span>
                    <span class="ship-meta">Кораблей: ${fleet.ships_count}</span>
                    <span class="ship-meta">X: ${fleet.position.x.toFixed(1)}, Y: ${fleet.position.y.toFixed(1)} [${fleet.area ? `${fleet.area.name}` : 'Тьма'}]</span>
                </div>
            `;
        });
        this.ui.fleetsContainer.innerHTML = html;
        this._bindFleetClicks();
    }

    _refreshSelectedHighlight() {
        const cards = this.ui.fleetsContainer.querySelectorAll('.ship-card');
        cards.forEach(card => {
            const id = parseInt(card.getAttribute('data-id'), 10);
            card.classList.toggle('selected', id === this.selectedFleetId);
        });
    }

    _bindFleetClicks() {
        const cards = this.ui.fleetsContainer.querySelectorAll('.ship-card');
        cards.forEach(card => {
            card.onclick = () => {
                const fleetId = parseInt(card.getAttribute('data-id'), 10);
                if (this.onFleetSelect && !isNaN(fleetId)) {
                    this.onFleetSelect(fleetId);
                }
            };
        });
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
        this.input.value = `{"action": "act_name", "params": {"fleet_id": ${fleetId}}}`;
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
            toggleJsonBtn: this.el.querySelector('#toggleFleetJsonBtn'),
            area: this.el.querySelector('#fleetArea')
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
        this.ui.area.textContent = fleetData.area ? fleetData.area.name : "Тьма";
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
            repairBuffer: this.el.querySelector('#shipDetailRepairBuffer'),
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
        this.ui.repairBuffer.textContent = shipData.repair_buffer.toFixed(4);
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
 * Компонент Карточки Журнала
 */
class JournalCard {
    constructor(containerId) {
        this.el = document.getElementById(containerId);
        this.apiBase = 'http://localhost:4000/api';
        this.eventTemplates = {
            starvation_begins: 'Во флоте {fleet_name} ({fleet_id}) начался голод',
            commands_complete: 'Флот {fleet_name} ({fleet_id}) выполнил команды',
            move_started: 'Флот {fleet_name} ({fleet_id}) начал движение в точку ({x}, {y})',
            move_arrived: 'Флот {fleet_name} ({fleet_id}) прибыл в точку ({x}, {y})',
            dock_started: 'Флот {fleet_name} ({fleet_id}) швартуется к платформе {platform_name} ({platform_id})',
            docked: 'Флот {fleet_name} ({fleet_id}) пришвартовался к платформе {platform_name} ({platform_id})'
        };
        this.severityNames = {
            1: 'info',
            2: 'warning',
            3: 'dangerous'
        };
        this.ui = {
            badge: this.el.querySelector('#journalUnreadBadge'),
            list: this.el.querySelector('#journalList')
        };
        this._loadSeq = 0;
        this._expandedIds = new Set();
    }

    _token() {
        return document.getElementById('tokenInput').value.trim();
    }

    setUnread(n) {
        this.ui.badge.textContent = String(n);
        this.ui.badge.classList.toggle('has-unread', n > 0);
    }

    async load() {
        const token = this._token();
        if (!token) {
            return;
        }

        const seq = ++this._loadSeq;
        try {
            const response = await fetch(`${this.apiBase}/journal?limit=50`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const events = await response.json();
            if (seq !== this._loadSeq) {
                return;
            }

            this.el.style.opacity = '1';
            this._render(events);

            const unreadIds = events.filter(e => !e.is_read).map(e => e.id);
            if (unreadIds.length === 0) {
                this.setUnread(0);
                return;
            }

            const readResponse = await fetch(`${this.apiBase}/journal/read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ids: unreadIds })
            });
            if (!readResponse.ok) {
                throw new Error(`HTTP ${readResponse.status}`);
            }
            const unreadState = await readResponse.json();
            if (seq !== this._loadSeq) {
                return;
            }
            this.setUnread(unreadState.unread);
        } catch (error) {
            console.error('Ошибка загрузки журнала:', error);
        }
    }

    _render(events) {
        if (!events || events.length === 0) {
            this.ui.list.innerHTML = '<div class="journal-empty">событий нет</div>';
            return;
        }

        let html = '';
        events.forEach(event => {
            const severity = this.severityNames[event.severity] || 'info';
            const { title, details } = this._formatDescription(event);
            const time = this._formatTime(event.created_at);
            const expanded = this._expandedIds.has(event.id);
            const detailsBlock = details
                ? `<button type="button" class="journal-details-btn" data-id="${event.id}">${expanded ? 'скрыть' : 'подробнее'}</button>
                    <div class="journal-item-details${expanded ? ' open' : ''}">${details}</div>`
                : '';
            html += `
                <div class="journal-item severity-${severity}${event.is_read ? '' : ' unread'}">
                    <div class="journal-item-header">
                        <span class="journal-item-title">${escapeHtml(title)}</span>
                        <span class="journal-item-time">${escapeHtml(time)}</span>
                    </div>
                    ${detailsBlock}
                </div>
            `;
        });
        this.ui.list.innerHTML = html;
        this._bindDetailsToggles();
    }

    _bindDetailsToggles() {
        const buttons = this.ui.list.querySelectorAll('.journal-details-btn');
        buttons.forEach(btn => {
            btn.onclick = () => {
                const id = parseInt(btn.getAttribute('data-id'), 10);
                if (this._expandedIds.has(id)) {
                    this._expandedIds.delete(id);
                } else {
                    this._expandedIds.add(id);
                }
                const item = btn.closest('.journal-item');
                const details = item.querySelector('.journal-item-details');
                const open = this._expandedIds.has(id);
                details.classList.toggle('open', open);
                btn.textContent = open ? 'скрыть' : 'подробнее';
            };
        });
    }

    _formatDescription(event) {
        const params = event.params && typeof event.params === 'object' ? event.params : {};
        if (event.event_type === 'move_to_obj_started' || event.event_type === 'move_to_obj_arrived') {
            return { title: this._formatMoveToObject(params, event.event_type === 'move_to_obj_started'), details: null };
        }
        if (event.event_type === 'trade_started' || event.event_type === 'trade_completed') {
            return this._formatTrade(params, event.event_type === 'trade_started');
        }
        const template = this.eventTemplates[event.event_type];
        if (template) {
            const title = template.replace(/\{(\w+)\}/g, (_, key) => {
                const value = params[key];
                if (value === undefined || value === null) {
                    return '';
                }
                if (key === 'x' || key === 'y') {
                    const n = Number(value);
                    return Number.isFinite(n) ? n.toFixed(2) : String(value);
                }
                return String(value);
            });
            return { title, details: null };
        }

        const entries = Object.entries(params)
            .map(([key, value]) => `${key}=${value}`)
            .join(', ');
        return { title: entries ? `${event.event_type}: ${entries}` : event.event_type, details: null };
    }

    _formatTrade(params, started) {
        const fleet = `Флот ${params.fleet_name} (${params.fleet_id})`;
        const platform = `платформе ${params.platform_name} (${params.platform_id})`;
        if (started) {
            return {
                title: `${fleet} начал торговлю на ${platform}`,
                details: this._formatTradeOpsDetails(params.operations || [])
            };
        }
        const fills = params.fills || [];
        const { buy, sell } = this._tradeTotals(fills);
        const net = sell - buy;
        const signed = net > 0 ? `+${net}` : String(net);
        return {
            title: `${fleet} завершил торговлю на ${platform}, баланс ${signed}`,
            details: this._formatTradeFillsDetails(fills, buy, sell)
        };
    }

    _tradeTotals(fills) {
        let buy = 0;
        let sell = 0;
        fills.forEach(fill => {
            const money = Number(fill.quantity) * Number(fill.price);
            if (fill.op_type === 2) {
                sell += money;
            } else {
                buy += money;
            }
        });
        return { buy, sell };
    }

    _formatTradeOpsDetails(operations) {
        if (!operations.length) {
            return '<div class="journal-details-empty">без операций</div>';
        }
        const buys = operations.filter(op => op.op_type !== 2);
        const sells = operations.filter(op => op.op_type === 2);
        return this._tradeListsHtml(buys, sells, true);
    }

    _formatTradeFillsDetails(fills, buyTotal, sellTotal) {
        if (!fills.length) {
            return '<div class="journal-details-empty">сделок не было</div>';
        }
        const buys = fills.filter(fill => fill.op_type !== 2);
        const sells = fills.filter(fill => fill.op_type === 2);
        return `${this._tradeListsHtml(buys, sells, false)}
            <div class="journal-details-totals">покупки: ${buyTotal}</div>
            <div class="journal-details-totals">продажи: ${sellTotal}</div>`;
    }

    _tradeListsHtml(buys, sells, isIntent) {
        const line = (item) => {
            const qty = isIntent && item.quantity === -1 ? 'всё' : item.quantity;
            return `<li>${escapeHtml(String(item.item_name))} ${escapeHtml(String(qty))} по ${escapeHtml(String(item.price))}</li>`;
        };
        const buyBlock = buys.length
            ? `<div class="journal-details-label">Покупки</div><ul class="journal-details-list">${buys.map(line).join('')}</ul>`
            : '';
        const sellBlock = sells.length
            ? `<div class="journal-details-label">Продажи</div><ul class="journal-details-list">${sells.map(line).join('')}</ul>`
            : '';
        return `${buyBlock}${sellBlock}`;
    }

    _formatMoveToObject(params, started) {
        const verb = started ? 'начал движение к' : 'прибыл к';
        const fleet = `Флот ${params.fleet_name} (${params.fleet_id})`;
        const objId = params.obj_id;
        const objName = params.obj_name ? String(params.obj_name) : '';
        switch (params.obj_type) {
            case 1:
                return objName
                    ? `${fleet} ${verb} платформе ${objName} (${objId})`
                    : `${fleet} ${verb} платформе (${objId})`;
            case 3:
                return objName
                    ? `${fleet} ${verb} флоту ${objName} (${objId})`
                    : `${fleet} ${verb} флоту (${objId})`;
            case 2: {
                const contents = { 1: 'рыбы', 2: 'феррита', 3: 'пирозина' };
                const content = contents[params.site_content] || 'ресурса';
                return `${fleet} ${verb} месторождению ${content} (${objId})`;
            }
            default:
                return `${fleet} ${verb} объекту (${objId})`;
        }
    }

    _formatTime(iso) {
        if (!iso) {
            return '--';
        }
        const date = new Date(iso);
        if (Number.isNaN(date.getTime())) {
            return String(iso);
        }
        return date.toLocaleString();
    }
}

/**
 * Главный менеджер соединений и диспетчер данных
 */
class ConnectionManager {
    constructor(logger, commandPanel, userCard, fleetCard, shipDetailCard, journalCard) {
        this.tokenInput = document.getElementById('tokenInput');
        this.connectBtn = document.getElementById('connectBtn');
        
        this.logger = logger;
        this.commandPanel = commandPanel;
        this.userCard = userCard;
        this.fleetCard = fleetCard;
        this.shipDetailCard = shipDetailCard;
        this.journalCard = journalCard;
        this.ws = null;

        this.connectBtn.onclick = () => this.connect();
    }

    selectFleet(fleetId) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.logger.error("Ошибка: Нет активного соединения для выбора флотилии!");
            return;
        }

        const actionPayload = {
            action: "subscribe",
            entity_type: "fleet",
            entity_id: fleetId
        };

        this.ws.send(JSON.stringify(actionPayload));
        this.userCard.setSelectedFleetId(fleetId);
        this.commandPanel.setInitialTemplate(fleetId);
        this.resetShipDetail();
        this.logger.info(`Запрошены данные флотилии ID: ${fleetId}`);
    }

    selectShip(shipId) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.logger.error("Ошибка: Нет активного соединения для выбора корабля!");
            return;
        }
        
        const actionPayload = {
            action: "subscribe",
            entity_type: "ship",
            entity_id: shipId
        };
        
        this.ws.send(JSON.stringify(actionPayload));
        this.logger.info(`Запрошены детальные данные для корабля ID: ${shipId}`);
    }

    resetShipDetail() {
        const el = this.shipDetailCard.el;
        el.style.opacity = "0.5";
        this.shipDetailCard.ui.name.textContent = "Корабль не выбран...";
        this.shipDetailCard.ui.id.textContent = "ID: --";
        this.shipDetailCard.ui.crew.textContent = "--";
        this.shipDetailCard.ui.hp.textContent = "--";
        this.shipDetailCard.ui.speed.textContent = "--";
        this.shipDetailCard.ui.hunger.textContent = "--";
        this.shipDetailCard.ui.repairBuffer.textContent = "--";
        this.shipDetailCard.ui.weightFloat.textContent = "-- / --";
        this.shipDetailCard.ui.power.textContent = "-- / --";
        this.shipDetailCard.ui.volume.textContent = "-- / --";
        this.shipDetailCard.ui.storage.innerHTML = '<li style="color: #666; font-style: italic;">Трюм пуст</li>';
        this.shipDetailCard.ui.rawBlock.textContent = "{}";
    }

    setToken(token) {
        this.tokenInput.value = token;
    }

    connect() {
        const token = this.tokenInput.value.trim();

        if (!token) {
            alert("Пожалуйста, сначала получите токен через форму входа!");
            return;
        }

        if (this.ws) {
            this.ws.close();
        }

        this.logger.info("Установка WebSocket соединения...");
        
        const wsUrl = `ws://localhost:4000/ws/?token=${encodeURIComponent(token)}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.logger.info("Соединение установлено");
            this.commandPanel.setSocket(this.ws);
            this.journalCard.load();
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
                    this.shipDetailCard.update(data, JSON.stringify(data, null, 2));
                }
            } else if (data.out_type === 'journal') {
                this.journalCard.setUnread(data.unread);
                this.journalCard.load();
            }
        } catch (e) {
            console.error("Ошибка парсинга входящего сообщения", e);
        }
    }
}

// Инициализация приложения при загрузке DOM
document.addEventListener("DOMContentLoaded", () => {
    const logger = new Logger('log');
    const shipDetailCard = new ShipDetailCard('shipDetailCard');
    const journalCard = new JournalCard('journalCard');
    const commandPanel = new CommandPanel(logger);

    const connectionManager = new ConnectionManager(logger, commandPanel, null, null, shipDetailCard, journalCard);

    const userCard = new UserCard('userCard', (fleetId) => {
        connectionManager.selectFleet(fleetId);
    });
    const fleetCard = new FleetCard('fleetCard', (shipId) => {
        connectionManager.selectShip(shipId);
    });

    connectionManager.userCard = userCard;
    connectionManager.fleetCard = fleetCard;

    new AuthPanel(logger, (token) => {
        connectionManager.setToken(token);
    });
});