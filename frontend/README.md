# DevAI Manager Frontend

Next.js frontend application for DevAI Manager.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.example .env.local
```

3. Update `.env.local` with your API URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Features

- Interactive dashboard for project visualization
- Issue cards with status and assignment information
- Project statistics overview
- AI-powered recommendations (coming soon)

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Axios for API calls
- Recharts for data visualization

## Project Structure

```
frontend/
├── src/
│   ├── app/          # Next.js app router pages
│   ├── components/   # React components
│   └── lib/          # Utilities and API client
└── public/           # Static assets
```

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

