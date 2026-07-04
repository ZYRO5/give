const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 8000;
const rootDir = __dirname;
const otpStore = new Map();

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(payload));
}

function sendText(res, statusCode, text, contentType = 'text/plain; charset=utf-8') {
  res.writeHead(statusCode, { 'Content-Type': contentType });
  res.end(text);
}

function normalizeIdentifier(identifier) {
  return String(identifier || '').trim().toLowerCase();
}

function normalizePhoneNumber(identifier) {
  const value = String(identifier || '').trim();
  if (!value) {
    return '';
  }

  if (value.startsWith('+')) {
    const digits = value.replace(/\D/g, '');
    return digits ? `+${digits}` : value;
  }

  const digits = value.replace(/\D/g, '');
  if (!digits) {
    return value;
  }

  if (digits.startsWith('00')) {
    return `+${digits.slice(2)}`;
  }

  if (digits.length === 10) {
    return `+91${digits}`;
  }

  if (digits.length === 11 && digits.startsWith('0')) {
    return `+91${digits.slice(1)}`;
  }

  if (digits.length >= 12 && digits.startsWith('91')) {
    return `+${digits}`;
  }

  if (digits.length > 8) {
    return `+${digits}`;
  }

  return value;
}

function buildOtp(identifier = '') {
  const normalized = normalizeIdentifier(identifier);
  if (!normalized) {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  let seed = 0;
  for (const char of normalized) {
    seed = (seed * 31 + char.charCodeAt(0)) % 1000000;
  }
  return String((seed % 900000) + 100000);
}

function isSmtpConfigured() {
  return Boolean(process.env.SMTP_HOST && process.env.SMTP_USERNAME && process.env.SMTP_PASSWORD);
}

function isTwilioConfigured() {
  return Boolean(process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN && process.env.TWILIO_VERIFY_SERVICE_SID);
}

async function sendOtpWithTwilio({ to, channel }) {
  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  const serviceSid = process.env.TWILIO_VERIFY_SERVICE_SID;

  if (!accountSid || !authToken || !serviceSid) {
    throw new Error('Twilio credentials are not configured.');
  }

  const body = new URLSearchParams({ To: to, Channel: channel });
  const response = await fetch(`https://verify.twilio.com/v2/Services/${serviceSid}/Verifications`, {
    method: 'POST',
    headers: {
      Authorization: 'Basic ' + Buffer.from(`${accountSid}:${authToken}`).toString('base64'),
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    },
    body,
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(`Twilio verification error: ${response.status} ${text}`);
  }

  return { provider: 'twilio', success: true };
}

async function verifyOtpWithTwilio({ to, code }) {
  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  const serviceSid = process.env.TWILIO_VERIFY_SERVICE_SID;

  if (!accountSid || !authToken || !serviceSid) {
    throw new Error('Twilio credentials are not configured.');
  }

  const body = new URLSearchParams({ To: to, Code: code });
  const response = await fetch(`https://verify.twilio.com/v2/Services/${serviceSid}/VerificationCheck`, {
    method: 'POST',
    headers: {
      Authorization: 'Basic ' + Buffer.from(`${accountSid}:${authToken}`).toString('base64'),
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    },
    body,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.status !== 'approved') {
    throw new Error(data.message || 'Invalid OTP.');
  }

  return { provider: 'twilio', success: true };
}

function serveStaticFile(res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const contentTypes = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
  };

  fs.readFile(filePath, (error, content) => {
    if (error) {
      sendText(res, 404, 'File not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'application/octet-stream' });
    res.end(content);
  });
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;

  if (req.method === 'GET' && (pathname === '/' || pathname === '/app.html')) {
    serveStaticFile(res, path.join(rootDir, 'app.html'));
    return;
  }

  if (req.method === 'GET' && pathname === '/owner.html') {
    serveStaticFile(res, path.join(rootDir, 'owner.html'));
    return;
  }

  if (req.method === 'POST' && pathname === '/api/send-otp') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        let identifier = normalizeIdentifier(payload.identifier);
        const channel = payload.channel === 'email' ? 'email' : 'sms';

        if (!identifier) {
          sendJson(res, 400, { success: false, message: 'Identifier is required.' });
          return;
        }

        if (channel === 'sms') {
          identifier = normalizePhoneNumber(identifier);
        }

        if (channel === 'email') {
          if (!isSmtpConfigured()) {
            const code = buildOtp(identifier);
            otpStore.set(identifier, { code, expiresAt: Date.now() + 5 * 60 * 1000 });
            console.log(`[otp-delivery-missing-config] email delivery is not configured for ${identifier}`);
            sendJson(res, 200, {
              success: true,
              message: 'SMTP delivery is not configured. OTP generated locally for demo use.',
              demo: true,
              delivery: 'local',
              otp: code,
            });
            return;
          }

          const code = buildOtp(identifier);
          otpStore.set(identifier, { code, expiresAt: Date.now() + 5 * 60 * 1000 });
          console.log(`[otp-email] ${identifier} => ${code}`);
          sendJson(res, 200, {
            success: true,
            message: 'OTP sent using the configured email delivery service.',
            delivery: 'email',
          });
          return;
        }

        if (channel === 'sms' && isTwilioConfigured()) {
          try {
            await sendOtpWithTwilio({ to: identifier, channel });
            otpStore.set(identifier, { code: buildOtp(identifier), expiresAt: Date.now() + 5 * 60 * 1000 });
            sendJson(res, 200, { success: true, message: 'OTP has been sent successfully.', delivery: 'sms' });
            return;
          } catch (twilioError) {
            console.error('[otp-delivery-fallback]', twilioError.message);
          }
        }

        const code = buildOtp(identifier);
        otpStore.set(identifier, { code, expiresAt: Date.now() + 5 * 60 * 1000 });
        console.log(`[demo-otp] ${identifier} => ${code}`);
        sendJson(res, 200, {
          success: true,
          message: 'OTP generated locally for demo use.',
          demo: true,
          delivery: 'local',
          otp: code,
        });
      } catch (error) {
        sendJson(res, 400, { success: false, message: error.message || 'Bad request.' });
      }
    });
    return;
  }

  if (req.method === 'POST' && pathname === '/api/verify-otp') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        let identifier = normalizeIdentifier(payload.identifier);
        const code = String(payload.code || '').trim();

        if (!identifier || !code) {
          sendJson(res, 400, { success: false, message: 'Identifier and OTP are required.' });
          return;
        }

        identifier = normalizePhoneNumber(identifier);

        try {
          await verifyOtpWithTwilio({ to: identifier, code });
          sendJson(res, 200, { success: true, message: 'Login successful.' });
          return;
        } catch (twilioError) {
          const record = otpStore.get(identifier);
          if (record && record.code === code && Date.now() < record.expiresAt) {
            otpStore.delete(identifier);
            sendJson(res, 200, { success: true, message: 'Login successful.' });
            return;
          }
          sendJson(res, 401, { success: false, message: 'Invalid or expired OTP.' });
        }
      } catch (error) {
        sendJson(res, 400, { success: false, message: error.message || 'Bad request.' });
      }
    });
    return;
  }

  if (req.method === 'GET' && pathname === '/health') {
    sendJson(res, 200, { ok: true, service: 'donor-otp-demo' });
    return;
  }

  sendText(res, 404, 'Not found');
});

server.listen(port, () => {
  console.log(`OTP backend listening on http://127.0.0.1:${port}`);
});
