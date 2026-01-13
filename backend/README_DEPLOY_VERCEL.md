## Deploying the FastAPI backend to Vercel (Docker)

This project contains a FastAPI backend in `backend/`.
The simplest reliable way to host it on Vercel is using a Docker build.

Steps:

1. Install the Vercel CLI (if you haven't already):

```bash
npm i -g vercel
```

2. Ensure the `backend/Dockerfile` and `vercel.json` are present (they are included in this repo).

3. Add environment variables in the Vercel Project settings (Environment Variables):

- `MAIL_SERVER` (e.g. `smtp.gmail.com`)
- `MAIL_PORT` (e.g. `587`)
- `MAIL_USERNAME` (your SMTP username)
- `MAIL_PASSWORD` (your SMTP app password)
- `ADMIN_EMAIL` (admin@novashield.in)

Do NOT commit real secrets to source control — use the Vercel dashboard to set them.

4. Deploy with Vercel CLI (interactive):

```bash
cd /path/to/repo
vercel login
vercel --prod
```

Vercel will detect `vercel.json` and build the Docker image using `@vercel/docker`.

5. After deployment, open the deployment URL. The FastAPI app will be available at the root. You can use `/api/health` to verify the service.

Notes and troubleshooting:
- If Vercel build fails due to Docker or builder constraints, consider deploying to Render, Railway, or Fly which have native Docker support.
- Alternatively, you can containerize the app and deploy to a container host (e.g., Google Cloud Run, AWS ECS, Azure Container Instances).
- For local testing before deploying:

```bash
cd backend
pip install -r requirements.txt
# create .env locally from .env.example
python app.py
# or run via uvicorn
uvicorn app:app --reload --port 5000
```
