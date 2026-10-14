const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.webp': 'image/webp',
  '.pdf': 'application/pdf'
};

const server = http.createServer((req, res) => {
  let urlPath = decodeURI(req.url.split('?')[0]);

  // Handle /api/chat
  if (urlPath === '/api/chat' || urlPath === '/api/chat/') {
    if (req.method === 'OPTIONS') {
      res.writeHead(200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      });
      res.end();
      return;
    }

    if (req.method === 'POST') {
      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', () => {
        try {
          const parsed = JSON.parse(body || '{}');
          const message = parsed.message || '';
          const userId = parsed.user_id || req.socket.remoteAddress || 'guest';
          
          const { spawn } = require('child_process');
          const py = spawn('python', [
            '-c',
            'import chatbot_service, json, sys; res = chatbot_service.process_chat(sys.argv[1], sys.argv[2]); print(json.dumps(res))',
            message,
            userId
          ], { env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });

          let output = '';
          py.stdout.on('data', d => { output += d.toString('utf-8'); });
          py.on('close', code => {
            res.writeHead(200, {
              'Content-Type': 'application/json; charset=utf-8',
              'Access-Control-Allow-Origin': '*'
            });
            if (code === 0 && output.trim()) {
              res.end(output.trim());
            } else {
              res.end(JSON.stringify({
                success: true,
                answer: "**Hello! 👋 Welcome to Haseeb Rehman's Portfolio!**\n\nHaseeb is a **Senior Full-Stack & SaaS Web Developer** with 3+ years of experience and 50+ projects delivered.\n\nYou can reach him directly on [WhatsApp (+92 326 8795099)](https://wa.me/923268795099) or [Email](mailto:haseebrehman3460@gmail.com)!",
                provider: "local-default"
              }));
            }
          });
        } catch (e) {
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
          res.end(JSON.stringify({ success: true, answer: "Hello! How can I assist you with Haseeb's portfolio today?", provider: "local-default" }));
        }
      });
      return;
    }
  }

  if (urlPath === '/') {
    urlPath = '/index.html';
  }

  let filePath = path.join(__dirname, urlPath);

  // Clean URLs support (matching Vercel routing): try .html or /index.html
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    if (fs.existsSync(filePath + '.html')) {
      filePath = filePath + '.html';
    } else if (fs.existsSync(path.join(filePath, 'index.html'))) {
      filePath = path.join(filePath, 'index.html');
    }
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      const notFoundPath = path.join(__dirname, '404.html');
      if (fs.existsSync(notFoundPath)) {
        res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
        fs.createReadStream(notFoundPath).pipe(res);
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
      }
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    const headers = { 'Content-Type': contentType };
    if (ext === '.pdf') {
      headers['Content-Disposition'] = 'attachment; filename="Haseeb_Rehman_CV.pdf"';
    }
    res.writeHead(200, headers);
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
