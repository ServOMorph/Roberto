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
const CAPTURES_DIR = path.join(__dirname, "..", "..", "..", "..", "_docs", "captures");

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

let lastMessage = null;

const SALUTATIONS_FILE = path.join(__dirname, "salutations.json");
let salutations = [];
try {
  salutations = JSON.parse(fs.readFileSync(SALUTATIONS_FILE, "utf8"));
} catch {
  salutations = [];
}

const GREETING_RE = /^(bonjour|salut|coucou|hello|hey|yo|bonsoir)\b/i;

function replyWithGreeting(ws) {
  if (salutations.length === 0) return;
  const text = salutations[Math.floor(Math.random() * salutations.length)];

  fs.appendFile(MESSAGES_LOG, `${new Date().toISOString()}\t[AUTO] ${text}\n`, () => {});

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
      if (ws.readyState === ws.OPEN) {
        ws.send(JSON.stringify({ type: "assistant.text", text }));
        ws.send(JSON.stringify({ type: "assistant.audio", audio: audioB64, mime: audioMime }));
        ws.send(JSON.stringify({ type: "state", state: "listening" }));
      }
    });
  });

  ttsReq.on("error", () => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: "assistant.text", text }));
      ws.send(JSON.stringify({ type: "state", state: "listening" }));
    }
  });

  ttsReq.end(JSON.stringify({ text }));
}

function sendPushNotification(text) {
  if (!VAPID_PUBLIC || !VAPID_PRIVATE) return Promise.resolve({ skipped: true, results: [] });
  const payload = JSON.stringify({ title: "Assistant", body: text });
  const jobs = [...pushSubs.values()].map((sub) => {
    return webpush.sendNotification(sub, payload, { TTL: 300 })
      .then((res) => ({ endpoint: sub.endpoint, statusCode: res.statusCode }))
      .catch((err) => {
        if (err.statusCode === 404 || err.statusCode === 410) {
          pushSubs.delete(sub.endpoint);
          saveSubs();
        }
        return { endpoint: sub.endpoint, error: err.statusCode || err.message, body: String(err.body || "").slice(0, 300) };
      });
  });
  return Promise.all(jobs).then((results) => ({ count: jobs.length, results }));
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
      let text, mode, awaitValidation;
      try {
        const parsed = JSON.parse(body);
        text = parsed.text;
        mode = parsed.mode;
        awaitValidation = !!parsed.awaitValidation;
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }

      if (mode === "texte") {
        let sent = 0;
        wss.clients.forEach((client) => {
          if (client.readyState === client.OPEN) {
            client.send(JSON.stringify({ type: "assistant.text", text, awaitValidation }));
            client.send(JSON.stringify({ type: "state", state: "listening" }));
            sent++;
          }
        });
        if (sent === 0) {
          lastMessage = { text, audio: null, mime: null, awaitValidation };
          sendPushNotification(text).catch(() => {});
        } else {
          lastMessage = null;
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ sent }));
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

          let sent = 0;
          wss.clients.forEach((client) => {
            if (client.readyState === client.OPEN) {
              client.send(JSON.stringify({ type: "assistant.text", text, awaitValidation }));
              client.send(JSON.stringify({ type: "assistant.audio", audio: audioB64, mime: audioMime }));
              sent++;
            }
          });

          if (sent === 0) {
            lastMessage = { text, audio: audioB64, mime: audioMime, awaitValidation };
            sendPushNotification(text).catch(() => {});
          } else {
            lastMessage = null;
          }

          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ sent }));
        });
      });

      ttsReq.on("error", () => {
        let sent = 0;
        wss.clients.forEach((client) => {
          if (client.readyState === client.OPEN) {
            client.send(JSON.stringify({ type: "assistant.text", text, awaitValidation }));
            client.send(JSON.stringify({ type: "state", state: "listening" }));
            sent++;
          }
        });
        if (sent === 0) {
          lastMessage = { text, audio: null, mime: null, awaitValidation };
          sendPushNotification(text).catch(() => {});
        } else {
          lastMessage = null;
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ sent, tts: "indisponible" }));
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
      let sub;
      try {
        sub = JSON.parse(body);
      } catch {
        res.writeHead(400);
        res.end("Corps invalide");
        return;
      }
      if (!sub || !sub.endpoint) {
        res.writeHead(400);
        res.end("Abonnement invalide");
        return;
      }
      pushSubs.set(sub.endpoint, sub);
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

  const keepAlive = setInterval(() => {
    if (ws.readyState === ws.OPEN) {
      ws.ping();
    }
  }, 20000);

  ws.send(JSON.stringify({ type: "state", state: "listening" }));

  let firstMessage = true;

  if (lastMessage) {
    ws.send(JSON.stringify({ type: "assistant.text", text: lastMessage.text, awaitValidation: lastMessage.awaitValidation }));
    if (lastMessage.audio) {
      ws.send(JSON.stringify({ type: "assistant.audio", audio: lastMessage.audio, mime: lastMessage.mime }));
    }
    lastMessage = null;
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

    if (msg.type === "user.message") {
      const channel = msg.channel === "vocal" ? "vocal" : "texte";
      const line = `${new Date().toISOString()}\t${msg.text}\t[canal:${channel}]\n`;
      const isGreetingTrigger = firstMessage && GREETING_RE.test((msg.text || "").trim());
      firstMessage = false;

      fs.appendFile(MESSAGES_LOG, line, () => {
        ws.send(JSON.stringify({ type: "message.ack", id: msg.id }));
      });

      ws.send(JSON.stringify({ type: "state", state: "processing" }));

      if (isGreetingTrigger) {
        replyWithGreeting(ws);
      }
    }

    if (msg.type === "user.image") {
      const match = /^data:([^;]+);base64,(.+)$/.exec(msg.data || "");
      if (!match) return;
      const mime = match[1];
      const b64 = match[2];
      const ext = mime.split("/")[1] || "png";
      fs.mkdirSync(CAPTURES_DIR, { recursive: true });
      const filename = `${new Date().toISOString().replace(/[:.]/g, "-")}.${ext}`;
      fs.writeFile(path.join(CAPTURES_DIR, filename), Buffer.from(b64, "base64"), () => {});

      const caption = msg.caption ? ` ${msg.caption}` : "";
      const line = `${new Date().toISOString()}\t[IMAGE]${caption} -> _docs/captures/${filename}\n`;
      fs.appendFile(MESSAGES_LOG, line, () => {});

      ws.send(JSON.stringify({ type: "state", state: "processing" }));
      return;
    }

    if (msg.type === "user.validation") {
      const label = msg.value === "ok" ? "Validation : ok" : "Validation : a corriger";
      const line = `${new Date().toISOString()}\t${label}\n`;
      fs.appendFile(MESSAGES_LOG, line, () => {});

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
