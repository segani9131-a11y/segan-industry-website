/* ========================================
   SEGAN INDUSTRY - FRONTEND JAVASCRIPT
   Main Application Logic & API Integration
   ======================================== */

// Configuration
// NOTE (2026-10-17): the legacy website API on Railway (segan-industry-website-production.up.railway.app)
// is retired — Railway returns 404 "Application not found" for every endpoint. All website features now
// work client-side; the chat widget uses the public, auth-free website chat endpoint below.
// (The /api/v1/agent/* endpoints require a Bearer token and their CORS does not allow the
// website origin, so the widget intentionally does NOT use them.)
const CONFIG = {
  // Public website chat endpoint: POST {message, session_id} -> {reply}
  liveChatUrl: 'https://seganindustry.duckdns.org/api/v1/website/chat',
  // Public website enquiry endpoints (auth-free; CORS-enabled for the website)
  liveQuoteUrl: 'https://seganindustry.duckdns.org/api/v1/website/quote',
  liveContactUrl: 'https://seganindustry.duckdns.org/api/v1/website/contact',
  companyName: 'Segan Industry Private Limited',
  gstin: '33AAECS1234F1Z5'
};

// Global State
const state = {
  currentPage: '',
  isLoading: false,
  toastContainer: null,
  chatWidget: null,
  mobileMenuOpen: false
};

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
  if (!state.toastContainer) {
    state.toastContainer = document.createElement('div');
    state.toastContainer.className = 'toast-container';
    document.body.appendChild(state.toastContainer);
  }

  const icons = {
    success: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
    error: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
    warning: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    info: '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
  };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    ${icons[type] || icons.info}
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
    </button>
  `;

  state.toastContainer.appendChild(toast);

  // Auto remove
  setTimeout(() => {
    toast.style.animation = 'slideInRight 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, duration);

  // Manual close
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.style.animation = 'slideInRight 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  });
}

/**
 * Show loading state
 */
function showLoading(element, show = true) {
  if (show) {
    element.classList.add('loading');
    element.disabled = true;
    const originalText = element.innerHTML;
    element.dataset.originalText = originalText;
    element.innerHTML = '<div class="spinner"></div>';
  } else {
    element.classList.remove('loading');
    element.disabled = false;
    if (element.dataset.originalText) {
      element.innerHTML = element.dataset.originalText;
    }
  }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount);
}

/**
 * Format number with commas
 */
function formatNumber(num) {
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get URL parameter
 */
function getUrlParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// ========================================
// API CLIENT
// ========================================

const api = {
  // The legacy website API is retired (Railway app gone — 404 for every endpoint).
  // Fail fast so page loaders fall through to their built-in static fallbacks cleanly.
  async request(endpoint, options = {}) {
    throw new Error(`Legacy website API retired — using static fallback (${endpoint})`);
  },

  // Quotation APIs
  async generateQuote(data) {
    return this.request('/quote', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async getQuote(id) {
    return this.request(`/quote/${id}`);
  },

  async listQuotes(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/quotes?${query}`);
  },

  // Product APIs
  async getProducts(category) {
    const query = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request(`/products${query}`);
  },

  async getProduct(id) {
    return this.request(`/products/${id}`);
  },

  async getCategories() {
    return this.request('/products/categories/list');
  },

  // Automation APIs
  async getAutomationServices() {
    return this.request('/automation');
  },

  async getAutomationService(id) {
    return this.request(`/automation/${id}`);
  },

  // Contact APIs
  async submitContact(data) {
    return this.request('/contact', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // AI Agent APIs
  async chatWithAgent(message, context = {}, sessionId = null) {
    return this.request('/agent', {
      method: 'POST',
      body: JSON.stringify({ message, context, session_id: sessionId })
    });
  },

  async getAgentHelp() {
    return this.request('/agent/help');
  },

  // Calculation APIs
  async compareMaterials(data) {
    return this.request('/calculate/material-comparison', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async calculateProfitLoss(data) {
    return this.request('/calculate/profit-loss', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async calculateGST(amount, isInterstate = false) {
    return this.request('/calculate/gst', {
      method: 'POST',
      body: JSON.stringify({ amount, is_interstate: isInterstate })
    });
  },

  async calculateEmployeeCosts(data = null) {
    return this.request('/calculate/employee-costs', {
      method: 'POST',
      body: JSON.stringify(data || {})
    });
  },

  async getInventoryStatus() {
    return this.request('/calculate/inventory');
  },

  async recommendMachinery(data) {
    return this.request('/calculate/machinery-recommendation', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async getProductionWorkflow(harnessType) {
    return this.request(`/calculate/workflow/${harnessType}`);
  },

  // Supplier APIs
  async getSuppliers(materialType) {
    const query = materialType ? `?material_type=${encodeURIComponent(materialType)}` : '';
    return this.request(`/suppliers${query}`);
  },

  // Company APIs
  async getCompanyInfo() {
    return this.request('/company');
  },

  async getGSTInfo() {
    return this.request('/company/gst');
  }
};

// ========================================
// NAVIGATION & HEADER
// ========================================

function initNavigation() {
  const header = document.querySelector('.header');
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  // Scroll effect
  window.addEventListener('scroll', debounce(() => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, 100));

  // Mobile menu toggle
  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
      navMenu.classList.toggle('open');
      mobileMenuBtn.setAttribute('aria-expanded', state.mobileMenuOpen);
    });
  }

  // Close mobile menu on link click
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (state.mobileMenuOpen) {
        state.mobileMenuOpen = false;
        navMenu.classList.remove('open');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  });

  // Active link highlighting
  const currentPath = window.location.pathname;
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (href !== 'index.html' && currentPath.startsWith(href))) {
      link.classList.add('active');
    }
  });
}

