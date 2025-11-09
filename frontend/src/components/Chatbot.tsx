'use client';

import { FormEvent, useState, ReactNode, useEffect, useRef } from "react";
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
    "Hi! I'm Claude, your AI assistant. How can I help you today?"
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
  const chatLogRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages, isSubmitting]);

  const handleSendMessage = async () => {
    const trimmed = question.trim();
    if (!trimmed || isSubmitting) {
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
    
    // Reset textarea height
    setTimeout(() => {
      const textarea = document.getElementById('chat-question') as HTMLTextAreaElement;
      if (textarea) {
        textarea.style.height = 'auto';
      }
    }, 0);

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
  };

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await handleSendMessage();
  }

  return (
    <section className={clsx(styles.wrapper, className)}>
      {/* Modern Minimal Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.avatarContainer}>
            <div className={styles.avatarCircle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
          </div>
          <div className={styles.headerInfo}>
            <h2>{heading}</h2>
            <div className={styles.headerMeta}>
              <span className={styles.statusDot}></span>
              <span>Active now</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className={styles.chatLog} role="log" aria-live="polite" ref={chatLogRef}>
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={clsx(
              styles.messageGroup,
              message.variant === "user" && styles.messageGroupUser
            )}
          >
            {message.variant === "assistant" && (
              <div className={styles.avatar}>
                <div className={styles.avatarInitial}>C</div>
              </div>
            )}
            <div className={styles.messageContentWrapper}>
              <div
                className={clsx(
                  styles.messageBubble,
                  message.variant === "user" && styles.messageBubbleUser
                )}
              >
                <div className={styles.messageText}>
                  {message.variant === "assistant" 
                    ? formatResponseText(message.text)
                    : <p>{message.text}</p>
                  }
                </div>
              </div>
            </div>
            {message.variant === "user" && (
              <div className={styles.avatar}>
                <div className={styles.avatarInitialUser}>U</div>
              </div>
            )}
          </div>
        ))}
        {isSubmitting && (
          <div className={styles.messageGroup}>
            <div className={styles.avatar}>
              <div className={styles.avatarInitial}>C</div>
            </div>
            <div className={styles.messageContentWrapper}>
              <div className={styles.messageBubble}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modern Input Area */}
      <div className={styles.inputArea}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputContainer}>
            <textarea
              id="chat-question"
              name="question"
              rows={1}
              placeholder="Message Claude..."
              value={question}
              onChange={(event) => {
                setQuestion(event.target.value);
                event.target.style.height = 'auto';
                event.target.style.height = `${Math.min(event.target.scrollHeight, 120)}px`;
              }}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={isSubmitting}
              className={styles.textarea}
            />
            <button
              type="submit"
              disabled={isSubmitting || !question.trim()}
              className={styles.sendButton}
              aria-label="Send message"
            >
              {isSubmitting ? (
                <div className={styles.spinner}></div>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}

