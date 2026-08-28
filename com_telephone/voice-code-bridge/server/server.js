const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
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
    sendPushNotification(payload.text, `${project.label} · Assistant`).catch(() => {});
  }
  return { sent, push: !foreground };
}

function logLine(text) {
  fs.appendFile(MESSAGES_LOG, `${new Date().toISOString()}\t[DEBUG] ${text}\n`, () => {});
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

function isLoopback(req) {
  const addr = req.socket.remoteAddress;
  return addr === "127.0.0.1" || addr === "::1" || addr === "::ffff:127.0.0.1";
}

const httpServer = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/send") {
    if (!isLoopback(req)) {
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
    if (!isAuthed(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    req.on("end", () => {
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
    if (!isAuthed(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    req.on("end", () => {
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
    if (!isLoopback(req)) {
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
    if (!isAuthed(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      const audio = Buffer.concat(chunks);

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
    if (!isAuthed(req)) {
      res.writeHead(401);
      res.end("Non autorise");
      return;
    }
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    req.on("end", () => {
      let text;
      try {
        text = JSON.parse(body).text;
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }

      const line = `${new Date().toISOString()}\t[DEBUG] ${text}\n`;
      fs.appendFile(MESSAGES_LOG, line, () => {});

      res.writeHead(200);
      res.end("ok");
    });
    return;
  }

  if (req.method === "GET" && req.url.split("?")[0] === "/projects") {
    if (!isAuthed(req)) {
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

  if (!filePath.startsWith(MOBILE_DIR)) {
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
    if (url.searchParams.get("token")) {
      headers["Set-Cookie"] = `auth=${AUTH_TOKEN}; HttpOnly; SameSite=Strict; Max-Age=31536000; Path=/`;
    }
    res.writeHead(200, headers);
    res.end(content);
  });
});

const wss = new WebSocketServer({
  server: httpServer,
  verifyClient: (info, callback) => {
    const cookieToken = getCookie(info.req, "auth");
    callback(!!cookieToken && timingSafeEqualStr(cookieToken, AUTH_TOKEN));
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

    if (msg.type === "client.log") {
      const line = `${new Date().toISOString()}\t[DEBUG] ${msg.text}\n`;
      fs.appendFile(MESSAGES_LOG, line, () => {});
      return;
    }

    if (msg.type === "client.visible") {
      ws.lastVisible = Date.now();
      return;
    }

    if (msg.type === "user.message") {
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      if (!resolveProject(msg.project)) {
        logLine(`user.message projet inconnu (${msg.project}), defaut ${project.id}`);
      }
      const channel = msg.channel === "vocal" ? "vocal" : "texte";
      const line = `${new Date().toISOString()}\t${msg.text}\t[canal:${channel}]\n`;

      fs.appendFile(projectLog(project), line, () => {
        ws.send(JSON.stringify({ type: "message.ack", id: msg.id }));
      });

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
    }

    if (msg.type === "user.image") {
      const match = /^data:([^;]+);base64,(.+)$/.exec(msg.data || "");
      if (!match) return;
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      const mime = match[1];
      const b64 = match[2];
      const ext = mime.split("/")[1] || "png";
      fs.mkdirSync(project.captures, { recursive: true });
      const filename = `${new Date().toISOString().replace(/[:.]/g, "-")}.${ext}`;
      const target = path.join(project.captures, filename);
      fs.writeFile(target, Buffer.from(b64, "base64"), () => {});

      const caption = msg.caption ? ` ${msg.caption}` : "";
      const line = `${new Date().toISOString()}\t[IMAGE]${caption} -> ${target}\n`;
      fs.appendFile(projectLog(project), line, () => {});

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
      fs.writeFile(target, content, () => {});

      const caption = msg.caption ? ` ${msg.caption}` : "";
      const line = `${new Date().toISOString()}\t[FICHIER]${caption} -> ${target}\n`;
      fs.appendFile(projectLog(project), line, () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
      return;
    }

    if (msg.type === "user.validation") {
      const project = resolveProject(msg.project) || DEFAULT_PROJECT;
      const label = msg.value === "ok" ? "Validation : ok" : "Validation : a corriger";
      const line = `${new Date().toISOString()}\t${label}\n`;
      fs.appendFile(projectLog(project), line, () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
    }
  });

  ws.on("close", () => {
    clearInterval(keepAlive);
    console.log(`[${new Date().toISOString()}] Client deconnecte`);
  });
});

httpServer.listen(PORT, () => {
  console.log(`Serveur HTTP + WebSocket demarre sur le port ${PORT}`);
});
