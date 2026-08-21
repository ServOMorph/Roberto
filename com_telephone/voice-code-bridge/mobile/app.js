const connDot = document.getElementById("connDot");
const connLabel = document.getElementById("connLabel");
const stateLabel = document.getElementById("stateLabel");
const chat = document.getElementById("chat");
const composer = document.getElementById("composer");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const voiceScreen = document.getElementById("voiceScreen");
const voiceCircle = document.getElementById("voiceCircle");
const voiceStatus = document.getElementById("voiceStatus");
const voiceCancel = document.getElementById("voiceCancel");
const voicePause = document.getElementById("voicePause");
const assistantAudioEl = document.getElementById("assistantAudio");

let ws = null;
let reconnectTimer = null;
let currentSession = null;
let sessionCounter = 0;
let hasSpoken = false;
let voiceCancelled = false;
let voicePaused = false;
let currentAudio = null;
let audioUnlocked = false;

const SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=";

function unlockAudioElement() {
  if (audioUnlocked) return;
  audioUnlocked = true;
  assistantAudioEl.src = SILENT_WAV;
  assistantAudioEl.play().then(() => {
    assistantAudioEl.pause();
    assistantAudioEl.currentTime = 0;
  }).catch(() => {
    audioUnlocked = false;
  });
}

const SPEECH_THRESHOLD = 0.02;
const SILENCE_MS = 900;
const MAX_DURATION_MS = 15000;

function wsUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const portSuffix = window.location.port ? `:${window.location.port}` : "";
  return `${protocol}//${window.location.hostname}${portSuffix}`;
}

function setConnected(connected) {
  connDot.classList.toggle("connected", connected);
  connLabel.textContent = connected ? "Connecte" : "Deconnecte";
}

function setState(state) {
  const labels = {
    listening: "Ecoute",
    processing: "Traitement",
    speaking: "Reponse",
    error: "Erreur"
  };
  stateLabel.textContent = labels[state] || "";
}

function addBubble(role, text) {
  const el = document.createElement("div");
  el.className = `bubble ${role}`;
  el.textContent = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

function connect() {
  ws = new WebSocket(wsUrl());

  ws.onopen = () => {
    setConnected(true);
    clearTimeout(reconnectTimer);
  };

  ws.onclose = () => {
    setConnected(false);
    reconnectTimer = setTimeout(connect, 3000);
  };

  ws.onerror = () => {
    setConnected(false);
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "state") {
      setState(msg.state);
    } else if (msg.type === "assistant.text") {
      addBubble("assistant", msg.text);
    } else if (msg.type === "assistant.audio") {
      playAssistantAudio(msg.audio, msg.mime);
    }
  };
}

function playAssistantAudio(base64, mime) {
  const inVoiceMode = voiceScreen.classList.contains("active") && !voiceCancelled;
  if (inVoiceMode) {
    voiceCircle.classList.remove("thinking", "paused");
    voiceCircle.classList.add("done");
    voiceStatus.textContent = "Titi vous repond...";
  }

  const audio = assistantAudioEl;
  currentAudio = audio;

  const resumeListening = () => {
    if (currentAudio !== audio) return;
    currentAudio = null;
    audio.onended = null;
    audio.onerror = null;
    if (inVoiceMode && !voiceCancelled && !voicePaused) {
      startVoiceCapture();
    } else if (voicePaused) {
      voiceCircle.classList.add("paused");
      voiceStatus.textContent = "Micro en pause";
    }
  };

  audio.onended = resumeListening;
  audio.onerror = () => {
    debugLog("erreur lecture audio assistant");
    resumeListening();
  };

  audio.src = `data:${mime};base64,${base64}`;
  audio.play().catch((err) => {
    debugLog(`autoplay bloque: ${err.message}`);
    resumeListening();
  });
}

function sendUserMessage(text) {
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
  addBubble("user", text);
  ws.send(JSON.stringify({ type: "user.message", text }));
}

composer.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = textInput.value.trim();
  sendUserMessage(text);
  textInput.value = "";
});

function openVoiceScreen() {
  voiceScreen.classList.add("active");
  voiceCircle.classList.remove("done", "thinking", "paused");
  voiceStatus.textContent = "Je vous ecoute...";
  voicePause.textContent = "Pause micro";
}

function closeVoiceScreen() {
  voiceScreen.classList.remove("active");
}

function debugLog(text) {
  fetch("/debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  }).catch(() => {});
}

function pickMimeType() {
  const candidates = ["audio/webm", "audio/mp4", "audio/ogg"];
  for (const type of candidates) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(type)) return type;
  }
  return "";
}

function confirmAndSend(transcript) {
  voiceCircle.classList.remove("paused");
  voiceCircle.classList.add("done");
  voiceStatus.textContent = "Compris, j'envoie a Titi";

  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    sendUserMessage(transcript);

    voiceCircle.classList.remove("done", "paused");
    voiceCircle.classList.add("thinking");
    voiceStatus.textContent = "Titi reflechit...";
  };

  if (window.speechSynthesis) {
    const utterance = new SpeechSynthesisUtterance("Compris, j'envoie a Titi");
    utterance.lang = "fr-FR";
    utterance.onend = finish;
    utterance.onerror = finish;
    window.speechSynthesis.speak(utterance);
    setTimeout(finish, 3500);
  } else {
    setTimeout(finish, 800);
  }
}

