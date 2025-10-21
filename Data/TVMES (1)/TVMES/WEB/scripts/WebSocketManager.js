
class WebSocketManager {
	constructor(resource) {
		this.params = {};
		this.ws = null;
		this.timerId = null;
		this.timeout = 450000; // WebSocket keep alive timeout
		this.handle = null;
		this.messageTimer = null; // Mesaj zamanlayıcısı
		this.messageTimeout = 120000; // 2 dakika boyunca mesaj gelmezse yeniden bağlan
		this.errorTimeout= 10000; //Hata ile kapanırsa 10sn de tekrar dene
		this.SubscribeTags = "";
		this.resource = null;
	}

	_initializeWebSocket() {
		try {
			
			this.ws = new WebSocket("ws://" + window.location.host.split(":")[0] + ":8097/" + this.resource);
			this.ws.onopen = () => {

				const currentTime = new Date().toLocaleString();
				console.log(currentTime + "WebSocket connection established to " + this.ws.url);
				/*Otomatik kapat aç*/
				this.timerId = setTimeout(this._reconnect.bind(this), this.timeout);
				if (this.messageTimer)
					clearTimeout(this.messageTimer);
				this.messageTimer = setTimeout(this._reconnect.bind(this), this.messageTimeout);
			};
			this.ws.onmessage = this._onMessage.bind(this);
			this.ws.onclose = this._onClose.bind(this);
			this.ws.onerror = this._onError.bind(this);
		}
		catch (error) {
			const currentTime = new Date().toLocaleString();
			console.error(`${currentTime} WebSocket initialization error:`, error);
		};
	}

	_onMessage(event) {
		const jsonData = JSON.parse(event.data);
		if (jsonData) {
			if (this.externalMessageHandler) {
				this.externalMessageHandler(jsonData);
			}
			if (this.messageTimer)
				clearTimeout(this.messageTimer);
			this.messageTimer = setTimeout(this._reconnect.bind(this), this.messageTimeout);
		}

	}

	_onClose(event) {
		const currentTime = new Date().toLocaleString();
		if (event.wasClean) {
			console.log(`${currentTime} [close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);

		} else {
			console.log(`${currentTime} [close] Connection died, code=${event.code} reason=${event.reason}`);
		}
		clearTimeout(this.timerId);
	}

	_onError(error) {
		const currentTime = new Date().toLocaleString();
		console.log(`${currentTime} [error] ${error.message}`);
		if (this.messageTimer)
			clearTimeout(this.messageTimer);
		this.messageTimer = setTimeout(this._reconnect.bind(this), this.errorTimeout);
	}

	_reconnect() {
		this.closeConnection();
		this._initializeWebSocket();
	}


	openConnection(resource) {
		if (resource !== undefined)
			this.resource = resource;
		else
			this.resource = localStorage.selectedResource.split("-")[1];
		if (this.resource && this.resource !== null)
			this._initializeWebSocket();
	}

	closeConnection() {
		if (this.ws) {
			this.ws.close();
			clearTimeout(this.messageTimer);
			const currentTime = new Date().toLocaleString();
			console.log(`${currentTime} WebSocket connection closed.`);
		}
	}

	setMessageHandler(handler) {
		this.externalMessageHandler = handler;
	}



}