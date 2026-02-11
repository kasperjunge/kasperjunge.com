/**
 * kasperjunge.com — Contact Form & Analytics
 */

document.addEventListener('DOMContentLoaded', () => {
    initContactForm();
    initAnalytics();
});

function getOrCreateSessionId(storageKey = 'kj_session_id') {
    let sessionId = localStorage.getItem(storageKey);
    if (sessionId) return sessionId;

    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
        sessionId = window.crypto.randomUUID();
    } else {
        sessionId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    localStorage.setItem(storageKey, sessionId);
    return sessionId;
}

function resolveApiUrl(path) {
    if (!path) return null;
    if (/^https?:\/\//i.test(path)) return path;

    const runtimeConfig = window.__APP_CONFIG__ || {};
    const configuredApiBaseUrl = `${runtimeConfig.API_BASE_URL || ""}`.trim();
    const dataAttributeApiBaseUrl = `${document.body.dataset.apiBaseUrl || ''}`.trim();
    const apiBaseUrl = configuredApiBaseUrl || dataAttributeApiBaseUrl;
    if (!apiBaseUrl) return path;

    const normalizedBase = apiBaseUrl.replace(/\/+$/, '');
    const normalizedPath = path.replace(/^\/+/, '');
    return `${normalizedBase}/${normalizedPath}`;
}

/**
 * Contact form submission to backend API
 */
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    const statusEl = document.getElementById('contactFormStatus');
    const apiUrl = resolveApiUrl(form.dataset.apiUrl);

    if (!apiUrl) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const btn = form.querySelector('button[type="submit"]');
        if (!btn) return;

        const originalText = btn.textContent;
        btn.textContent = 'Sending...';
        btn.disabled = true;
        btn.style.opacity = '0.7';

        if (statusEl) {
            statusEl.textContent = '';
            statusEl.classList.remove('is-success', 'is-error');
        }

        const formData = new FormData(form);
        const payload = {
            name: `${formData.get('name') || ''}`.trim(),
            email: `${formData.get('email') || ''}`.trim(),
            message: `${formData.get('message') || ''}`.trim(),
            website: `${formData.get('website') || ''}`.trim(),
        };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error('Request failed');
            }

            if (statusEl) {
                statusEl.textContent = 'Thanks for your message. I\'ll get back to you within 24 hours.';
                statusEl.classList.add('is-success');
            }
            form.reset();
            btn.textContent = 'Sent!';
        } catch (_error) {
            if (statusEl) {
                statusEl.textContent = 'Something went wrong. Please try again in a moment.';
                statusEl.classList.add('is-error');
            }
            btn.textContent = originalText;
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    });
}

/**
 * Anonymous pageview tracking
 */
function initAnalytics() {
    const endpoint = resolveApiUrl(document.body.dataset.analyticsUrl);
    if (!endpoint) return;

    const payload = {
        path: window.location.pathname + window.location.search,
        referrer: document.referrer || null,
        title: document.title,
        session_id: getOrCreateSessionId(),
    };

    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true,
    }).catch(() => {});
}