/**
 * Escape HTML and preserve line breaks for agent chat replies
 */
function safeChatText(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br>');
}

// ========================================
// CHAT WIDGET
// ========================================

function initChatWidget() {
  const chatToggle = document.querySelector('.chat-toggle');
  const chatWindow = document.querySelector('.chat-window');
  const chatClose = document.querySelector('.chat-close');
  const chatInput = document.querySelector('.chat-input');
  const chatSend = document.querySelector('.chat-send');
  const chatMessages = document.querySelector('.chat-messages');

  if (!chatToggle || !chatWindow) return;

  // Per-page-load session id, sent in every chat message body for the
  // backend conversation log.
  let sessionId = (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : 'web-' + Date.now() + '-' + Math.random().toString(36).slice(2);

  // Quick-reply starter chips (sent as user messages on click)
  const chatChips = document.createElement('div');
  chatChips.className = 'chat-chips';
  ['What products do you make?', 'How do I get a quote?', 'Where are you located?'].forEach(text => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chat-chip';
    chip.textContent = text;
    chip.addEventListener('click', () => {
      chatInput.value = text;
      sendMessage();
    });
    chatChips.appendChild(chip);
  });
  const chatHeader = chatWindow.querySelector('.chat-header');
  if (chatHeader) chatHeader.after(chatChips);

  function hideChatChips() {
    if (chatChips) chatChips.style.display = 'none';
  }

  chatToggle.addEventListener('click', () => {
    chatWindow.classList.toggle('open');
    if (chatWindow.classList.contains('open')) {
      chatInput.focus();
    }
  });

  if (chatClose) {
    chatClose.addEventListener('click', () => {
      chatWindow.classList.remove('open');
    });
  }

  function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    
    const avatarIcon = isUser 
      ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
      : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M8 21h8"></path><path d="M12 17v4"></path></svg>';

    messageDiv.innerHTML = `
      <div class="chat-message-avatar">${avatarIcon}</div>
      <div class="chat-message-content">${content}</div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    hideChatChips();
    chatInput.value = '';
    chatInput.disabled = true;
    chatSend.disabled = true;

    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot';
    typingDiv.innerHTML = `
      <div class="chat-message-avatar"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M8 21h8"></path><path d="M12 17v4"></path></svg></div>
      <div class="chat-message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      // Public website chat endpoint (no auth; CORS-enabled for the website).
      const response = await fetch(CONFIG.liveChatUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId })
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      typingDiv.remove();
      hideChatChips();
      addMessage(safeChatText(data.reply || ''));
    } catch (error) {
      console.info('Website chat endpoint unavailable; showing contact fallback.', error);
      typingDiv.remove();
      addMessage(
        'Thanks for reaching out! Our assistant is temporarily unavailable, but our team ' +
        'will be glad to help — email us at <a href="mailto:info@seganindustry.com">info@seganindustry.com</a> ' +
        'or visit our <a href="contact.html">contact page</a>.'
      );
    } finally {
      chatInput.disabled = false;
      chatSend.disabled = false;
      chatInput.focus();
    }
  }

  chatSend.addEventListener('click', sendMessage);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

