let mediaRecorder;
let audioChunks = [];

async function grabarYEnviar(urlDestino) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", blob, "voz.webm");

        const res = await fetch(urlDestino, { method: "POST", body: formData });
        const data = await res.json();
        alert(data.mensaje);

        if (data.acceso) {
            // Redirigir solo si la voz coincide
            window.location.href = "/acceso";
        }
    };

    mediaRecorder.start();
    alert("🎤 Grabando 3 segundos...");
    setTimeout(() => mediaRecorder.stop(), 3000);
}

// Para registrar voz base:
function registrarVoz() {
    grabarYEnviar("/guardar_voz");
}

// Para verificar voz:
function verificarVoz() {
    grabarYEnviar("/verificar_voz");
}

