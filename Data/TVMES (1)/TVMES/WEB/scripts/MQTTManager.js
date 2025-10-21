class MQTTManager {
  constructor(resource,that) {
    client = new Paho.MQTT.Client("arank47v", Number(8080), resource +"_POD");

    // set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = that.handleWebSocketMessage;

    // connect the client
    client.connect({ onSuccess: onConnect });


    // called when the client connects
    function onConnect() {
      console.log("onConnect");
      client.subscribe(resource);
    }

    // called when the client loses its connection
    function onConnectionLost(responseObject) {
      if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost: " + responseObject.errorMessage);
      }
    }

    // called when a message arrives
    function onMessageArrived(message) {
      console.log("onMessageArrived: " + JSON.parse(message.payloadString));
    }
  }
}