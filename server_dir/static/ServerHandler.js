// const io = require("socket.io-client");
const socket = io();
// const { promisify } = require("util");
// const wait = promisify(setTimeout);
// const pickle = require("picklejs");

class ServerHandlerSockIO {
  constructor(server_ip, port, client_type = "user", time_out = 0) {
    this.sio = io(`http://${server_ip}:${port}`);
    this.sio.on("response", this.handle_response.bind(this));
    this.client_type = client_type;
    this.time_out = time_out;
    this.client_id = null;
  }

  // region GENERAL

  async listen() {
    return this.wait_for_response();
  }

  async send_and_receive(mes) {
    const pickled_mes = JSON.stringify([...mes, this.client_id]);
    console.log("sent data:", mes, this.client_id);
    console.log("sent pickled data:", pickled_mes);
    this.sio.emit(mes[0], pickled_mes);
    return this.wait_for_response();
  }

  send(mes, add_id = true) {
    let pickled_mes;
    if (add_id) {
      pickled_mes = JSON.stringify([...mes, this.client_id]);
    } else {
      pickled_mes = JSON.stringify(mes);
    }
    this.sio.emit(mes[0], pickled_mes);
  }

  handle_response(response) {
    this.response = JSON.parse(response);
  }

  async wait_for_response() {
    while (!this.hasOwnProperty("response")) {
      await new Promise(r => setTimeout(r, 10));
    }
    if (this.response) {
      const response = this.response;
      console.log("Response:", response);
      delete this.response;
      return response;
    }
    return null;
  }

  // endregion

  // region USERSQL

  sign_up(username, password, user_code = null) {
    const mes = ["sign_up", username, password, user_code];
    this.send(mes);
  }

  async login(username, password) {
    const mes = ["login", username, password];
    const r = await this.send_and_receive(mes);
    this.set_client_id(r[1][0]);
    this.send_client_id(r[1][0]);
    return r;
  }

  register_plant(plant_dict) {
    const mes = ["register_plant", plant_dict];
    this.send(mes);
  }

  // endregion

  // region REMOTE

  set_time_out(time = null) {
    time = time ?? this.time_out;
    this.sio.serverManager.transport.webSocketServer.pingInterval = time;
  }

  send_data(data, add_id = true) {
    const mes = ["remote_data", data];
    this.send(mes, add_id);
    return null;
  }

  start_remote_mode() {
    const mes = ["remote_start", null];
    this.send(mes);
  }

  get_moisture(plant) {
    var m = ["remote_action", [1, plant]];
    var moisture = this.send_and_receive(m);
    console.log("Moisture level: ", moisture);
  }

  // endregion

  // region VIDEO

  video_start(ip, port) {
    const mes = ["video_start", [ip, port]];
    this.send(mes);
  }

  stop_receiving(ip, port) {
    const mes = ["video_stop", [ip, port]];
    this.send(mes);
  }

  // endregion

  // region Other Functions

  send_automatic_mode(mode, plant) {
    const mes = ["set_auto_mode", mode, plant];
    this.send(mes);
  }

  send_plants_names(plant_dict) {
    const mes = ["response_plant_dict", plant_dict];
    this.send(mes);
  }

  disconnect() {
    this.send_and_receive(["disconnect", null]);
  }

  set_client_id(id) {
    this.client_id = id;
  }

  send_client_id(id = null) {
    if (id !== null) {
      this.client_id = id;
    }
    const mes = ["client_type", this.client_type, this.client_id];
    const r = this.send_and_receive(mes);
  }
  // endregion
}

//if (require.main === module) {
//const server_handler = new ServerHandlerSockIO("127.0.0.1", 5000);
// server_handler.sign_up("2", "2")
// server_handler.login("2", "2");
//}
