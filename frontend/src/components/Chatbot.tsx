'use client';

import { FormEvent, useMemo, useState, ReactNode } from "react";
import clsx from "clsx";
import styles from "./Chatbot.module.css";

type Message = {
  id: string;
  variant: "user" | "assistant";
  text: string;
};

export type ChatbotProps = {
  apiUrl?: string;
  heading?: string;
  tagline?: string;
  introMessage?: string;
  className?: string;
};

const DEFAULTS = {
  heading: "Claude Assistant",
  tagline: "Your AI partner for hackathon success.",
  introMessage:
    "Welcome!, How can I help you?"
} as const;

/**
 * Formats response text to look awesome with bullet points, bold text, and clean formatting
 */
function formatResponseText(text: string): ReactNode {
  if (!text) return text;

  // Clean up the text: remove extra whitespace, normalize line breaks
  let cleaned = text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  // Split into blocks (either paragraphs separated by double newlines, or list groups)
  const blocks: Array<{ type: 'list' | 'paragraph'; items?: string[]; isNumbered?: boolean; content?: string }> = [];
  const parts = cleaned.split(/\n\n+/);

  parts.forEach(part => {
    part = part.trim();
    if (!part) return;

    const lines = part.split('\n').filter(line => line.trim().length > 0);
    
    // Check if all lines are list items (bullet or numbered)
    const isBulletList = lines.length > 0 && lines.every(line => /^[-*•]\s+/.test(line.trim()));
    const isNumberedList = lines.length > 0 && lines.every(line => /^\d+[.)]\s+/.test(line.trim()));
    
    if (isBulletList) {
      const items = lines.map(line => line.replace(/^[-*•]\s+/, '').trim()).filter(item => item.length > 0);
      if (items.length > 0) {
        blocks.push({ type: 'list', items, isNumbered: false });
      }
    } else if (isNumberedList) {
      const items = lines.map(line => line.replace(/^\d+[.)]\s+/, '').trim()).filter(item => item.length > 0);
      if (items.length > 0) {
        blocks.push({ type: 'list', items, isNumbered: true });
      }
    } else {
      // Regular paragraph
      blocks.push({ type: 'paragraph', content: part });
    }
  });

  return (
    <>
      {blocks.map((block, idx) => {
        if (block.type === 'list' && block.items) {
          const ListComponent = block.isNumbered ? 'ol' : 'ul';
          const listClass = block.isNumbered ? styles.numberedList : styles.bulletList;
          return (
            <ListComponent key={idx} className={listClass}>
              {block.items.map((item, itemIdx) => (
                <li key={itemIdx}>
                  {formatInlineText(item)}
                </li>
              ))}
            </ListComponent>
          );
        } else if (block.content) {
          return (
            <p key={idx}>
              {formatInlineText(block.content)}
            </p>
          );
        }
        return null;
      })}
    </>
  );
}

/**
 * Formats inline text with bold, italic, and code formatting
 */
