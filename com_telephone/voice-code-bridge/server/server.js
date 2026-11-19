const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { exec } = require("child_process");
const { URL } = require("url");
const { WebSocketServer } = require("ws");
const webpush = require("web-push");

const PORT = process.env.PORT || 5000;
const STT_PORT = process.env.STT_PORT || 5001;
const TTS_PORT = process.env.TTS_PORT || 5002;
const MOBILE_DIR = path.join(__dirname, "..", "mobile");
const MESSAGES_LOG = path.join(__dirname, "messages.log");
const PROJECTS_FILE = path.join(__dirname, "projects.json");
const LOGS_DIR = path.join(__dirname, "logs");

let projects;
try {
  projects = JSON.parse(fs.readFileSync(PROJECTS_FILE, "utf8"));
} catch (err) {
  console.error(`projects.json illisible (${err.message}). Copier projects.example.json et l'adapter.`);
  process.exit(1);
}
if (!Array.isArray(projects) || projects.length === 0) {
  console.error("projects.json doit etre un tableau non vide.");
  process.exit(1);
}
const DEFAULT_PROJECT = projects[0];
fs.mkdirSync(LOGS_DIR, { recursive: true });

function resolveProject(id) {
  return projects.find((p) => p && p.id === id) || null;
}
function projectLog(project) {
  return path.join(__dirname, project.log);
}

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  for (const line of fs.readFileSync(filePath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    if (idx === -1) continue;
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    if (!(key in process.env)) process.env[key] = value;
  }
}
loadEnvFile(path.join(__dirname, ".env"));

const AUTH_TOKEN = process.env.AUTH_TOKEN;
if (!AUTH_TOKEN) {
  console.error("AUTH_TOKEN manquant. Definir la variable d'environnement AUTH_TOKEN avant de lancer le serveur.");
  process.exit(1);
}

const BIND_HOST = process.env.BIND_HOST || "127.0.0.1";
const NOTIF_SHOW_CONTENT = process.env.NOTIF_SHOW_CONTENT === "1";
const ALLOW_REMOTE_SLEEP = process.env.ALLOW_REMOTE_SLEEP === "1";
const BANG_ALLOWLIST = (process.env.BANG_ALLOWLIST || "close,start")
  .split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
const MAX_WS_CLIENTS = 5;
const MAX_JSON_BODY = 64 * 1024;
const MAX_AUDIO_BODY = 10 * 1024 * 1024;
const VOCAL_GROUP_MS = Number(process.env.VOCAL_GROUP_MS || 4000);
const VOCAL_GROUP_MAX_MS = 15000;
const REPLY_ALERT_MS = Number(process.env.REPLY_ALERT_MS || 60000);

const vocalBuffers = new Map();
const replyWatches = new Map();

function startReplyWatch(project) {
  if (!REPLY_ALERT_MS) return;
  clearTimeout(replyWatches.get(project.id));
  replyWatches.set(project.id, setTimeout(() => {
    replyWatches.delete(project.id);
    logLine(`ALERTE ${project.label} sans reponse depuis ${Math.round(REPLY_ALERT_MS / 1000)} s`);
    broadcastAndNotify(project, { text: `${project.label} n'a pas répondu.` });
  }, REPLY_ALERT_MS));
}

function writeUserLine(project, text, channel) {
  fs.appendFile(projectLog(project), `${new Date().toISOString()}\t${text}\t[canal:${channel}]\n`, "utf8", () => {});
  startReplyWatch(project);
}

function flushVocal(project) {
  const buf = vocalBuffers.get(project.id);
  if (!buf) return;
  clearTimeout(buf.timer);
  vocalBuffers.delete(project.id);
  const text = buf.parts.join(" ").replace(/\s+/g, " ").trim();
  if (text) writeUserLine(project, text, "vocal");
}

function bufferVocal(project, text) {
  const buf = vocalBuffers.get(project.id) || { parts: [], firstAt: Date.now(), timer: null };
  buf.parts.push(text);
  clearTimeout(buf.timer);
  const remaining = Math.max(0, VOCAL_GROUP_MAX_MS - (Date.now() - buf.firstAt));
  buf.timer = setTimeout(() => flushVocal(project), Math.min(VOCAL_GROUP_MS, remaining));
  vocalBuffers.set(project.id, buf);
}

