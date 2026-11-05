# Sky Sparks: hosting and instructions

## Files

- `index.html` — student page and interactive competition screen.
- `host.html` — private host sign-in page.
- `server.py` — Python backend for joining, approval, questions, scores and timer. Serves both pages.
- `render.yaml` — optional Render Blueprint configuration.

**Important:** This needs a Python web service that runs continuously. Uploading only HTML files to a static hosting service will not work: students need the shared backend. Use one server instance because game data is stored in memory.

## Deploy on Render (example)

1. Create a GitHub repository and upload these four files to its root (not inside another folder). You may also include this README.
2. At https://render.com create an account, choose **New → Web Service**, and connect your GitHub repository.
3. Choose Python as the language/runtime. The app has no external packages. If a build command is required, enter `python -m compileall .`. Set the start command to `python server.py`.
4. In Environment, add `HOST_SECRET` and set it to a long, hard-to-guess password (for example, 24 or more random letters and numbers). Never share this password with students. The platform supplies `PORT`; do not hard-code it.
5. Deploy. Set the service to **one instance**. Wait until the deployment is live and copy the site's HTTPS URL, such as `https://your-app.onrender.com`.
6. Host: open `https://your-app.onrender.com/host` and enter the host password. Student link: `https://your-app.onrender.com/`. Replace the example address with your actual URL. The preview address shown by Arena is protected and is not your public deployment.
7. Have students open the student link on their own devices, enter names and wait. On the host dashboard approve up to five players, select the timer, then click Start challenge. Everyone may click Enable sound on their own device.

Alternatively, Render's Blueprint feature can use `render.yaml`; set the requested `HOST_SECRET` when prompted. Platform options, free availability, sleep behaviour and pricing may change. A sleeping server can take time to wake up.

## Test on one computer

Install Python 3.9 or newer. Open a terminal in this folder and run:

    python server.py

Open http://localhost:8000/host. The terminal prints a temporary host link containing the host password; copy the value after `host=` into the host sign-in page. Open http://localhost:8000/ in a different browser or a private window to act as a student. To choose your own stable password, set the `HOST_SECRET` environment variable before starting the server.

For other devices on the same Wi-Fi, replace localhost with the server computer's LAN IP address, and allow port 8000 through the firewall. `localhost` on a student's phone refers to the phone, not your computer. For play over the internet use a public HTTPS web host instead.

## Game details

Each student starts with five Diwali questions, then gets original Grade 7 NCERT-aligned practice questions in maths, English and science. These are not verbatim textbook questions. Wrong answers advance to the next question. A correct ordinary answer is worth one spark. Once a student has at least six correct answers and averages at most 20 seconds per correct answer, equations may appear, worth three sparks each. The shared sky shows a growing anar fountain and rocket fireworks; an equation makes the sky flash especially bright. Sound is optional and must be enabled separately on each device.

## Limitations and safety

- Restarting or redeploying the server clears the current round and players. A free service may sleep. This is a prototype, not a persistent tournament platform.
- Use one instance only; multiple independent instances would have separate games.
- Keep the host password private. The dashboard URL contains it, so do not share that URL or screenshots of it. Use HTTPS in production. This simple prototype does not include accounts, rate limiting, durable storage, or hardened production security.
- The animations and sounds are virtual; no real fireworks are needed.
