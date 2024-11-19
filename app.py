import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import json
import paho.mqtt.client as paho

# Callbacks para MQTT
def on_publish(client, userdata, result):  
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"Mensaje recibido: {message_received}")

# Configuración MQTT
broker = "test.mosquitto.org"  # Cambiar broker según necesidad
port = 1883
client1 = paho.Client("GIT-HUB")
client1.on_message = on_message
client1.on_publish = on_publish
client1.connect(broker, port)

# Interfaz en Streamlit
st.title("Interfaz de voz Pill-E")
st.subheader("Pídele a Pill-E la pastilla que necesitas: Roja=Resfriado, Morada=Infección Gastrointestinal o Azul=Alergia.")

# Imagen decorativa
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.write("Toca el Botón y habla")

# Botón para iniciar reconocimiento de voz
stt_button = Button(label="Inicio", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };
    recognition.start();
"""))

# Procesamiento de eventos de reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    recognized_text = result.get("GET_TEXT").strip()
    st.write(f"Texto reconocido: {recognized_text}")

    # Publicar comando en MQTT según el texto reconocido
    if "pastilla roja" in recognized_text.lower():
        message = json.dumps({"command": "roja"})
    elif "pastilla morada" in recognized_text.lower():
        message = json.dumps({"command": "morada"})
    elif "pastilla azul" in recognized_text.lower():
        message = json.dumps({"command": "azul"})
    else:
        message = json.dumps({"command": "comando no reconocido"})
    
    ret = client1.publish("servo/comandos", message)
    st.write(f"Comando enviado: {message}")

# Asegurarse de que exista el directorio 'temp'
os.makedirs("temp", exist_ok=True)