const rateBuckets = new Map();
function allowRate(key, limit, windowMs) {
  const now = Date.now();
  const bucket = rateBuckets.get(key) || [];
  while (bucket.length && now - bucket[0] > windowMs) bucket.shift();
  if (bucket.length >= limit) {
    rateBuckets.set(key, bucket);
    return false;
  }
  bucket.push(now);
  rateBuckets.set(key, bucket);
  return true;
}

function readBody(req, res, max, onDone) {
  const chunks = [];
  let size = 0;
  let aborted = false;
  req.on("data", (chunk) => {
    if (aborted) return;
    size += chunk.length;
    if (size > max) {
      aborted = true;
      res.writeHead(413);
      res.end("Trop volumineux");
      req.destroy();
      return;
    }
    chunks.push(chunk);
  });
  req.on("end", () => {
    if (!aborted) onDone(Buffer.concat(chunks));
  });
}

const VAPID_PUBLIC = process.env.VAPID_PUBLIC;
const VAPID_PRIVATE = process.env.VAPID_PRIVATE;
if (VAPID_PUBLIC && VAPID_PRIVATE) {
  webpush.setVapidDetails("https://serenia-tech.fr", VAPID_PUBLIC, VAPID_PRIVATE);
}

const SUBS_FILE = path.join(__dirname, "push_subs.json");
let pushSubs = new Map();
function loadSubs() {
  try {
    pushSubs = new Map(JSON.parse(fs.readFileSync(SUBS_FILE, "utf8")));
  } catch {
    pushSubs = new Map();
  }
}
function saveSubs() {
  fs.writeFileSync(SUBS_FILE, JSON.stringify([...pushSubs]), "utf8");
}
loadSubs();

const lastMessages = new Map();
let lastSleepRequest = 0;

const FOREGROUND_WINDOW_MS = 8000;
let midCounter = 0;
function nextMid() {
  return `${Date.now().toString(36)}_${(++midCounter).toString(36)}`;
}
function anyClientForeground() {
  for (const client of wss.clients) {
    if (client.readyState === client.OPEN && Date.now() - (client.lastVisible || 0) < FOREGROUND_WINDOW_MS) {
      return true;
    }
  }
  return false;
}

function broadcastAndNotify(project, payload) {
  clearTimeout(replyWatches.get(project.id));
  replyWatches.delete(project.id);
  const mid = nextMid();
  const textMsg = JSON.stringify({
    type: "assistant.text", project: project.id, mid, text: payload.text,
    awaitValidation: payload.awaitValidation, options: payload.options, recommended: payload.recommended
  });
  const audioMsg = payload.audio
    ? JSON.stringify({ type: "assistant.audio", project: project.id, mid, audio: payload.audio, mime: payload.mime })
    : null;
  const stateMsg = JSON.stringify({ type: "state", state: "listening" });

  let sent = 0;
  wss.clients.forEach((client) => {
    if (client.readyState === client.OPEN) {
      client.send(textMsg);
      client.send(audioMsg || stateMsg);
      sent++;
    }
  });

  const foreground = anyClientForeground();
  if (foreground) {
    lastMessages.delete(project.id);
  } else {
    lastMessages.set(project.id, {
      mid, text: payload.text, audio: payload.audio || null, mime: payload.mime || null,
      awaitValidation: payload.awaitValidation, options: payload.options, recommended: payload.recommended
    });
    sendPushNotification(NOTIF_SHOW_CONTENT ? payload.text : "Nouveau message", `${project.label} · Assistant`).catch(() => {});
  }
  return { sent, push: !foreground };
}

function logLine(text) {
  fs.appendFile(MESSAGES_LOG, `${new Date().toISOString()}\t[DEBUG] ${text}\n`, "utf8", () => {});
}