// ========================================
// HOME PAGE
// ========================================

function initHomePage() {
  // Animate stats on scroll
  const statValues = document.querySelectorAll('.stat-value, .visual-stat-number');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateValue(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statValues.forEach(el => observer.observe(el));
}

function animateValue(element) {
  const text = element.textContent;
  const match = text.match(/([\d,]+)(\+?)/);
  if (!match) return;
  
  const target = parseInt(match[1].replace(/,/g, ''));
  const suffix = match[2];
  const duration = 2000;
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (target - start) * eased);
    
    element.textContent = formatNumber(current) + suffix;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// ========================================
// PRODUCTS PAGE
// ========================================

let allProducts = [];
let currentCategory = 'all';

async function initProductsPage() {
  try {
    showLoading(document.querySelector('.product-grid') || document.body, true);
    allProducts = await api.getProducts();
    renderProducts(allProducts);
    initProductTabs();
  } catch (error) {
    // Legacy API retired — static fallback is the normal path, not an error.
    console.info('Products: using static fallback.');
    renderProductFallback();
  } finally {
    showLoading(document.querySelector('.product-grid') || document.body, false);
  }
}

function renderProducts(products) {
  const grid = document.querySelector('.product-grid');
  if (!grid) return;

  if (products.length === 0) {
    grid.innerHTML = '<div class="loading">No products found</div>';
    return;
  }

  grid.innerHTML = products.map(product => `
    <article class="product-card" data-id="${product.id}">
      <div class="product-image">
        ${getProductIcon(product.category)}
      </div>
      <div class="product-content">
        <span class="product-category">${product.category}</span>
        <h3 class="product-title">${product.name}</h3>
        <p class="product-description">${product.description}</p>
        <div class="product-specs">
          ${product.specifications ? Object.entries(product.specifications).slice(0, 4).map(([key, value]) => 
            `<span class="spec-tag">${key}: ${Array.isArray(value) ? value.slice(0, 2).join(', ') : value}</span>`
          ).join('') : ''}
        </div>
        <div class="product-footer">
          ${product.base_price_range ? `<span class="product-price">${product.base_price_range}</span>` : ''}
          ${product.min_order_quantity ? `<span class="product-moq">MOQ: ${formatNumber(product.min_order_quantity)}</span>` : ''}
          <a href="quote.html?product=${product.id}" class="btn btn-outline btn-sm">Request Quote</a>
        </div>
      </div>
    </article>
  `).join('');

  // Add click handlers
  grid.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      window.location.href = `products.html?id=${id}`;
    });
  });
}

function getProductIcon(category) {
  const icons = {
    'Automotive': `<svg class="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.3-1.4.7L3 11c-.3.3-.5.7-.5 1.2v3c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle></svg>`,
    'EV': `<svg class="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.3-1.4.7L3 11c-.3.3-.5.7-.5 1.2v3c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle><line x1="12" y1="7" x2="12" y2="12"></line><path d="M9 10h6"></path></svg>`,
    'Industrial': `<svg class="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M6 7h12"></path><path d="M6 11h12"></path></svg>`,
    'Components': `<svg class="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="8" height="8" rx="1"></rect><rect x="14" y="3" width="8" height="8" rx="1"></rect><rect x="2" y="13" width="8" height="8" rx="1"></rect><rect x="14" y="13" width="8" height="8" rx="1"></rect></svg>`,
    'Custom': `<svg class="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>`
  };
  return icons[category] || icons['Custom'];
}

function initProductTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentCategory = tab.dataset.category;
      filterProducts(currentCategory);
    });
  });
}

function filterProducts(category) {
  let filtered = allProducts;
  if (category !== 'all') {
    filtered = allProducts.filter(p => p.category.toLowerCase() === category.toLowerCase());
  }
  renderProducts(filtered);
}

