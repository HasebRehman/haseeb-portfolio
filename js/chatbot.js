/**
 * Haseeb Rehman Portfolio — AI Chatbot Controller
 * - Bottom-right floating widget matching website theme
 * - Dual AI failover backend (/api/chat)
 * - Zero-error fallback to local knowledge base
 * - Portfolio-only scope guardrails & per-user quota handling
 * - Session & chat history persistence across page navigation
 */

(function () {
  'use strict';

  // Configuration
  const CONFIG = {
    apiEndpoint: '/api/chat',
    storagePrefix: 'hsb_ai_chat_',
    maxHistoryStored: 20,
    minTypingDelayMs: 1100,
    welcomeMessage: `**Hi there! 👋 Welcome to Haseeb Rehman's Portfolio.**\n\nI'm Haseeb's dedicated AI Assistant. I can tell you about his full-stack & SaaS experience, technical skills, live projects, or help you connect with him directly.\n\nWhat would you like to explore?`,
    suggestions: [
      { label: '💼 Services Offered', query: 'What services does Haseeb offer?' },
      { label: '🚀 Featured Projects', query: 'Show me projects built by Haseeb' },
      { label: '⚡ Tech Stack & Skills', query: 'What is Haseeb\'s tech stack and skills?' },
      { label: '📞 Hire / Contact Haseeb', query: 'How can I hire or contact Haseeb?' },
      { label: '📄 Download CV', query: 'Where can I download Haseeb\'s CV?' }
    ]
  };

  // Client-side emergency fallback (in case network itself fails completely)
  const CLIENT_FALLBACKS = {
    contact: `**Connect with Haseeb Rehman 🚀**\n\n• **WhatsApp:** [+92 326 8795099](https://wa.me/923268795099)\n• **Email:** [haseebrehman3460@gmail.com](mailto:haseebrehman3460@gmail.com)\n• **LinkedIn:** [linkedin.com/in/haseebrehmanweb](https://www.linkedin.com/in/haseebrehmanweb/)\n• **GitHub:** [github.com/HasebRehman](https://github.com/HasebRehman)`,
    projects: `**Featured Projects by Haseeb 💼**\n\n1. **[Veylohr](https://veylohr.com/)** — Full-stack scalable HR management SaaS.\n2. **[Lizzt](https://lizzt.app/)** — Collaborative event app with real-time tracking.\n3. **[VendoSphere](https://ecommerce-one-tau-62.vercel.app/)** — Modern e-commerce web platform.\n4. **[Pakhims](https://pakhims.com/)** — Hospital brand portal & healthcare management web app.`,
    skills: `**Haseeb's Core Stack ⚡**\n\n• **Frontend:** React, Next.js, TypeScript, Tailwind CSS, Bootstrap, GSAP.\n• **Backend:** Node.js, NestJS, Express, Python, REST APIs, Microservices.\n• **Databases:** PostgreSQL, MongoDB, Supabase, Redis.\n• **AI Integrations:** Gemini, OpenAI, Groq, custom chat assistants.`,
    general: `**Haseeb Rehman — Senior Full-Stack & SaaS Developer**\n\nWith 3+ years of experience and 50+ delivered projects, Haseeb specializes in building custom SaaS platforms, modern web apps, and AI integrations. You can reach him directly on [WhatsApp (+92 326 8795099)](https://wa.me/923268795099)!`
  };

  // State
  let isOpen = false;
  let isSending = false;
  let userId = '';
  let chatHistory = [];

  // Helper: Generate or retrieve persistent User ID
  function getUserId() {
    try {
      let storedId = localStorage.getItem(CONFIG.storagePrefix + 'user_id');
      if (!storedId) {
        storedId = 'usr_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();
        localStorage.setItem(CONFIG.storagePrefix + 'user_id', storedId);
      }
      return storedId;
    } catch (e) {
      return 'usr_guest_' + Date.now();
    }
  }

  // Helper: Load history
  function loadHistory() {
    try {
      const data = localStorage.getItem(CONFIG.storagePrefix + 'history');
      if (data) {
        return JSON.parse(data);
      }
    } catch (e) {}
    return [];
  }

  // Helper: Save history
  function saveHistory(messages) {
    try {
      const trimmed = messages.slice(-CONFIG.maxHistoryStored);
      localStorage.setItem(CONFIG.storagePrefix + 'history', JSON.stringify(trimmed));
    } catch (e) {}
  }

  // Helper: Format Markdown to HTML safely
  function formatMarkdown(text) {
    if (!text) return '';
    let html = text;

    // Escape raw HTML entities to prevent XSS
    html = html
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Links: [text](url)
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

    // Bullet points (• or - )
    const lines = html.split('\n');
    let inList = false;
    let result = [];

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      if (line.startsWith('• ') || line.startsWith('- ') || line.startsWith('* ')) {
        if (!inList) {
          result.push('<ul>');
          inList = true;
        }
        result.push('<li>' + line.substring(2) + '</li>');
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        if (line.length > 0) {
          result.push('<p>' + line + '</p>');
        }
      }
    }

    if (inList) {
      result.push('</ul>');
    }

    return result.join('');
  }

  // Inject UI Markup
  function createChatWidget() {
    if (document.getElementById('hsbChatWidgetContainer')) return;

    const container = document.createElement('div');
    container.id = 'hsbChatWidgetContainer';
    container.innerHTML = `
      <!-- Floating Launcher Button -->
      <button id="hsbChatLauncher" class="hsb-chat-launcher" aria-label="Open Haseeb's AI Assistant" title="Chat with Haseeb's AI">
        <span class="hsb-launcher-beacon" aria-hidden="true"></span>
        <i class="fa-solid fa-comments hsb-launcher-icon-chat"></i>
        <i class="fa-solid fa-xmark hsb-launcher-icon-close"></i>
      </button>

      <!-- Tooltip Notification / Callout Badge -->
      <div id="hsbChatTooltip" class="hsb-chat-tooltip" role="button" aria-label="Chat with Haseeb's AI" title="Click to chat with Haseeb's AI">
        <span class="hsb-tooltip-sparkle">✨</span>
        <span class="hsb-tooltip-text">Chat with Haseeb's AI</span>
      </div>

      <!-- Chat Window -->
      <div id="hsbChatWindow" class="hsb-chat-window" role="dialog" aria-modal="true" aria-label="Haseeb Rehman AI Assistant">
        <!-- Header -->
        <div class="hsb-chat-header">
          <div class="hsb-header-profile">
            <div class="hsb-avatar-wrapper">
              <div class="hsb-avatar-circle">
                <video class="hsb-avatar-video" src="images/AI Chatbot.mp4" autoplay loop muted playsinline></video>
              </div>
              <span class="hsb-avatar-status" title="Active"></span>
            </div>
            <div class="hsb-header-info">
              <div class="hsb-header-title">Haseeb Rehman</div>
              <div class="hsb-header-subtitle">
                <span class="status-indicator"></span>
                <span>Online &bull; Instant Answers</span>
              </div>
            </div>
          </div>
          <div class="hsb-header-actions">
            <button id="hsbResetChatBtn" class="hsb-action-btn" title="Clear Conversation" aria-label="Reset chat">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button id="hsbCloseChatBtn" class="hsb-action-btn" title="Close" aria-label="Close chat">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <!-- Body / Messages -->
        <div id="hsbChatBody" class="hsb-chat-body"></div>

        <!-- Footer / Input -->
        <div class="hsb-chat-footer">
          <div class="hsb-input-wrapper">
            <input type="text" id="hsbChatInput" class="hsb-chat-input" placeholder="Ask about Haseeb's work or skills..." autocomplete="off">
            <button id="hsbSendBtn" class="hsb-send-btn" aria-label="Send message">
              <i class="fa-solid fa-paper-plane"></i>
            </button>
          </div>
          <div class="hsb-footer-disclaimer">
            <span>Portfolio Assistant</span>
            <a href="https://wa.me/923268795099" target="_blank" rel="noopener noreferrer">WhatsApp Direct &rarr;</a>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(container);
  }

  // Render a message into the DOM
  function appendMessageToUI(role, content, timeStr) {
    const chatBody = document.getElementById('hsbChatBody');
    if (!chatBody) return;

    const row = document.createElement('div');
    row.className = 'hsb-msg-row ' + (role === 'user' ? 'is-user' : 'is-bot');

    const formattedHtml = formatMarkdown(content);
    const timeDisplay = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (role === 'user') {
      row.innerHTML = `
        <div class="hsb-msg-bubble">
          ${formattedHtml}
          <div class="hsb-msg-meta">${timeDisplay}</div>
        </div>
      `;
    } else {
      row.innerHTML = `
        <div class="hsb-bot-avatar-mini">
          <video class="hsb-avatar-video" src="images/AI Chatbot.mp4" autoplay loop muted playsinline></video>
        </div>
        <div class="hsb-msg-bubble">
          ${formattedHtml}
          <div class="hsb-msg-meta">${timeDisplay}</div>
        </div>
      `;
    }

    chatBody.appendChild(row);

    const v = row.querySelector('video');
    if (v) {
      v.muted = true;
      v.play().catch(() => {});
    }

    scrollToBottom();
  }

  // Render suggestion chips
  function appendSuggestionsToUI() {
    const chatBody = document.getElementById('hsbChatBody');
    if (!chatBody) return;

    const existing = document.getElementById('hsbSuggestionsContainer');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.id = 'hsbSuggestionsContainer';
    box.className = 'hsb-suggestions-box';

    CONFIG.suggestions.forEach(item => {
      const chip = document.createElement('button');
      chip.className = 'hsb-chip-btn';
      chip.textContent = item.label;
      chip.addEventListener('click', () => {
        box.remove();
        handleUserSend(item.query);
      });
      box.appendChild(chip);
    });

    chatBody.appendChild(box);
    scrollToBottom();
  }

  // Typing Indicator
  function showTypingIndicator() {
    const chatBody = document.getElementById('hsbChatBody');
    if (!chatBody || document.getElementById('hsbTypingIndicatorRow')) return;

    const row = document.createElement('div');
    row.id = 'hsbTypingIndicatorRow';
    row.className = 'hsb-msg-row is-bot';
    row.innerHTML = `
      <div class="hsb-bot-avatar-mini">
        <video class="hsb-avatar-video" src="images/AI Chatbot.mp4" autoplay loop muted playsinline></video>
      </div>
      <div class="hsb-typing-indicator">
        <div class="hsb-typing-dot"></div>
        <div class="hsb-typing-dot"></div>
        <div class="hsb-typing-dot"></div>
      </div>
    `;

    chatBody.appendChild(row);

    const v = row.querySelector('video');
    if (v) {
      v.muted = true;
      v.play().catch(() => {});
    }

    scrollToBottom();
  }

  function removeTypingIndicator() {
    const row = document.getElementById('hsbTypingIndicatorRow');
    if (row) row.remove();
  }

  function scrollToBottom() {
    const chatBody = document.getElementById('hsbChatBody');
    if (chatBody) {
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  }

  // Toggle open/close
  function toggleChat(open) {
    isOpen = typeof open === 'boolean' ? open : !isOpen;
    const launcher = document.getElementById('hsbChatLauncher');
    const windowEl = document.getElementById('hsbChatWindow');
    const tooltip = document.getElementById('hsbChatTooltip');

    if (isOpen) {
      launcher.classList.add('is-open');
      windowEl.classList.add('is-open');
      if (tooltip) tooltip.classList.remove('is-visible');

      // Ensure animated robot avatar video plays smoothly
      windowEl.querySelectorAll('video').forEach(vid => {
        vid.muted = true;
        vid.play().catch(() => {});
      });

      setTimeout(() => {
        const input = document.getElementById('hsbChatInput');
        if (input) input.focus();
        scrollToBottom();
      }, 150);
    } else {
      launcher.classList.remove('is-open');
      windowEl.classList.remove('is-open');
      if (tooltip) tooltip.classList.add('is-visible');
    }
  }

  // Send message flow
  async function handleUserSend(textToSend) {
    if (isSending) return;

    const input = document.getElementById('hsbChatInput');
    const sendBtn = document.getElementById('hsbSendBtn');
    const message = (textToSend || (input ? input.value : '')).trim();

    if (!message) return;

    if (input) input.value = '';
    isSending = true;
    if (sendBtn) sendBtn.disabled = true;

    // Remove any floating suggestion buttons
    const suggestions = document.getElementById('hsbSuggestionsContainer');
    if (suggestions) suggestions.remove();

    // 1. Add user message to UI & history
    const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    appendMessageToUI('user', message, nowStr);
    chatHistory.push({ role: 'user', content: message, time: nowStr });
    saveHistory(chatHistory);

    // 2. Show typing indicator (3 animated bouncing dots)
    showTypingIndicator();
    const sendStartTime = Date.now();

    try {
      // 3. Send to backend endpoint
      const response = await fetch(CONFIG.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          user_id: userId,
          history: chatHistory.slice(-6).map(m => ({ role: m.role, content: m.content }))
        })
      });

      if (!response.ok) {
        throw new Error('Server returned ' + response.status);
      }

      const data = await response.json();
      const botReply = data.answer || CLIENT_FALLBACKS.general;

      // Realistic typing delay: ensure 3 dots remain visible for at least minTypingDelayMs
      const elapsed = Date.now() - sendStartTime;
      if (elapsed < CONFIG.minTypingDelayMs) {
        await new Promise(resolve => setTimeout(resolve, CONFIG.minTypingDelayMs - elapsed));
      }

      removeTypingIndicator();

      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      appendMessageToUI('assistant', botReply, botTime);
      chatHistory.push({ role: 'assistant', content: botReply, time: botTime });
      saveHistory(chatHistory);

    } catch (err) {
      // Emergency Client Fallback (Zero error screen guarantee)
      const q = message.toLowerCase();
      let fallbackText = CLIENT_FALLBACKS.general;

      if (q.includes('contact') || q.includes('hire') || q.includes('whatsapp') || q.includes('email')) {
        fallbackText = CLIENT_FALLBACKS.contact;
      } else if (q.includes('project') || q.includes('work') || q.includes('portfolio')) {
        fallbackText = CLIENT_FALLBACKS.projects;
      } else if (q.includes('skill') || q.includes('stack') || q.includes('tech') || q.includes('react')) {
        fallbackText = CLIENT_FALLBACKS.skills;
      }

      // Maintain typing delay on fallback too so user experience is consistent
      const elapsed = Date.now() - sendStartTime;
      if (elapsed < CONFIG.minTypingDelayMs) {
        await new Promise(resolve => setTimeout(resolve, CONFIG.minTypingDelayMs - elapsed));
      }

      removeTypingIndicator();

      const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      appendMessageToUI('assistant', fallbackText, botTime);
      chatHistory.push({ role: 'assistant', content: fallbackText, time: botTime });
      saveHistory(chatHistory);
    } finally {
      isSending = false;
      if (sendBtn) sendBtn.disabled = false;
      if (input) input.focus();
    }
  }

  // Reset Conversation
  async function resetConversation() {
    chatHistory = [];
    saveHistory([]);
    const chatBody = document.getElementById('hsbChatBody');
    if (chatBody) chatBody.innerHTML = '';

    showTypingIndicator();
    await new Promise(resolve => setTimeout(resolve, 850));
    removeTypingIndicator();

    appendMessageToUI('assistant', CONFIG.welcomeMessage);
    appendSuggestionsToUI();
  }

  // Initialization
  function initChat() {
    userId = getUserId();
    createChatWidget();

    const launcher = document.getElementById('hsbChatLauncher');
    const closeBtn = document.getElementById('hsbCloseChatBtn');
    const resetBtn = document.getElementById('hsbResetChatBtn');
    const sendBtn = document.getElementById('hsbSendBtn');
    const input = document.getElementById('hsbChatInput');
    const tooltip = document.getElementById('hsbChatTooltip');

    // Load conversation or welcome with dynamic typing feel
    chatHistory = loadHistory();
    if (chatHistory.length > 0) {
      chatHistory.forEach(item => {
        appendMessageToUI(item.role, item.content, item.time);
      });
    } else {
      showTypingIndicator();
      setTimeout(() => {
        removeTypingIndicator();
        appendMessageToUI('assistant', CONFIG.welcomeMessage);
        appendSuggestionsToUI();
      }, 850);
    }

    // Event listeners
    if (launcher) launcher.addEventListener('click', () => toggleChat());
    if (closeBtn) closeBtn.addEventListener('click', () => toggleChat(false));
    if (resetBtn) resetBtn.addEventListener('click', resetConversation);

    if (sendBtn) {
      sendBtn.addEventListener('click', () => handleUserSend());
    }

    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          handleUserSend();
        }
      });
    }

    // Show callout badge right after page opens so visitors immediately notice it
    setTimeout(() => {
      if (!isOpen && tooltip) {
        tooltip.classList.add('is-visible');
      }
    }, 400);

    // Clicking the badge opens the chat
    if (tooltip) {
      tooltip.addEventListener('click', () => toggleChat(true));
    }
  }

  // Boot after DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChat);
  } else {
    initChat();
  }
})();
