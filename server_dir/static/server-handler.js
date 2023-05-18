const socket = io();

class ServerHandlerSockIO {
  constructor(server_ip, port, client_type = "user", time_out = 0) {
    this.sio = io(`http://${server_ip}:${port}`);
    this.sio.on("response", this.handle_response.bind(this));
    this.client_type = client_type;
    this.time_out = time_out;
    this.token = null;
    this.client_id = null;
    this.plant_dict = null;
  }

  // region GENERAL

  async listen() {
    return this.wait_for_response();
  }

  get_socketio() {
    return this.sio;
  }

  send_and_receive(mes) {
    const pickled_mes = JSON.stringify([...mes, this.client_id]);
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
    console.log("sent pickled data:", pickled_mes);
    this.sio.emit(mes[0], pickled_mes);
  }

  handle_response(response) {
    this.response = JSON.parse(response);
  }

  async wait_for_response() {
    let timeout = false;

    setTimeout(() => {
      timeout = true;
    }, 7385);

    while (!this.hasOwnProperty("response")) {
      await new Promise((r) => setTimeout(r, 100));

      if (timeout) {
        return -1;
      }
    }

    const response = this.response;
    delete this.response;
    return response;
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

  set_text(text) {
    var m = ["remote_action", [0, text]];
    this.send_and_receive(m);
  }

  get_moisture(plant) {
    var m = ["remote_action", [1, plant]];
    var moisture = this.send_and_receive(m);
    console.log("Moisture level: ", moisture);
    return moisture;
  }

  led_ring(plant, mode) {
    var m = ["remote_action", [2, plant, mode]];
    this.send(m);
  }

  add_water(plant, duration) {
    var m = ["remote_action", [3, plant, parseInt(duration)]];
    this.send(m);
  }

  get_light_level(plant) {
    var m = ["remote_action", [4, plant]];
    var light_level = this.send_and_receive(m);
    console.log("Light level: ", light_level);
    return light_level;
  }

  change_automatic(mode, plant) {
    var automatic = mode == "1" ? true : false;
    this.send_automatic_mode(automatic, plant);
  }

  stop_remote_mode() {
    const mes = ["remote_stop", null];
    this.send(mes);
  }

  // endregion

  // region VIDEO

  video_start(ip, port) {
    const mes = ["video_start", [ip, port]];
    var stream_ip = this.send_and_receive(mes);
    return stream_ip;
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

  get_plants_dict() {
    const mes = ["get_plant_dict", this.client_id];
    self.plant_dict = this.send_and_receive(mes);
  }

  get_dict() {
    return self.plant_dict;
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

  // home
  health_assesment() {
    var m = ["plant_health_web", []];
    var done = this.send_and_receive(m);
    return done;
  }
}