function sendPushNotification(text, title) {
  if (!VAPID_PUBLIC || !VAPID_PRIVATE) {
    logLine("push ignore: VAPID non configure");
    return Promise.resolve({ skipped: true, results: [] });
  }
  if (pushSubs.size === 0) {
    logLine("push ignore: aucune souscription enregistree");
    return Promise.resolve({ skipped: true, results: [] });
  }
  const payload = JSON.stringify({ title: title || "Assistant", body: text });
  const jobs = [...pushSubs.values()].map((sub) => {
    return webpush.sendNotification(sub, payload, { TTL: 300 })
      .then((res) => ({ endpoint: sub.endpoint, statusCode: res.statusCode }))
      .catch((err) => {
        const staleKey = err.statusCode === 400 && String(err.body || "").includes("VapidPkHashMismatch");
        if (err.statusCode === 404 || err.statusCode === 410 || staleKey) {
          pushSubs.delete(sub.endpoint);
          saveSubs();
        }
        return { endpoint: sub.endpoint, error: err.statusCode || err.message, body: String(err.body || "").slice(0, 300) };
      });
  });
  return Promise.all(jobs).then((results) => {
    for (const r of results) {
      if (r.error) {
        logLine(`push echec (${r.endpoint.slice(-12)}): ${r.error} ${r.body}`);
      } else {
        logLine(`push envoye (${r.endpoint.slice(-12)}): ${r.statusCode}`);
      }
    }
    return { count: jobs.length, results };
  });
}

const MIME_TYPES = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css"
};

function timingSafeEqualStr(a, b) {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  if (bufA.length !== bufB.length) return false;
  return crypto.timingSafeEqual(bufA, bufB);
}

function getCookie(req, name) {
  const header = req.headers.cookie;
  if (!header) return null;
  for (const part of header.split(";")) {
    const idx = part.indexOf("=");
    if (idx === -1) continue;
    if (part.slice(0, idx).trim() === name) return part.slice(idx + 1).trim();
  }
  return null;
}

function isAuthed(req) {
  const cookieToken = getCookie(req, "auth");
  if (cookieToken && timingSafeEqualStr(cookieToken, AUTH_TOKEN)) return true;
  const url = new URL(req.url, "http://localhost");
  const queryToken = url.searchParams.get("token");
  return !!queryToken && timingSafeEqualStr(queryToken, AUTH_TOKEN);
}

const DEVICES_FILE = path.join(__dirname, "known_devices.json");
let knownDevices = {};
let devicesMtime = -1;
function loadDevices() {
  let mtime = 0;
  try {
    mtime = fs.statSync(DEVICES_FILE).mtimeMs;
  } catch {
    mtime = 0;
  }
  if (mtime === devicesMtime) return;
  devicesMtime = mtime;
  try {
    knownDevices = JSON.parse(fs.readFileSync(DEVICES_FILE, "utf8")) || {};
  } catch {
    knownDevices = {};
  }
}
loadDevices();

function isKnownDevice(req) {
  loadDevices();
  const id = getCookie(req, "dev");
  return !!id && /^[a-f0-9]{32}$/.test(id) && Object.prototype.hasOwnProperty.call(knownDevices, id);
}

function pairingLocked() {
  loadDevices();
  return Object.keys(knownDevices).length > 0;
}

const SECONDARY_PAIRING_MS = 10 * 60 * 1000;
const MAX_DEVICES = 3;
function uaFamily(ua) {
  return String(ua || "").split("Mobile/")[0].replace(/Version\/[\d.]+/, "").replace(/\s+/g, " ").trim();
}
// Safari et l'appli ecran d'accueil iOS ont des cookies separes : un 2e contexte du meme
// navigateur est accepte pendant 10 min apres l'appairage du premier.
function canPairSecondary(req) {
  loadDevices();
  const entries = Object.values(knownDevices);
  if (entries.length === 0 || entries.length >= MAX_DEVICES) return false;
  const ua = uaFamily(req.headers["user-agent"]);
  if (!ua) return false;
  const now = Date.now();
  return entries.some((d) =>
    now - Date.parse(d.premiereConnexion) < SECONDARY_PAIRING_MS && uaFamily(d.ua) === ua
  );
}

function clientIp(req) {
  const fwd = req.headers["cf-connecting-ip"] || String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return oneLine(fwd || req.socket.remoteAddress || "inconnue").slice(0, 64);
}

function registerNewDevice(req) {
  const id = crypto.randomBytes(16).toString("hex");
  const ua = oneLine(req.headers["user-agent"] || "inconnu").slice(0, 160);
  const ip = clientIp(req);
  knownDevices[id] = { premiereConnexion: new Date().toISOString(), ip, ua };
  fs.writeFileSync(DEVICES_FILE, JSON.stringify(knownDevices, null, 2), "utf8");
  devicesMtime = -1;
  logLine(`APPAIRAGE appareil enregistre (${Object.keys(knownDevices).length} au total): ${ip} ${ua}`);
  return id;
}

