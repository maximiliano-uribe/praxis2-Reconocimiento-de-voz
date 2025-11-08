let mediaRecorder;
let audioChunks = [];

async function grabarAudio(urlDestino) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("audio", blob, "voz.wav");

        const res = await fetch(urlDestino, { method: "POST", body: formData });
        const data = await res.json();

        if (data.grafica) {
            document.getElementById("resultado").innerHTML = `
                <h3>Transformada de Fourier</h3>
                <img src="data:image/png;base64,${data.grafica}" width="500">
            `;
        } else if (data.mensaje) {
            document.getElementById("resultado").innerHTML = `<p>${data.mensaje}</p>`;
        }
    };

    mediaRecorder.start();
    alert("🎤 Grabando 3 segundos...");
    setTimeout(() => mediaRecorder.stop(), 3000);
}