function getStaticProducts() {
  // Static catalog (used everywhere now that the legacy website API is retired).
  // Generic names/descriptions only — NO prices, NO invented specs/certifications.
  return [
    { id: 'PRD001', name: 'Automotive Wiring Harness — 2 Wheeler', description: 'Complete wiring harness for motorcycles and scooters.', category: 'Automotive' },
    { id: 'PRD002', name: 'Automotive Wiring Harness — 4 Wheeler', description: 'Full vehicle wiring harness for passenger cars.', category: 'Automotive' },
    { id: 'PRD003', name: 'Commercial Vehicle Wiring Harness', description: 'Heavy-duty wiring harness for commercial vehicles.', category: 'Automotive' },
    { id: 'PRD004', name: 'EV High-Voltage Battery Harness', description: 'High-voltage harness for EV battery systems.', category: 'EV' },
    { id: 'PRD005', name: 'EV Low-Voltage Control Harness', description: 'Low-voltage control and signal harness for electric vehicles.', category: 'EV' },
    { id: 'PRD006', name: 'EV Charging Port Harness', description: 'Charging inlet and port wiring harness for electric vehicles.', category: 'EV' },
    { id: 'PRD007', name: 'Industrial Control Panel Wiring Harness', description: 'Panel wiring harness for industrial control systems.', category: 'Industrial' },
    { id: 'PRD008', name: 'Industrial Sensor & Actuator Harness', description: 'Sensor and actuator wiring harness for factory automation.', category: 'Industrial' },
    { id: 'PRD009', name: 'Connector & Terminal Assemblies', description: 'Connector and terminal sub-assemblies built to drawing.', category: 'Components' },
    { id: 'PRD010', name: 'Custom Cable Assemblies', description: 'Custom cable assemblies made to customer specifications.', category: 'Components' },
    { id: 'PRD011', name: 'Custom-Engineered Wiring Harness', description: 'Fully custom wiring harness engineered to your drawings.', category: 'Custom' }
  ];
}

function renderProductFallback() {
  // Fallback static products if API fails
  allProducts = getStaticProducts();
  renderProducts(allProducts);
}

// ========================================
// PRODUCT DETAIL PAGE
// ========================================

async function initProductDetailPage() {
  const productId = getUrlParam('id');
  if (!productId) return;

  // Legacy API retired — resolve from the static catalog.
  const catalog = getStaticProducts();
  const product = catalog.find(p => p.id === productId);
  if (product) {
    renderProductDetail(product);
  } else {
    const container = document.querySelector('.product-detail');
    if (container) {
      container.innerHTML = '<div class="card"><h3>Product not found</h3>' +
        '<p>This product is not in our current catalog.</p>' +
        '<a href="products.html" class="btn btn-primary">Back to Products</a></div>';
    }
  }
}

function renderProductDetail(product) {
  const container = document.querySelector('.product-detail');
  if (!container) return;

  container.innerHTML = `
    <div class="product-detail-header">
      <span class="product-category">${product.category}</span>
      <h1>${product.name}</h1>
      <p class="product-description">${product.description}</p>
    </div>
    <div class="product-detail-grid">
      <div class="product-detail-main">
        <div class="product-image-large">
          ${getProductIcon(product.category)}
        </div>
        ${product.base_price_range ? `<div class="product-price-large">${product.base_price_range}</div>` : ''}
      </div>
      <div class="product-detail-sidebar">
        <div class="card">
          <h3>Specifications</h3>
          <dl class="spec-list">
            ${Object.entries(product.specifications || {}).map(([key, value]) => `
              <div class="spec-item">
                <dt>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</dt>
                <dd>${Array.isArray(value) ? value.join(', ') : value}</dd>
              </div>
            `).join('')}
          </dl>
        </div>
        <div class="card">
          <h3>Applications</h3>
          <ul class="application-list">
            ${(product.applications || []).map(app => `<li>${app}</li>`).join('')}
          </ul>
        </div>
        <div class="card">
          <h3>Certifications</h3>
          <ul class="cert-list">
            ${(product.certifications || []).map(cert => `<li>${cert}</li>`).join('')}
          </ul>
        </div>
        <div class="card">
          <h3>Order Information</h3>
          <dl class="order-info">
            ${product.min_order_quantity ? `<div><dt>Min Order Quantity</dt><dd>${formatNumber(product.min_order_quantity)} units</dd></div>` : ''}
            ${product.lead_time_days ? `<div><dt>Lead Time</dt><dd>${product.lead_time_days} days</dd></div>` : ''}
          </dl>
          <a href="quote.html?product=${product.id}" class="btn btn-primary btn-lg" style="width: 100%; margin-top: var(--space-md);">
            Request Quote
          </a>
        </div>
      </div>
    </div>
  `;
}

