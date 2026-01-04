const fs = require('node:fs');
const path = require('node:path');
const { test, expect } = require('@playwright/test');

function nowRunId() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

async function capturePageBasics(page) {
  return page.evaluate(() => {
    const description =
      document.querySelector('meta[name="description"]')?.getAttribute('content') ?? null;

    const h1 = document.querySelector('h1')?.textContent?.trim() ?? null;
    const canonical =
      document.querySelector('link[rel="canonical"]')?.getAttribute('href') ?? null;

    return {
      title: document.title || null,
      description,
      canonical,
      h1,
      url: window.location.href,
    };
  });
}

async function captureNavigationTimings(page) {
  try {
    return await page.evaluate(() => {
      const entry = performance.getEntriesByType('navigation')[0];
      if (!entry) return null;
      return {
        type: entry.type,
        startTime: entry.startTime,
        duration: entry.duration,
        domContentLoaded: entry.domContentLoadedEventEnd,
        loadEventEnd: entry.loadEventEnd,
        transferSize: entry.transferSize,
        encodedBodySize: entry.encodedBodySize,
        decodedBodySize: entry.decodedBodySize,
      };
    });
  } catch {
    return null;
  }
}

async function captureLayoutSignals(page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const horizontalOverflow = doc.scrollWidth > doc.clientWidth + 1;
    return {
      viewport: { width: window.innerWidth, height: window.innerHeight },
      client: { width: doc.clientWidth, height: doc.clientHeight },
      devicePixelRatio: window.devicePixelRatio,
      horizontalOverflow,
      scrollHeight: doc.scrollHeight,
      scrollWidth: doc.scrollWidth,
    };
  });
}

async function captureOverflowOffenders(page, { limit = 25 } = {}) {
  return page.evaluate(({ limit }) => {
    const doc = document.documentElement;
    const clientWidth = doc.clientWidth;

    function isVisible(el) {
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    }

    function selectorHint(el) {
      if (el.id) return `#${el.id}`;
      const className = typeof el.className === 'string' ? el.className.trim() : '';
      if (className) return `.${className.split(/\s+/)[0]}`;
      return el.tagName.toLowerCase();
    }

    const offenders = [];
    const all = Array.from(document.body?.querySelectorAll('*') ?? []);
    for (const el of all) {
      if (!isVisible(el)) continue;
      const rect = el.getBoundingClientRect();
      const overflowRight = Math.max(0, rect.right - clientWidth);
      const overflowLeft = Math.max(0, -rect.left);
      const overflow = Math.max(overflowRight, overflowLeft);
      if (overflow <= 1) continue;

      offenders.push({
        hint: selectorHint(el),
        tag: el.tagName.toLowerCase(),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        left: Math.round(rect.left),
        right: Math.round(rect.right),
        overflow,
        overflowRight: Math.round(overflowRight),
        overflowLeft: Math.round(overflowLeft),
      });
    }

    offenders.sort((a, b) => b.overflow - a.overflow);
    return {
      clientWidth,
      offenderCount: offenders.length,
      offenders: offenders.slice(0, limit),
    };
  }, { limit });
}

async function captureInteractiveTargets(page) {
  return page.evaluate(() => {
    const candidates = Array.from(
      document.querySelectorAll(
        [
          'a[href]',
          'button',
          'input:not([type="hidden"])',
          'select',
          'textarea',
          '[role="button"]',
          '[role="link"]',
          '[onclick]',
        ].join(','),
      ),
    );

    function isVisible(el) {
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') return false;
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return false;
      if (rect.bottom < 0 || rect.right < 0) return false;
      if (rect.top > window.innerHeight || rect.left > window.innerWidth) return false;
      return true;
    }

    function labelFor(el) {
      const aria = el.getAttribute('aria-label')?.trim();
      if (aria) return aria;
      const title = el.getAttribute('title')?.trim();
      if (title) return title;
      const text = el.textContent?.replace(/\s+/g, ' ').trim();
      if (text) return text.slice(0, 120);
      if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
        const placeholder = el.placeholder?.trim();
        if (placeholder) return placeholder.slice(0, 120);
        const value = el.value?.trim();
        if (value) return value.slice(0, 120);
      }
      const href = el instanceof HTMLAnchorElement ? el.href : null;
      if (href) return href;
      if (el.id) return `#${el.id}`;
      const className = typeof el.className === 'string' ? el.className.trim() : '';
      if (className) return `.${className.split(/\s+/)[0]}`;
      return el.tagName.toLowerCase();
    }

    const targets = [];
    for (const element of candidates) {
      if (!isVisible(element)) continue;
      const rect = element.getBoundingClientRect();
      targets.push({
        tag: element.tagName.toLowerCase(),
        label: labelFor(element),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        top: Math.round(rect.top),
        left: Math.round(rect.left),
        href: element instanceof HTMLAnchorElement ? element.getAttribute('href') : null,
        id: element.id || null,
        className: typeof element.className === 'string' ? element.className : null,
      });
    }
    return targets;
  });
}

