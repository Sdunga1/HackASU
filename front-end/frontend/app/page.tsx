'use client';

import styles from "./page.module.css";
import { Chatbot } from "@/components/Chatbot";

const envApiUrl =
  typeof process !== "undefined" && process.env
    ? process.env.NEXT_PUBLIC_CHAT_API_URL
    : undefined;

const DEFAULT_API_URL = envApiUrl ?? "http://localhost:8000/api/chat";

export default function HomePage() {
  return (
    <main className={styles.page}>
      <Chatbot
        apiUrl={DEFAULT_API_URL}
        heading="Claude Assistant"
        tagline="Chaos to Clarity."
        introMessage="Welcome!, How can I help you?"
      />
    </main>
  );
}

