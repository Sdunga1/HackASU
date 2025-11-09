# Claude Chatbot

An assistant that forwards user prompts to Anthropic's Claude API via a lightweight FastAPI proxy.

## Backend (`front-end/backend`)

### Prerequisites

- Python 3.11+
- Claude API key with access to the Messages API

### Setup

```bash
cd front-end/backend
python -m venv venv
.\venv\Scripts\activate        # On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file or export the key in your shell:

```bash
setx ANTHROPIC_API_KEY "<your_api_key>"   # PowerShell
# export ANTHROPIC_API_KEY="<your_api_key>"   # macOS/Linux
```

Run the API server:

```bash
uvicorn main:app --reload --port 8000
```

The Swagger UI is available at `http://localhost:8000/docs` and the chatbot endpoint at `POST /api/chat`.

## Frontend (`front-end/frontend`)

The new UI is a Next.js 14 + React application that exposes a reusable `Chatbot` component. The demo page (`app/page.tsx`) shows the component in context, while the component can be imported into any other React/Next application.

### Install dependencies & run locally

```bash
cd front-end/frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:3000`. The component expects the backend to be available at `http://localhost:8000/api/chat` unless overridden via the `NEXT_PUBLIC_CHAT_API_URL` environment variable.

### Embedding the React component

```tsx
import { Chatbot } from "@/components/Chatbot";

export function SupportPanel() {
  return (
    <Chatbot
      apiUrl="https://your-backend.example.com/api/chat"
      heading="Assistant"
      tagline="Ask anything about your build or project."
      introMessage="Welcome!, How can I help you?"
    />
  );
}
```

Multiple instances can coexist on the same page and maintain their own history. The component accepts optional props:

- `apiUrl` – backend endpoint override (`http://localhost:8000/api/chat` default)
- `heading` – card title override
- `tagline` – subtitle/description override
- `introMessage` – first assistant message override

## Architecture

1. **Frontend** collects user questions and posts them to the backend.
2. **FastAPI backend** validates input, enriches it with safe defaults, and forwards the prompt to Claude using the Messages API.
3. The assistant's answer is returned to the client and rendered in the chat timeline.

## Security Notes

- The Claude API key must never be committed to source control.
- Rate limiting and authentication are not implemented; deploy behind trusted entry-points for production.
- Add request logging and tracing as needed for observability.