function summarizeTargetSizes(targets, { minSize }) {
  const tooSmall = targets
    .filter((t) => t.width < minSize || t.height < minSize)
    .map((t) => ({
      ...t,
      minDimension: Math.min(t.width, t.height),
      area: t.width * t.height,
    }))
    .sort((a, b) => a.minDimension - b.minDimension || a.area - b.area);

  return {
    minSize,
    totalTargets: targets.length,
    tooSmallCount: tooSmall.length,
    worstOffenders: tooSmall.slice(0, 25),
  };
}

test('Quoted UX excellence capture (Playwright)', async ({ browser }) => {
  test.setTimeout(20 * 60 * 1000);

  const baseUrl = process.env.UX_AUDIT_BASE_URL || 'https://quoted.it.com';
  const runId = process.env.UX_AUDIT_RUN_ID || nowRunId();
  const outputRoot =
    process.env.UX_AUDIT_OUTPUT_DIR || path.join('reports', 'ux-excellence-playwright', runId);

  ensureDir(outputRoot);

  const runMeta = {
    runId,
    baseUrl,
    startedAt: new Date().toISOString(),
    env: {
      headless: process.env.PW_HEADLESS ?? 'default',
      ci: process.env.CI ?? 'false',
    },
  };
  writeJson(path.join(outputRoot, 'run-meta.json'), runMeta);

  const sessions = [];

  async function runSession(session) {
    const sessionDir = path.join(outputRoot, session.name);
    ensureDir(sessionDir);

    const context = await browser.newContext({
      viewport: session.viewport,
      deviceScaleFactor: session.deviceScaleFactor,
      isMobile: session.isMobile,
      hasTouch: session.hasTouch,
      acceptDownloads: true,
      locale: 'en-US',
    });
    const page = await context.newPage();
    page.setDefaultTimeout(60_000);
    page.setDefaultNavigationTimeout(60_000);

    const consoleMessages = [];
    const pageErrors = [];
    const requestFailures = [];

    page.on('console', (msg) => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location(),
      });
    });
    page.on('pageerror', (error) => {
      pageErrors.push({ message: String(error?.message ?? error), name: error?.name });
    });
    page.on('requestfailed', (request) => {
      requestFailures.push({
        url: request.url(),
        method: request.method(),
        failure: request.failure()?.errorText ?? 'unknown',
      });
    });

    async function gotoAndCapture(relativePath, label, { fullPage = true } = {}) {
      const url = new URL(relativePath, baseUrl).toString();
      const startedAt = Date.now();
      let response = null;
      let domContentLoadedMs = null;
      let navigationError = null;
      try {
        response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60_000 });
        domContentLoadedMs = Date.now() - startedAt;
      } catch (error) {
        navigationError = String(error?.message ?? error);
      }

      if (!navigationError) {
        await page.waitForLoadState('load', { timeout: 45_000 }).catch(() => {});
        await page.waitForTimeout(1000);
      }

      const basics = navigationError ? null : await capturePageBasics(page);
      const timings = navigationError ? null : await captureNavigationTimings(page);
      const layout = navigationError ? null : await captureLayoutSignals(page);

      const screenshotPath = path.join(sessionDir, `${label}.png`);
      if (!navigationError) {
        await page.screenshot({ path: screenshotPath, fullPage });
      }

      return {
        label,
        url,
        status: response?.status() ?? null,
        navigationError,
        domContentLoadedMs,
        basics,
        timings,
        layout,
        screenshotPath,
      };
    }

    const captures = [];

    captures.push(await gotoAndCapture('/', 'landing', { fullPage: true }));

    if (session.isMobile) {
      const targets = await captureInteractiveTargets(page);
      writeJson(path.join(sessionDir, 'landing-targets.json'), targets);
      writeJson(
        path.join(sessionDir, 'landing-target-size-summary.json'),
        summarizeTargetSizes(targets, { minSize: 44 }),
      );

      const overflow = await captureOverflowOffenders(page);
      writeJson(path.join(sessionDir, 'landing-overflow.json'), overflow);
    }

    captures.push(await gotoAndCapture('/try', 'try-initial', { fullPage: true }));

    const tourWelcome = page.locator('#tourWelcome');
    if (await tourWelcome.isVisible().catch(() => false)) {
      await page.screenshot({ path: path.join(sessionDir, 'try-tour-welcome.png'), fullPage: true });
    }

    const textTab = page.locator('#textTab');
    if (await textTab.count()) {
      await textTab.click();
    }

    const description = page.locator('#descriptionInput');
    await expect(description).toBeVisible({ timeout: 30_000 });
    await description.fill(
      'Kitchen remodel for the Johnson family. New cabinets + quartz countertops + backsplash tile. Roughly 35 linear feet of base/upper cabinets. Include demo and haul-away. Target completion in 2 weeks.',
    );
    await page.screenshot({ path: path.join(sessionDir, 'try-text-filled.png'), fullPage: true });

    const generateBtn = page.locator('#generateBtn');
    const generationStart = Date.now();
    await generateBtn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(sessionDir, 'try-generating-0.5s.png'), fullPage: true });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: path.join(sessionDir, 'try-generating-3s.png'), fullPage: true });

    await page
      .waitForFunction(() => document.getElementById('resultsSection')?.classList.contains('visible'), null, {
        timeout: 90_000,
      })
      .catch(() => {});
    const generationMs = Date.now() - generationStart;

    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(sessionDir, 'try-results.png'), fullPage: true });

    const shareBtn = page.locator('#shareQuoteBtn');
    if (await shareBtn.isVisible().catch(() => false)) {
      await shareBtn.click().catch(() => {});
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(sessionDir, 'try-after-share-click.png'), fullPage: true });
    }

    const downloadPdfBtn = page.locator('#downloadPdfBtn');
    if (await downloadPdfBtn.isVisible().catch(() => false)) {
      const downloadPromise = page.waitForEvent('download', { timeout: 15_000 }).catch(() => null);
      await downloadPdfBtn.click().catch(() => {});
      const download = await downloadPromise;
      if (download) {
        const downloadPath = path.join(sessionDir, await download.suggestedFilename());
        await download.saveAs(downloadPath);
      }
    }

    const authCapture = await gotoAndCapture('/app', 'app-entry', { fullPage: true });
    captures.push(authCapture);

    const emailInput = page.locator('input[type="email"]');
    if (!authCapture.navigationError && (await emailInput.isVisible().catch(() => false))) {
      await emailInput.fill('not-an-email');
      await page.screenshot({ path: path.join(sessionDir, 'app-invalid-email.png'), fullPage: true });
    }

    const blogCapture = await gotoAndCapture('/blog', 'blog-index', { fullPage: true });
    captures.push(blogCapture);

    const useCasesCapture = await gotoAndCapture('/use-cases', 'use-cases', { fullPage: true });
    captures.push(useCasesCapture);
    if (session.isMobile && !useCasesCapture.navigationError) {
      const overflow = await captureOverflowOffenders(page);
      writeJson(path.join(sessionDir, 'use-cases-overflow.json'), overflow);
    }

    const helpCapture = await gotoAndCapture('/help', 'help', { fullPage: true });
    captures.push(helpCapture);

    const customerLandingCapture = await gotoAndCapture('/for-customers', 'for-customers', { fullPage: true });
    captures.push(customerLandingCapture);

    const termsCapture = await gotoAndCapture('/terms', 'terms', { fullPage: true });
    captures.push(termsCapture);

    const privacyCapture = await gotoAndCapture('/privacy', 'privacy', { fullPage: true });
    captures.push(privacyCapture);

    const sessionSummary = {
      ...session,
      generationMs,
      captures,
      consoleSummary: {
        total: consoleMessages.length,
        errors: consoleMessages.filter((m) => m.type === 'error').slice(0, 50),
        warnings: consoleMessages.filter((m) => m.type === 'warning').slice(0, 50),
      },
      pageErrors: pageErrors.slice(0, 50),
      requestFailures: requestFailures.slice(0, 50),
    };

    writeJson(path.join(sessionDir, 'session-summary.json'), sessionSummary);
    writeJson(path.join(sessionDir, 'console.json'), consoleMessages);
    writeJson(path.join(sessionDir, 'page-errors.json'), pageErrors);
    writeJson(path.join(sessionDir, 'request-failures.json'), requestFailures);

    await context.close();
    return sessionSummary;
  }

  sessions.push(
    await runSession({
      name: 'desktop-1440',
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 1,
      isMobile: false,
      hasTouch: false,
    }),
  );

  sessions.push(
    await runSession({
      name: 'mobile-375',
      viewport: { width: 375, height: 667 },
      deviceScaleFactor: 2,
      isMobile: true,
      hasTouch: true,
    }),
  );

  writeJson(path.join(outputRoot, 'sessions.json'), sessions);
});