const WHISPER_HALLUCINATIONS = [
  "sous-titres réalisés par la communauté d'amara.org",
  "sous-titrage st' 501",
  "merci d'avoir regardé cette vidéo",
  "abonnez-vous"
];

function isHallucination(text) {
  const lower = text.toLowerCase().trim();
  return WHISPER_HALLUCINATIONS.some((h) => lower.includes(h));
}

async function transcribeAudio(blob) {
  voiceStatus.textContent = "Transcription en cours...";
  try {
    const res = await fetch("/transcribe", {
      method: "POST",
      headers: { "Content-Type": blob.type || "application/octet-stream" },
      body: blob
    });
    const data = await res.json();

    if (!res.ok || !data.text || isHallucination(data.text)) {
      debugLog(`transcription vide/hallucination: ${JSON.stringify(data)}`);
      voiceStatus.textContent = "Rien compris, reessayez.";
      setTimeout(closeVoiceScreen, 1500);
      return;
    }

    confirmAndSend(data.text);
  } catch (err) {
    debugLog(`erreur transcription: ${err.message}`);
    voiceStatus.textContent = "Erreur de transcription.";
    setTimeout(closeVoiceScreen, 1500);
  }
}

function startVoiceCapture() {
  voiceCancelled = false;
  hasSpoken = false;

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    openVoiceScreen();
    voiceStatus.textContent = "Micro non supporte sur ce navigateur.";
    debugLog("getUserMedia indisponible");
    setTimeout(closeVoiceScreen, 2000);
    return;
  }

  openVoiceScreen();

  const session = { id: ++sessionCounter, discard: false, stopped: false };
  currentSession = session;

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then((stream) => {
      if (voiceCancelled || currentSession !== session || session.stopped) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      session.stream = stream;
      const mimeType = pickMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      session.recorder = recorder;
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      recorder.onstop = () => {
        clearTimeout(session.silenceTimer);
        clearTimeout(session.maxDurationTimer);
        stream.getTracks().forEach((t) => t.stop());
        session.audioContext.close().catch(() => {});

        if (session.discard || voiceCancelled) return;
        const blob = new Blob(chunks, { type: recorder.mimeType });
        transcribeAudio(blob);
      };

      recorder.start();
      debugLog(`enregistrement demarre (${recorder.mimeType})`);

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      session.audioContext = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);

      function checkVolume() {
        if (currentSession !== session || session.stopped) return;
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          const v = (data[i] - 128) / 128;
          sum += v * v;
        }
        const rms = Math.sqrt(sum / data.length);

        if (rms > SPEECH_THRESHOLD) {
          hasSpoken = true;
          clearTimeout(session.silenceTimer);
          session.silenceTimer = setTimeout(() => {
            if (recorder.state === "recording") recorder.stop();
          }, SILENCE_MS);
        }

        requestAnimationFrame(checkVolume);
      }
      requestAnimationFrame(checkVolume);

      session.maxDurationTimer = setTimeout(() => {
        if (recorder.state === "recording") recorder.stop();
      }, MAX_DURATION_MS);
    })
    .catch((err) => {
      debugLog(`getUserMedia refuse ou erreur: ${err.message}`);
      voiceStatus.textContent = "Micro refuse ou indisponible.";
      setTimeout(closeVoiceScreen, 2000);
    });
}

micBtn.addEventListener("click", () => {
  unlockAudioElement();
  startVoiceCapture();
});

function haltSession(session) {
  if (!session || session.stopped) return;
  session.discard = true;
  session.stopped = true;
  if (session.recorder && session.recorder.state === "recording") {
    session.recorder.stop();
  } else if (session.stream) {
    clearTimeout(session.silenceTimer);
    clearTimeout(session.maxDurationTimer);
    session.stream.getTracks().forEach((t) => t.stop());
    if (session.audioContext) session.audioContext.close().catch(() => {});
  }
}

voicePause.addEventListener("click", () => {
  if (voicePaused) {
    voicePaused = false;
    voicePause.textContent = "Pause micro";
    startVoiceCapture();
    return;
  }

  voicePaused = true;
  voicePause.textContent = "Reprendre";
  haltSession(currentSession);
  voiceCircle.classList.remove("done", "thinking");
  voiceCircle.classList.add("paused");
  voiceStatus.textContent = "Micro en pause";
});

voiceCancel.addEventListener("click", () => {
  voiceCancelled = true;
  voicePaused = false;
  haltSession(currentSession);
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  closeVoiceScreen();
});

connect();
debugLog(`ua: ${navigator.userAgent} | secureContext: ${window.isSecureContext} | mediaDevices: ${!!navigator.mediaDevices}`);
