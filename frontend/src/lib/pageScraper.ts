/**
 * Page Scraper Utility
 * Extracts meaningful content from the current page for AI context
 */

export interface PageContext {
  url: string;
  title: string;
  content: string;
  timestamp: number;
  pageType: string;
}

/**
 * Scrapes the current page and extracts meaningful content
 */
export function scrapePageContent(): PageContext {
  const url = window.location.href;
  const title = document.title;
  
  // Extract main content, excluding navigation, headers, footers
  const mainContent = extractMainContent();
  
  // Determine page type based on URL or content
  const pageType = determinePageType(url);
  
  return {
    url,
    title,
    content: mainContent,
    timestamp: Date.now(),
    pageType,
  };
}

/**
 * Extracts main content from the page, excluding nav, headers, footers
 */
function extractMainContent(): string {
  // Try to find main content areas
  const mainSelectors = [
    'main',
    '[role="main"]',
    '.main-content',
    '.content',
    '#content',
    'article',
    '.page-content',
  ];
  
  let mainElement: Element | null = null;
  
  for (const selector of mainSelectors) {
    mainElement = document.querySelector(selector);
    if (mainElement) break;
  }
  
  // If no main element found, use body but exclude common non-content elements
  if (!mainElement) {
    mainElement = document.body;
  }
  
  // Clone to avoid modifying the original
  const clone = mainElement.cloneNode(true) as Element;
  
  // Remove unwanted elements
  const elementsToRemove = clone.querySelectorAll(
    'nav, header, footer, aside, .navbar, .header, .footer, .sidebar, ' +
    'script, style, .chatbot, .chat, [class*="chat"], [id*="chat"]'
  );
  
  elementsToRemove.forEach((el) => el.remove());
  
  // Extract text content
  const textContent = clone.textContent || '';
  
  // Clean up: remove excessive whitespace, normalize line breaks
  const cleaned = textContent
    .replace(/\s+/g, ' ')
    .replace(/\n\s*\n/g, '\n')
    .trim();
  
  // Limit content length to avoid token limits (keep first 8000 characters)
  const maxLength = 8000;
  const truncated = cleaned.length > maxLength 
    ? cleaned.substring(0, maxLength) + '... [content truncated]'
    : cleaned;
  
  return truncated;
}

/**
 * Determines the page type based on URL or content
 */
function determinePageType(url: string): string {
  const pathname = new URL(url).pathname;
  
  if (pathname.includes('/dashboard')) return 'dashboard';
  if (pathname.includes('/issues')) return 'issues';
  if (pathname.includes('/narrative')) return 'narrative';
  if (pathname.includes('/anomaly')) return 'anomaly';
  if (pathname === '/' || pathname === '') return 'home';
  
  return 'unknown';
}

/**
 * Extracts structured data from the page (tables, lists, etc.)
 */
export function extractStructuredData(): {
  headings: string[];
  links: Array<{ text: string; href: string }>;
  buttons: string[];
  tables: string[];
} {
  const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
    .map((h) => h.textContent?.trim() || '')
    .filter((h) => h.length > 0);
  
  const links = Array.from(document.querySelectorAll('a[href]'))
    .map((a) => ({
      text: a.textContent?.trim() || '',
      href: (a as HTMLAnchorElement).href,
    }))
    .filter((l) => l.text.length > 0);
  
  const buttons = Array.from(document.querySelectorAll('button, [role="button"]'))
    .map((b) => b.textContent?.trim() || '')
    .filter((b) => b.length > 0);
  
  const tables = Array.from(document.querySelectorAll('table'))
    .map((table) => {
      const rows = Array.from(table.querySelectorAll('tr'))
        .map((row) => {
          const cells = Array.from(row.querySelectorAll('td, th'))
            .map((cell) => cell.textContent?.trim() || '');
          return cells.join(' | ');
        })
        .filter((row) => row.length > 0);
      return rows.join('\n');
    })
    .filter((table) => table.length > 0);
  
  return {
    headings,
    links,
    buttons,
    tables,
  };
}

/**
 * Creates a summary of the page context for AI
 * Optimized for professional, PM-focused responses
 */
export function createPageContextSummary(context: PageContext): string {
  const structured = extractStructuredData();
  
  // Detect active tab/section in dashboard
  let activeSection = '';
  try {
    // Check for active tab indicators
    const activeTabElement = document.querySelector('[class*="active"][class*="tab"], [aria-selected="true"], button[class*="active"]');
    if (activeTabElement) {
      activeSection = activeTabElement.textContent?.trim() || '';
    }
    
    // Also check for visible tab content
    const tabPanels = document.querySelectorAll('[role="tabpanel"], [class*="tab-panel"], [class*="tab-content"]');
    for (const panel of Array.from(tabPanels)) {
      const style = window.getComputedStyle(panel);
      if (style.display !== 'none' && style.visibility !== 'hidden') {
        const heading = panel.querySelector('h1, h2, h3');
        if (heading) {
          activeSection = heading.textContent?.trim() || activeSection;
        }
      }
    }
  } catch (e) {
    // Ignore errors in section detection
  }
  
  // Build concise context summary without verbose headers
  let summary = '';
  
  // Add active section if detected
  if (activeSection) {
    summary += `Current Section: ${activeSection}\n\n`;
  }
  
  // Add key metrics and data from the page
  if (context.content) {
    // Extract key metrics and information from content
    summary += context.content;
  }
  
  // Add structured data if available (tables, headings)
  if (structured.tables.length > 0) {
    if (summary) summary += '\n\n';
    summary += structured.tables.slice(0, 2).join('\n\n');
  }
  
  // Add key headings for context (but only if not too many)
  if (structured.headings.length > 0 && structured.headings.length <= 8) {
    if (summary) summary += '\n\n';
    summary += `Sections: ${structured.headings.slice(0, 8).join(', ')}`;
  }
  
  return summary.trim();
}