// ========================================
// AUTOMATION PAGE
// ========================================

let automationServicesCache = [];

async function initAutomationPage() {
  try {
    showLoading(document.querySelector('.automation-grid') || document.body, true);
    const services = await api.getAutomationServices();
    renderAutomationServices(services);
  } catch (error) {
    // Legacy API retired — static fallback is the normal path, not an error.
    console.info('Automation services: using static fallback.');
    renderAutomationFallback();
  } finally {
    showLoading(document.querySelector('.automation-grid') || document.body, false);
  }
}

function renderAutomationServices(services) {
  const grid = document.querySelector('.automation-grid');
  if (!grid) return;
  automationServicesCache = services;

  grid.innerHTML = services.map(service => `
    <article class="card automation-card">
      <div class="automation-header">
        <div class="automation-icon">
          ${getAutomationIcon(service.id)}
        </div>
        <h3 class="automation-title">${service.name}</h3>
      </div>
      <p class="automation-description">${service.description}</p>
      <ul class="automation-features">
        ${service.features.map(f => `<li>${f}</li>`).join('')}
      </ul>
      <div class="automation-technologies">
        ${service.technologies.map(t => `<span class="tech-tag">${t}</span>`).join('')}
      </div>
      <button class="btn btn-outline automation-cta" data-service="${service.id}">
        Learn More
      </button>
    </article>
  `).join('');

  // Add click handlers
  grid.querySelectorAll('.automation-cta').forEach(btn => {
    btn.addEventListener('click', () => {
      const serviceId = btn.dataset.service;
      showAutomationModal(serviceId);
    });
  });
}

function getAutomationIcon(serviceId) {
  const icons = {
    'AI_AGENT': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M9 7h6"></path><path d="M9 11h6"></path></svg>',
    'WORKFLOW_AUTO': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="2" y="14" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><path d="M9 10h6"></path><path d="M9 14h6"></path><path d="M9 18h6"></path></svg>',
    'INVENTORY_AUTO': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>',
    'QUALITY_AUTO': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
  };
  return icons[serviceId] || icons['AI_AGENT'];
}

function renderAutomationFallback() {
  // Fallback if API fails
  const services = [
    {
      id: 'AI_AGENT',
      name: 'AI-Powered Quotation Agent',
      description: 'Automated wiring harness quotation with real-time material pricing, GST calculation, and profit optimization',
      features: ['Instant quotes', 'Material price comparison', 'GST compliance', 'Profit optimization'],
      technologies: ['Python', 'FastAPI', 'OpenAI', 'Real-time pricing APIs']
    }
    // ... add more
  ];
  renderAutomationServices(services);
}

function showAutomationModal(serviceId) {
  // Inline details toggle — data already exists on the card's service entry.
  const service = automationServicesCache.find(svc => svc.id === serviceId);
  const btn = document.querySelector(`.automation-cta[data-service="${serviceId}"]`);
  const card = btn ? btn.closest('.automation-card') : null;
  if (!service || !card) return;

  let details = card.querySelector('.automation-details');
  if (details) {
    details.remove();
    btn.textContent = 'Learn More';
    return;
  }

  details = document.createElement('div');
  details.className = 'automation-details';
  details.innerHTML = `
    <h4>What is included</h4>
    <ul>${(service.features || []).map(f => `<li>${escapeHtml(f)}</li>`).join('')}</ul>
    <h4>Technologies</h4>
    <p>${(service.technologies || []).map(escapeHtml).join(' · ')}</p>
    <a href="quote.html" class="btn btn-primary">Request a Quote for this service</a>
  `;
  card.appendChild(details);
  btn.textContent = 'Show Less';
}

// ========================================
// ABOUT PAGE
// ========================================

async function initAboutPage() {
  try {
    const company = await api.getCompanyInfo();
    renderCompanyInfo(company);
  } catch (error) {
    // Legacy API retired; the about page carries its content statically.
    console.info('Company info: using static page content.');
  }
}