function reportRefusedDevice(req) {
  const ua = oneLine(req.headers["user-agent"] || "inconnu").slice(0, 160);
  const ip = clientIp(req);
  logLine(`ALERTE appareil non appaire refuse: ${ip} ${ua}`);
  if (allowRate("refus-push", 3, 10 * 60 * 1000)) {
    sendPushNotification(
      `Tentative de connexion refusée (${ip}, ${ua.slice(0, 60)}). Quelqu'un a peut-être votre lien : changez AUTH_TOKEN.`,
      "Alerte sécurité"
    ).catch(() => {});
  }
}

function isAuthedDevice(req) {
  return isAuthed(req) && isKnownDevice(req);
}

function isLoopback(req) {
  const addr = req.socket.remoteAddress;
  return addr === "127.0.0.1" || addr === "::1" || addr === "::ffff:127.0.0.1";
}

const FORWARDED_HEADERS = ["x-forwarded-for", "x-forwarded-host", "x-real-ip", "cf-connecting-ip", "forwarded", "fly-client-ip", "true-client-ip"];
function isProxied(req) {
  return FORWARDED_HEADERS.some((h) => req.headers[h]);
}
// Endpoints "locaux" (/send, /push/test) : vraiment locaux, jamais via un tunnel.
function isLocalOnly(req) {
  return isLoopback(req) && !isProxied(req);
}

function oneLine(value) {
  return String(value == null ? "" : value).replace(/[\r\n\t]+/g, " ");
}