function formatInlineText(text: string): ReactNode {
  if (!text) return text;

  // Process in order: code blocks first (to avoid conflicts), then bold, then italic
  const parts: Array<string | ReactNode> = [text];
  let keyCounter = 0;

  // Process code blocks first (backticks)
  const processedParts: Array<string | ReactNode> = [];
  parts.forEach(part => {
    if (typeof part === 'string') {
      const codeRegex = /`([^`]+)`/g;
      let lastIndex = 0;
      let match;
      
      while ((match = codeRegex.exec(part)) !== null) {
        // Add text before code
        if (match.index > lastIndex) {
          processedParts.push(part.substring(lastIndex, match.index));
        }
        // Add code element
        processedParts.push(
          <code key={`code-${keyCounter++}`} className={styles.inlineCode}>
            {match[1]}
          </code>
        );
        lastIndex = match.index + match[0].length;
      }
      // Add remaining text
      if (lastIndex < part.length) {
        processedParts.push(part.substring(lastIndex));
      }
    } else {
      processedParts.push(part);
    }
  });

  // Process bold text (**text**)
  const boldParts: Array<string | ReactNode> = [];
  processedParts.forEach(part => {
    if (typeof part === 'string') {
      const boldRegex = /\*\*([^*]+)\*\*/g;
      let lastIndex = 0;
      let match;
      
      while ((match = boldRegex.exec(part)) !== null) {
        if (match.index > lastIndex) {
          boldParts.push(part.substring(lastIndex, match.index));
        }
        boldParts.push(<strong key={`bold-${keyCounter++}`}>{match[1]}</strong>);
        lastIndex = match.index + match[0].length;
      }
      if (lastIndex < part.length) {
        boldParts.push(part.substring(lastIndex));
      }
    } else {
      boldParts.push(part);
    }
  });

  // Process italic text (*text*) - but not if it's part of bold
  const finalParts: Array<string | ReactNode> = [];
  boldParts.forEach(part => {
    if (typeof part === 'string') {
      const italicRegex = /\*([^*]+)\*/g;
      let lastIndex = 0;
      let match;
      
      while ((match = italicRegex.exec(part)) !== null) {
        if (match.index > lastIndex) {
          finalParts.push(part.substring(lastIndex, match.index));
        }
        finalParts.push(<em key={`italic-${keyCounter++}`}>{match[1]}</em>);
        lastIndex = match.index + match[0].length;
      }
      if (lastIndex < part.length) {
        finalParts.push(part.substring(lastIndex));
      }
    } else {
      finalParts.push(part);
    }
  });

  return <>{finalParts.length > 0 ? finalParts : text}</>;
}

export function Chatbot({
  apiUrl = "http://localhost:8000/api/chat",
  heading = DEFAULTS.heading,
  tagline = DEFAULTS.tagline,
  introMessage = DEFAULTS.introMessage,
  className
}: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>(() => [
    {
      id: crypto.randomUUID(),
      variant: "assistant",
      text: introMessage
    }
  ]);
  const [question, setQuestion] = useState("");
  const [isSubmitting, setSubmitting] = useState(false);

  const statusLabel = useMemo(
    () => (isSubmitting ? "Thinking..." : "Send"),
    [isSubmitting]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      variant: "user",
      text: trimmed
    };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setSubmitting(true);

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed })
      });

      if (!response.ok) {
        let detail: string | undefined;
        try {
          const payload = await response.json();
          detail = payload?.detail;
        } catch {
          // ignore
        }
        throw new Error(
          detail ?? "Claude is unavailable at the moment. Please try again soon."
        );
      }

      const data = (await response.json()) as { answer: string };
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          variant: "assistant",
          text: data.answer
        }
      ]);
    } catch (error) {
      const fallback =
        error instanceof Error && error.message
          ? error.message
          : "Unexpected error. Please retry in a moment.";
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          variant: "assistant",
          text: fallback
        }
      ]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={clsx(styles.wrapper, className)}>
      <div className={styles.header}>
        <div>
          <h2>{heading}</h2>
          <p>{tagline}</p>
        </div>
        <span className={styles.statusDot} aria-hidden />
      </div>

      <div className={styles.chatLog} role="log" aria-live="polite">
        {messages.map((message) => (
          <article
            key={message.id}
            className={clsx(
              styles.message,
              message.variant === "user" && styles.messageUser
            )}
          >
            <div className={styles.avatar} aria-hidden>
              {message.variant === "user" ? "YOU" : "AI"}
            </div>
            <div className={styles.messageBody}>
              <h3>
                {message.variant === "user" ? "You" : "Claude"}
              </h3>
              <div className={styles.messageContent}>
                {message.variant === "assistant" 
                  ? formatResponseText(message.text)
                  : <p>{message.text}</p>
                }
              </div>
            </div>
          </article>
        ))}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <label htmlFor="chat-question" className={styles.srOnly}>
          Your question
        </label>
        <textarea
          id="chat-question"
          name="question"
          rows={2}
          placeholder="How can I optimize my project workflow?"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={isSubmitting}
          required
        />
        <button type="submit" disabled={isSubmitting}>
          <span>{statusLabel}</span>
          <span
            className={clsx(styles.spinner, isSubmitting && styles.spinnerVisible)}
            aria-hidden
          />
        </button>
      </form>
    </section>
  );
}