function renderCompanyInfo(company) {
  // Update page with company info
  const elements = {
    'company-name': company.name,
    'company-tagline': company.tagline,
    'company-address': company.address,
    'company-phone': company.phone,
    'company-email': company.email,
    'company-gstin': company.gstin,
    'company-pan': company.pan,
    'company-cin': company.cin
  };

  Object.entries(elements).forEach(([id, value]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  });
}

// ========================================
// CONTACT PAGE
// ========================================

function initContactPage() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitContactForm(form);
  });
}

async function submitContactForm(form) {
  // Form status element: create it if the page doesn't have one.
  let messageDiv = form.querySelector('.form-message');
  if (!messageDiv) {
    messageDiv = document.createElement('div');
    messageDiv.className = 'form-message';
    messageDiv.style.display = 'none';
    const submitBtnRef = form.querySelector('button[type="submit"]');
    if (submitBtnRef) submitBtnRef.after(messageDiv); else form.prepend(messageDiv);
  }
  const showFormMessage = (type, text) => {
    messageDiv.className = `form-message ${type}`;
    messageDiv.textContent = text;
    messageDiv.style.display = 'block';
  };

  const submitBtn = form.querySelector('button[type="submit"]');
  const formData = new FormData(form);

  // Map actual contact.html fields: firstName/lastName, inquiryType (no subject field).
  const firstName = (formData.get('firstName') || '').toString().trim();
  const lastName = (formData.get('lastName') || '').toString().trim();
  const name = `${firstName} ${lastName}`.trim();
  const email = (formData.get('email') || '').toString().trim();
  const phone = (formData.get('phone') || '').toString().trim();
  const company = (formData.get('company') || '').toString().trim();
  const contactType = (formData.get('inquiryType') || 'Enquiry').toString();
  const subject = contactType; // no dedicated subject field on the form
  const message = (formData.get('message') || '').toString().trim();

  if (!firstName || !email || !message) {
    showFormMessage('error', 'Please fill in your first name, email and message before continuing.');
    return;
  }

  const payload = { name, email, phone, company, contact_type: contactType, subject, message };

  // Primary: capture to the founder's system via the public backend endpoint.
  showLoading(submitBtn, true);
  try {
    const response = await fetch(CONFIG.liveContactUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    showFormMessage('success', 'Message received! We will get back to you shortly.');
    showToast('Message received! We will get back to you shortly.', 'success');
    form.reset();
  } catch (error) {
    // Fallback: open the visitor's email app with everything pre-filled so
    // the enquiry is never lost. Honest wording — never claim it was "sent".
    console.info('Contact endpoint unavailable; falling back to email app.', error);
    const body = [
      `Name: ${name}`,
      `Email: ${email}`,
      `Phone: ${phone || '-'}`,
      `Company: ${company || '-'}`,
      `Type: ${contactType}`,
      '',
      message
    ].join('\n');

    window.location.href =
      `mailto:info@seganindustry.com?subject=${encodeURIComponent(`${contactType}`)}&body=${encodeURIComponent(body)}`;

    showFormMessage('success', 'Our system is temporarily unavailable — your email app opened with the message ready to send. Just press Send so your enquiry is not lost.');
    showToast('Email app opened with your message ready to send', 'success');
  } finally {
    showLoading(submitBtn, false);
  }
}

// ========================================
// QUOTE PAGE
// ========================================

let quoteSessionId = null;

function initQuotePage() {
  const form = document.getElementById('quote-form');
  const harnessTypeSelect = document.getElementById('harness_type');
  const productParam = getUrlParam('product');

  if (!form) return;

  // Pre-fill product if from product page
  if (productParam) {
    // Could pre-select category based on product
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await generateQuote(form);
  });

  // Real-time validation
  form.querySelectorAll('input, select').forEach(input => {
    input.addEventListener('blur', validateField);
    input.addEventListener('input', () => {
      if (input.classList.contains('error')) {
        validateField({ target: input });
      }
    });
  });
}

function validateField(event) {
  const field = event.target;
  const errorEl = field.parentNode.querySelector('.field-error');
  
  if (field.required && !field.value.trim()) {
    field.classList.add('error');
    if (errorEl) errorEl.textContent = 'This field is required';
    return false;
  }
  
  if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
    field.classList.add('error');
    if (errorEl) errorEl.textContent = 'Please enter a valid email';
    return false;
  }
  
  if (field.type === 'tel' && field.value && !isValidPhone(field.value)) {
    field.classList.add('error');
    if (errorEl) errorEl.textContent = 'Please enter a valid phone number';
    return false;
  }
  
  field.classList.remove('error');
  if (errorEl) errorEl.textContent = '';
  return true;
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
  return /^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{4,6}$/.test(phone);
}