const httpServer = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/send") {
    if (!isLocalOnly(req)) {
      res.writeHead(403);
      res.end("Interdit");
      return;
    }
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    req.on("end", () => {
      let text, mode, awaitValidation, options, recommended, project;
      try {
        const parsed = JSON.parse(body);
        text = parsed.text;
        mode = parsed.mode;
        awaitValidation = !!parsed.awaitValidation;
        options = Array.isArray(parsed.options) ? parsed.options.filter((o) => typeof o === "string") : null;
        recommended = typeof parsed.recommended === "string" ? parsed.recommended : null;
        project = resolveProject(parsed.project);
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }

      if (!project) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "champ 'project' manquant ou inconnu", projets: projects.map((p) => p.id) }));
        return;
      }

      if (typeof text !== "string" || !text.trim()) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "champ 'text' manquant ou vide (cle attendue: 'text')" }));
        return;
      }

      if (mode === "texte") {
        const r = broadcastAndNotify(project, { text, awaitValidation, options, recommended });
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(r));
        return;
      }

      const ttsReq = http.request({
        host: "127.0.0.1",
        port: TTS_PORT,
        path: "/synthesize",
        method: "POST",
        headers: { "Content-Type": "application/json" }
      }, (ttsRes) => {
        const chunks = [];
        ttsRes.on("data", (chunk) => chunks.push(chunk));
        ttsRes.on("end", () => {
          const audioMime = ttsRes.headers["content-type"] || "audio/wav";
          const audioB64 = Buffer.concat(chunks).toString("base64");

          const r = broadcastAndNotify(project, { text, awaitValidation, options, recommended, audio: audioB64, mime: audioMime });

          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify(r));
        });
      });

      ttsReq.on("error", () => {
        const r = broadcastAndNotify(project, { text, awaitValidation, options, recommended });
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ...r, tts: "indisponible" }));
      });

      ttsReq.end(JSON.stringify({ text }));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/push/subscribe") {
    if (!isAuthedDevice(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    readBody(req, res, MAX_JSON_BODY, (buf) => {
      const body = buf.toString("utf8");
      let payload;
      try {
        payload = JSON.parse(body);
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }
      const sub = payload && payload.subscription ? payload.subscription : payload;
      const deviceId = payload && typeof payload.deviceId === "string" ? payload.deviceId : null;
      if (!sub || !sub.endpoint) {
        res.writeHead(400);
        res.end("Abonnement invalide");
        return;
      }
      if (deviceId) {
        for (const [ep, s] of pushSubs) {
          if (ep !== sub.endpoint && (!s.deviceId || s.deviceId === deviceId)) {
            pushSubs.delete(ep);
          }
        }
      }
      pushSubs.set(sub.endpoint, { ...sub, deviceId });
      saveSubs();
      res.writeHead(200);
      res.end("ok");
    });
    return;
  }

  if (req.method === "POST" && req.url === "/push/unsubscribe") {
    if (!isAuthedDevice(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    readBody(req, res, MAX_JSON_BODY, (buf) => {
      const body = buf.toString("utf8");
      let sub;
      try {
        sub = JSON.parse(body);
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }
      pushSubs.delete(sub && sub.endpoint);
      saveSubs();
      res.writeHead(200);
      res.end("ok");
    });
    return;
  }

  if (req.method === "POST" && req.url === "/push/test") {
    if (!isLocalOnly(req)) {
      res.writeHead(403);
      res.end("Interdit");
      return;
    }
    sendPushNotification("Notification de test").then((r) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(r));
    }).catch((err) => {
      res.writeHead(500);
      res.end(String(err));
    });
    return;
  }

  if (req.method === "POST" && req.url === "/transcribe") {
    if (!isAuthedDevice(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    if (!allowRate("transcribe", 30, 60 * 1000)) {
      res.writeHead(429);
      res.end("Trop de requetes");
      return;
    }
    readBody(req, res, MAX_AUDIO_BODY, (audio) => {

      const sttReq = http.request({
        host: "127.0.0.1",
        port: STT_PORT,
        path: "/transcribe",
        method: "POST",
        headers: { "Content-Length": audio.length }
      }, (sttRes) => {
        let body = "";
        sttRes.on("data", (chunk) => { body += chunk; });
        sttRes.on("end", () => {
          res.writeHead(sttRes.statusCode, { "Content-Type": "application/json" });
          res.end(body);
        });
      });

      sttReq.on("error", () => {
        res.writeHead(502, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "STT indisponible" }));
      });

      sttReq.end(audio);
    });
    return;
  }

  if (req.method === "POST" && req.url === "/debug") {
    if (!isAuthedDevice(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    if (!allowRate("debug", 120, 60 * 1000)) {
      res.writeHead(429);
      res.end("Trop de requetes");
      return;
    }
    readBody(req, res, MAX_JSON_BODY, (buf) => {
      const body = buf.toString("utf8");
      let text;
      try {
        text = JSON.parse(body).text;
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }

      const line = `${new Date().toISOString()}\t[DEBUG] ${oneLine(text)}\n`;
      fs.appendFile(MESSAGES_LOG, line, "utf8", () => {});

      res.writeHead(200);
      res.end("ok");
    });
    return;
  }

  if (req.method === "GET" && req.url.split("?")[0] === "/vapid-public") {
    if (!isAuthedDevice(req) || !VAPID_PUBLIC) {
      res.writeHead(VAPID_PUBLIC ? 401 : 404);
      res.end(VAPID_PUBLIC ? "Non autorise" : "VAPID non configure");
      return;
    }
    res.writeHead(200, { "Content-Type": "text/plain", "Cache-Control": "no-store" });
    res.end(VAPID_PUBLIC);
    return;
  }

  if (req.method === "GET" && req.url.split("?")[0] === "/projects") {
    if (!isAuthedDevice(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    res.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "no-store" });
    res.end(JSON.stringify(projects.map((p) => ({ id: p.id, label: p.label }))));
    return;
  }

  if (!isAuthed(req)) {
    res.writeHead(401);
    res.end("Non autorise");
    return;
  }

  const url = new URL(req.url, "http://localhost");
  let filePath = url.pathname === "/" ? "/index.html" : url.pathname;
  filePath = path.join(MOBILE_DIR, filePath);

  if (!filePath.startsWith(MOBILE_DIR + path.sep)) {
    res.writeHead(403);
    res.end("Interdit");
    return;
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      res.end("Introuvable");
      return;
    }
    const ext = path.extname(filePath);
    const headers = {
      "Content-Type": MIME_TYPES[ext] || "application/octet-stream",
      "Cache-Control": "no-store"
    };
    if (ext === ".html" && !isKnownDevice(req) && pairingLocked() && !canPairSecondary(req)) {
      reportRefusedDevice(req);
      res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Appareil non appaire");
      return;
    }
    const cookies = [];
    if (url.searchParams.get("token")) {
      cookies.push(`auth=${AUTH_TOKEN}; HttpOnly; SameSite=Strict; Max-Age=31536000; Path=/`);
    }
    if (ext === ".html" && !isKnownDevice(req)) {
      cookies.push(`dev=${registerNewDevice(req)}; HttpOnly; SameSite=Strict; Max-Age=31536000; Path=/`);
    }
    if (cookies.length) headers["Set-Cookie"] = cookies;
    res.writeHead(200, headers);
    res.end(content);
  });
});

