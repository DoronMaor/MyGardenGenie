const ServerHandler = {
  bufferSize: 2048,
  serverIp: "localhost",
  port: 60218,
  clientType: "plant",
  timeOut: 0,
  clientId: null,

  connectToServer() {
    const socket = new WebSocket("ws://" + server_ip + ":" + port);
    return socket;
  },

  sendAndReceive(mes) {
    const pickledMes = JSON.stringify(mes.concat(this.clientId));
    socket.send(pickledMes);
    socket.onmessage = (event) => {
      return JSON.parse(event.data);
    };
  },

  send(mes, addId = true) {
    let pickledMes;
    if (addId) {
      pickledMes = JSON.stringify(mes.concat(this.clientId));
    } else {
      pickledMes = JSON.stringify(mes);
    }
    socket.send(pickledMes);
  },

  signUp(username, password, userCode = null) {
    this.send(["sign_up", username, password, userCode]);
  },

  login(username, password) {
    const mes = ["login", username, password];
    const r = this.sendAndReceive(mes);
    this.setClientId(r[1][0]);
    this.sendClientId();
    return r;
  },

  startRemoteMode() {
    this.send(["remote_start", null]);
  },

  sendData(data, addId = true) {
    this.send(["remote_data", data], addId);
    return null;
  },

  videoStart(ip, port) {
    this.send(["video_start", [ip, port]]);
  },

  stopReceiving(ip, port) {
    this.send(["video_stop", [ip, port]]);
  },

  sendAutomaticMode(mode, plant) {
    this.send(["set_auto_mode", mode, plant]);
  },

  sendPlantsNames(plantDict) {
    var mes = ["response_plant_dict", plantDict];
    this.send(mes);
  },

  disconnect() {
    this.sendAndReceive(["disconnect", null]);
  },

  setClientId(id) {
    this.clientId = id;
  },

  sendClientId(id = null) {
    if (id !== null) {
      this.clientId = id;
    }

    console.log(
      this.sendAndReceive(["client_type", this.clientType, this.clientId])
    );
  },

  // remotes
  display_text(text) {
    var m = ("remote_action", (indx, inp));
    this.send(m);
  },
};