// The legacy AI pricing API is retired — the quote page is now an RFQ (Request
// for Quotation) flow: validate client-side, render a summary, and email it.
let lastRFQ = null;

async function generateQuote(form) {
  const submitBtn = form.querySelector('button[type="submit"]');
  const resultContainer = document.getElementById('quote-result');
  const infoPanel = document.getElementById('quote-info');

  // Client-side validation (form uses novalidate, so do it explicitly)
  if (!form.reportValidity()) {
    showToast('Please complete the required fields.', 'error');
    return;
  }

  showLoading(submitBtn, true);

  const formData = new FormData(form);

  // Collect checkbox values for special requirements
  const checkboxFields = ['shielding', 'waterproof', 'ultrasonic_weld', 'tape_wrap', 'testing', 'labeling'];
  const specialRequirements = [];

  checkboxFields.forEach(field => {
    if (formData.get(field) === 'true') {
      specialRequirements.push(field.replace(/_/g, ' '));
    }
  });

  // Add any text special requirements
  const textRequirements = formData.get('special_requirements');
  if (textRequirements) {
    specialRequirements.push(textRequirements);
  }

  const data = {
    customer_name: formData.get('customer_name'),
    customer_email: formData.get('customer_email'),
    customer_phone: formData.get('customer_phone'),
    company_name: formData.get('company_name') || '',
    harness_type: formData.get('harness_type'),
    quantity: parseInt(formData.get('quantity')),
    wire_length_meters: parseFloat(formData.get('wire_length_meters')),
    wire_gauge_mm2: parseFloat(formData.get('wire_gauge_mm2')),
    connector_count: parseInt(formData.get('connector_count')),
    terminal_count: parseInt(formData.get('terminal_count')),
    special_requirements: specialRequirements.length > 0 ? specialRequirements.join(', ') : 'None',
    delivery_location: formData.get('delivery_location'),
    expected_delivery_days: parseInt(formData.get('expected_delivery_days')) || 30
  };

  lastRFQ = data;

  // Primary: capture the RFQ in the founder's system.
  try {
    const response = await fetch(CONFIG.liveQuoteUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json().catch(() => ({}));
    const ref = result.reference_id || result.id || result.quote_id;
    renderRFQSummary(data, resultContainer);
    if (infoPanel) infoPanel.style.display = 'none';
    resultContainer.style.display = 'block';
    showToast('Request received! Our team will contact you shortly.' + (ref ? ` Reference: ${ref}` : ''), 'success');
  } catch (error) {
    // Fallback: keep the summary AND open the visitor's email app so the
    // enquiry is never lost.
    console.info('Quote endpoint unavailable; falling back to email app.', error);
    renderRFQSummary(data, resultContainer);
    if (infoPanel) infoPanel.style.display = 'none';
    resultContainer.style.display = 'block';
    showToast('Our system is temporarily unavailable — your email app is opening so the RFQ is not lost.', 'info');
    sendRFQByEmail();
  } finally {
    showLoading(submitBtn, false);
  }
}

function renderRFQSummary(data, container) {
  // NOTE: no price estimates here — pricing is done by the Segan team, not automated.
  const rows = [
    ['Name', escapeHtml(data.customer_name)],
    ['Email', escapeHtml(data.customer_email)],
    ['Phone', escapeHtml(data.customer_phone)],
    ['Company', escapeHtml(data.company_name || '-')],
    ['Harness Type', escapeHtml(data.harness_type)],
    ['Quantity', formatNumber(data.quantity)],
    ['Wire Length (m)', isNaN(data.wire_length_meters) ? '-' : data.wire_length_meters],
    ['Wire Gauge (mm²)', isNaN(data.wire_gauge_mm2) ? '-' : data.wire_gauge_mm2],
    ['Connectors', formatNumber(data.connector_count)],
    ['Terminals', formatNumber(data.terminal_count)],
    ['Special Requirements', escapeHtml(data.special_requirements)],
    ['Delivery Location', escapeHtml(data.delivery_location || 'Chennai, Tamil Nadu, India')],
    ['Expected Delivery (days)', data.expected_delivery_days],
  ];

  container.innerHTML = `
    <div class="quote-header">
      <div class="quote-id">Request for Quotation</div>
      <div class="quote-date">Date: ${new Date().toLocaleDateString('en-IN')}</div>
    </div>
    <div class="quote-customer">
      <h4>${escapeHtml(data.customer_name)}</h4>
      <p>${escapeHtml(data.customer_email)} | ${escapeHtml(data.harness_type)} Harness</p>
    </div>
    <div class="quote-items">
      ${rows.map(([k, v]) => `<div class="quote-item"><span>${k}</span><span></span><span></span><span>${v}</span></div>`).join('')}
    </div>
    <div class="quote-terms">
      <h4>What happens next</h4>
      <ul>
        <li>Our team reviews your specifications and responds with an itemized quotation.</li>
        <li>No automated pricing — every quote is prepared by our engineers.</li>
        <li>HSN Code: 8544 (Wiring Harness)</li>
      </ul>
    </div>
    <div class="quote-actions">
      <button class="btn btn-primary" onclick="sendRFQByEmail()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
        Send this RFQ by email
      </button>
      <button class="btn btn-outline" onclick="window.print()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Print / Save as PDF
      </button>
    </div>
  `;
}

function sendRFQByEmail() {
  if (!lastRFQ) {
    showToast('Please prepare an RFQ summary first.', 'error');
    return;
  }
  const d = lastRFQ;
  const body = [
    'Request for Quotation — Segan Industry',
    `Date: ${new Date().toLocaleDateString('en-IN')}`,
    '',
    `Name: ${d.customer_name}`,
    `Email: ${d.customer_email}`,
    `Phone: ${d.customer_phone}`,
    `Company: ${d.company_name || '-'}`,
    `Harness Type: ${d.harness_type}`,
    `Quantity: ${d.quantity}`,
    `Wire Length (m): ${isNaN(d.wire_length_meters) ? '-' : d.wire_length_meters}`,
    `Wire Gauge (mm²): ${isNaN(d.wire_gauge_mm2) ? '-' : d.wire_gauge_mm2}`,
    `Connectors: ${d.connector_count}`,
    `Terminals: ${d.terminal_count}`,
    `Special Requirements: ${d.special_requirements}`,
    `Delivery Location: ${d.delivery_location || 'Chennai, Tamil Nadu, India'}`,
    `Expected Delivery (days): ${d.expected_delivery_days}`,
  ].join('\n');

  window.location.href =
    `mailto:sales@seganindustry.com?subject=${encodeURIComponent(`RFQ: ${d.harness_type} Harness x ${d.quantity} — ${d.customer_name}`)}&body=${encodeURIComponent(body)}`;
  showToast('Your email app opened with the RFQ ready to send', 'success');
}

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(value);
  return div.innerHTML;
}