const wss = new WebSocketServer({
  server: httpServer,
  maxPayload: 12 * 1024 * 1024,
  verifyClient: (info, callback) => {
    const cookieToken = getCookie(info.req, "auth");
    const authed = !!cookieToken && timingSafeEqualStr(cookieToken, AUTH_TOKEN);
    if (!authed || !isKnownDevice(info.req)) {
      callback(false, 401, "Non autorise");
      return;
    }
    if (wss.clients.size >= MAX_WS_CLIENTS) {
      logLine(`connexion refusee: ${MAX_WS_CLIENTS} clients deja connectes`);
      callback(false, 503, "Trop de connexions");
      return;
    }
    callback(true);
  }
});

wss.on("connection", (ws) => {
  console.log(`[${new Date().toISOString()}] Client connecte`);

  ws.isAlive = true;
  ws.lastVisible = 0;
  ws.on("pong", () => { ws.isAlive = true; });

  const keepAlive = setInterval(() => {
    if (ws.readyState !== ws.OPEN) return;
    if (!ws.isAlive) {
      logLine("connexion morte detectee (pas de pong), fermeture");
      ws.terminate();
      return;
    }
    ws.isAlive = false;
    ws.ping();
  }, 20000);

  ws.send(JSON.stringify({ type: "state", state: "listening" }));

  if (lastMessages.size > 0) {
    for (const [pid, m] of lastMessages) {
      ws.send(JSON.stringify({ type: "assistant.text", project: pid, mid: m.mid, text: m.text, awaitValidation: m.awaitValidation, options: m.options, recommended: m.recommended }));
      if (m.audio) {
        ws.send(JSON.stringify({ type: "assistant.audio", project: pid, mid: m.mid, audio: m.audio, mime: m.mime }));
      }
    }
    lastMessages.clear();
  }

  ws.on("message", (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      return;
    }

    console.log("Recu:", msg);

    const RATE_RULES = {
      "client.log": ["log", 120, 60 * 1000],
      "user.message": ["message", 30, 60 * 1000],
      "user.validation": ["message", 30, 60 * 1000],
      "user.image": ["upload", 10, 10 * 60 * 1000],
      "user.file": ["upload", 10, 10 * 60 * 1000]
    };
    const rule = RATE_RULES[msg.type];
    if (rule && !allowRate(rule[0], rule[1], rule[2])) {
      logLine(`limite de debit atteinte: ${msg.type}`);
      return;
    }

    if (msg.type === "client.log") {
      const line = `${new Date().toISOString()}\t[DEBUG] ${oneLine(msg.text)}\n`;
      fs.appendFile(MESSAGES_LOG, line, "utf8", () => {});
      return;
    }

    if (msg.type === "client.visible") {
      ws.lastVisible = Date.now();
      return;
    }

    if (msg.type === "client.sleep") {
      if (!ALLOW_REMOTE_SLEEP) {
        logLine("client.sleep refuse: ALLOW_REMOTE_SLEEP desactive");
        ws.send(JSON.stringify({
          type: "assistant.text", project: DEFAULT_PROJECT.id, mid: nextMid(),
          text: "Mise en veille à distance désactivée sur le PC (ALLOW_REMOTE_SLEEP)."
        }));
        return;
      }
      const now = Date.now();
      if (now - lastSleepRequest < 5000) return;
      lastSleepRequest = now;
      logLine("client.sleep: mise en veille du PC demandee");
      const cmd = process.platform === "win32"
        ? "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        : "systemctl suspend";
      exec(cmd, (err) => {
        if (err) logLine(`client.sleep echec: ${err.message}`);
      });
      return;
    }

    if (msg.type === "user.message") {
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      if (!resolveProject(msg.project)) {
        logLine(`user.message projet inconnu (${oneLine(msg.project)}), defaut ${project.id}`);
      }
      const channel = msg.channel === "vocal" ? "vocal" : "texte";
      const text = oneLine(msg.text).trim();
      if (!text) return;
      const bang = /^!\s*(\S+)/.exec(text);
      if (bang && !BANG_ALLOWLIST.includes(bang[1].toLowerCase())) {
        logLine(`commande refusee (${project.id}): !${bang[1].slice(0, 40)}`);
        ws.send(JSON.stringify({ type: "message.ack", id: msg.id }));
        ws.send(JSON.stringify({
          type: "assistant.text", project: project.id, mid: nextMid(),
          text: `Commande !${bang[1].slice(0, 40)} refusée par le serveur. Autorisées : ${BANG_ALLOWLIST.map((c) => "!" + c).join(", ")}.`
        }));
        ws.send(JSON.stringify({ type: "state", state: "listening" }));
        return;
      }
      if (channel === "vocal" && VOCAL_GROUP_MS > 0) {
        ws.send(JSON.stringify({ type: "message.ack", id: msg.id }));
        ws.send(JSON.stringify({ type: "signal", kind: "recu", project: project.id }));
        bufferVocal(project, text);
        ws.send(JSON.stringify({ type: "state", state: "processing" }));
        return;
      }

      flushVocal(project);
      writeUserLine(project, text, channel);
      ws.send(JSON.stringify({ type: "message.ack", id: msg.id }));
      ws.send(JSON.stringify({ type: "state", state: "processing" }));
    }

    if (msg.type === "user.image") {
      const match = /^data:([^;]+);base64,(.+)$/.exec(msg.data || "");
      if (!match) return;
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      const mime = match[1];
      const b64 = match[2];
      const buf = Buffer.from(b64, "base64");
      if (buf.length === 0 || buf.length > 8 * 1024 * 1024) {
        logLine(`user.image rejete: taille ${buf.length} (${project.id})`);
        return;
      }
      const ext = (mime.split("/")[1] || "png").replace(/[^a-z0-9]/gi, "").slice(0, 8) || "png";
      fs.mkdirSync(project.captures, { recursive: true });
      const filename = `${new Date().toISOString().replace(/[:.]/g, "-")}.${ext}`;
      const target = path.join(project.captures, filename);
      fs.writeFile(target, buf, () => {});

      const caption = msg.caption ? ` ${oneLine(msg.caption)}` : "";
      const line = `${new Date().toISOString()}\t[IMAGE]${caption} -> ${target}\n`;
      fs.appendFile(projectLog(project), line, "utf8", () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
      return;
    }

    if (msg.type === "user.file") {
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      const content = typeof msg.content === "string" ? msg.content : "";
      if (!content) return;
      if (Buffer.byteLength(content, "utf8") > 8 * 1024 * 1024) {
        logLine(`user.file rejete: trop volumineux (${project.id})`);
        return;
      }
      try {
        JSON.parse(content);
      } catch {
        logLine(`user.file rejete: JSON invalide (${project.id})`);
        return;
      }
      let base = path.basename(String(msg.name || "fichier.json")).replace(/[^\w.-]/g, "_");
      if (!/\.json$/i.test(base)) base += ".json";
      const filesDir = path.join(path.dirname(project.captures), "fichiers");
      fs.mkdirSync(filesDir, { recursive: true });
      const filename = `${new Date().toISOString().replace(/[:.]/g, "-")}__${base}`;
      const target = path.join(filesDir, filename);
      fs.writeFile(target, content, "utf8", () => {});

      const caption = msg.caption ? ` ${oneLine(msg.caption)}` : "";
      const line = `${new Date().toISOString()}\t[FICHIER]${caption} -> ${target}\n`;
      fs.appendFile(projectLog(project), line, "utf8", () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
      return;
    }

    if (msg.type === "user.validation") {
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      const label = msg.value === "ok" ? "Validation : ok" : "Validation : a corriger";
      const line = `${new Date().toISOString()}\t${label}\n`;
      fs.appendFile(projectLog(project), line, "utf8", () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
    }
  });

  ws.on("close", () => {
    clearInterval(keepAlive);
    console.log(`[${new Date().toISOString()}] Client deconnecte`);
  });
});

httpServer.listen(PORT, BIND_HOST, () => {
  console.log(`Serveur HTTP + WebSocket demarre sur ${BIND_HOST}:${PORT}`);
});
