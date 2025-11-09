/**
 * Context Storage Utility
 * Manages storage of page context for AI chat sessions
 */

import { PageContext } from './pageScraper';

const STORAGE_KEY = 'chat_page_context';
const CONTEXT_HISTORY_KEY = 'chat_context_history';
const MAX_HISTORY_LENGTH = 10; // Keep last 10 page contexts

export interface ContextHistoryItem {
  context: PageContext;
  messageCount: number;
}

/**
 * Stores the current page context
 */
export function storePageContext(context: PageContext): void {
  try {
    // Store current context
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(context));
    
    // Update history
    const history = getContextHistory();
    const existingIndex = history.findIndex(
      (item) => item.context.url === context.url
    );
    
    if (existingIndex >= 0) {
      // Update existing context
      history[existingIndex].context = context;
      history[existingIndex].messageCount += 1;
    } else {
      // Add new context
      history.unshift({
        context,
        messageCount: 1,
      });
      
      // Limit history length
      if (history.length > MAX_HISTORY_LENGTH) {
        history.pop();
      }
    }
    
    sessionStorage.setItem(CONTEXT_HISTORY_KEY, JSON.stringify(history));
  } catch (error) {
    console.error('Error storing page context:', error);
  }
}

/**
 * Retrieves the current page context
 */
export function getPageContext(): PageContext | null {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    
    return JSON.parse(stored) as PageContext;
  } catch (error) {
    console.error('Error retrieving page context:', error);
    return null;
  }
}

/**
 * Gets the context history
 */
export function getContextHistory(): ContextHistoryItem[] {
  try {
    const stored = sessionStorage.getItem(CONTEXT_HISTORY_KEY);
    if (!stored) return [];
    
    return JSON.parse(stored) as ContextHistoryItem[];
  } catch (error) {
    console.error('Error retrieving context history:', error);
    return [];
  }
}

/**
 * Clears the current page context
 */
export function clearPageContext(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing page context:', error);
  }
}

/**
 * Clears all context history
 */
export function clearContextHistory(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(CONTEXT_HISTORY_KEY);
  } catch (error) {
    console.error('Error clearing context history:', error);
  }
}

/**
 * Creates a brief summary of context history for AI
 */
export function createContextHistorySummary(): string {
  const history = getContextHistory();
  if (history.length === 0) return '';
  
  let summary = 'Recent Page Context History:\n';
  history.slice(0, 5).forEach((item, index) => {
    summary += `${index + 1}. ${item.context.title} (${item.context.url})\n`;
    summary += `   Messages: ${item.messageCount}, Type: ${item.context.pageType}\n`;
  });
  
  return summary;
}

/**
 * Checks if context has changed (new page)
 */
export function hasContextChanged(newContext: PageContext): boolean {
  const currentContext = getPageContext();
  if (!currentContext) return true;
  
  // Context changed if URL is different
  return currentContext.url !== newContext.url;
}