function shareQuote() {
  // Share the RFQ page
  if (navigator.share) {
    navigator.share({
      title: 'Request a Quote — Segan Industry',
      text: 'Request a wiring harness quotation from Segan Industry Private Limited',
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href);
    showToast('Link copied to clipboard!', 'success');
  }
}

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
  // Detect current page
  const path = window.location.pathname;
  const page = path.split('/').pop().replace('.html', '') || 'index';
  state.currentPage = page;

  // Initialize common components
  initNavigation();
  initChatWidget();

  // Page-specific initialization
  switch (page) {
    case 'index':
    case '':
      initHomePage();
      break;
    case 'products':
      if (getUrlParam('id')) {
        initProductDetailPage();
      } else {
        initProductsPage();
      }
      break;
    case 'automation':
      initAutomationPage();
      break;
    case 'about':
      initAboutPage();
      break;
    case 'contact':
      initContactPage();
      break;
    case 'quote':
      initQuotePage();
      break;
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  console.log('🚀 Segan Industry Website Initialized');
  console.log(`   Page: ${page}`);
  console.log('   Website API: legacy API retired — site runs on static fallbacks; live chat uses the production backend.');
});

// Export for global access
window.SeganIndustry = {
  api,
  showToast,
  formatCurrency,
  formatNumber,
  CONFIG
};