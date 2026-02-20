const { chromium } = require('playwright');
const path = require('path');

const IMAGES_DIR = path.join(__dirname, 'src/main/asciidoc/images');
const BASE_URL = 'http://localhost:2480';
const USERNAME = 'root';
const PASSWORD = 'playwithdata';
const DATABASE = 'org-legaladvicenow';

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function screenshot(page, name, options = {}) {
  const filePath = path.join(IMAGES_DIR, name);
  await page.screenshot({ path: filePath, fullPage: false, ...options });
  console.log(`  ✓ ${name}`);
}

async function dismissToasts(page) {
  await page.evaluate(() => {
    document.querySelectorAll('.toast').forEach(t => t.remove());
    const container = document.getElementById('toastContainer');
    if (container) container.innerHTML = '';
  });
  await delay(100);
}

async function clickTab(page, selector) {
  await dismissToasts(page);
  await page.click(selector, { force: true });
  await delay(1000);
}

async function clickSubTab(page, selector) {
  await dismissToasts(page);
  await page.click(selector, { force: true });
  await delay(800);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  console.log('Navigating to Studio...');
  // Clear storage before navigating to force login
  await page.addInitScript(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await delay(3000);

  // === LOGIN ===
  console.log('\n📸 Login');
  // Check if login popup is already visible, if not trigger it
  const loginVisible = await page.evaluate(() => {
    const popup = document.getElementById('loginPopup');
    return popup && popup.classList.contains('show');
  });
  if (!loginVisible) {
    await page.evaluate(() => { if (typeof showLoginPopup === 'function') showLoginPopup(); });
    await delay(1000);
  }
  await page.waitForSelector('#inputUserName', { state: 'visible', timeout: 10000 });
  await delay(500);
  await screenshot(page, 'studio-login.png');

  // Log in
  await page.fill('#inputUserName', USERNAME);
  await page.fill('#inputUserPassword', PASSWORD);
  await page.click('#loginForm button[type="submit"]');
  await delay(3000);

  // Select database
  await page.selectOption('#queryInputDatabase', DATABASE);
  await delay(2000);

  // === QUERY TAB ===
  console.log('\n📸 Query Tab');
  await clickTab(page, '#tab-query-sel');
  await delay(500);

  // Command panel (full query tab)
  await screenshot(page, 'studio-command-panel.png');

  // Language dropdown
  await page.click('#inputLanguage');
  await delay(300);
  // On some browsers, select dropdowns can't be screenshotted open.
  // Take screenshot with the select focused
  await screenshot(page, 'studio-command-select-language.png');
  await page.keyboard.press('Escape');
  await delay(200);

  // Sidebar panels
  // Overview is already active
  await screenshot(page, 'studio-query-overview.png');

  await page.click('button[data-panel="history"]');
  await delay(500);
  await screenshot(page, 'studio-query-history.png');

  await page.click('button[data-panel="saved"]');
  await delay(500);
  await screenshot(page, 'studio-query-saved.png');

  await page.click('button[data-panel="reference"]');
  await delay(500);
  await screenshot(page, 'studio-query-reference.png');

  // Switch back to overview
  await page.click('button[data-panel="overview"]');
  await delay(300);

  // Execute a query to get results - first a SELECT for table/json
  console.log('\n📸 Query Results');
  await page.evaluate(() => {
    const cm = document.querySelector('.CodeMirror').CodeMirror;
    cm.setValue('SELECT FROM V LIMIT 20');
  });
  await delay(300);
  await page.click('[data-testid="execute-query-button"]');
  await delay(3000);

  // Table result
  await clickSubTab(page, '#tab-table-sel');
  await delay(500);
  await screenshot(page, 'studio-table.png');

  // For graph: run a query that produces connected vertices
  await page.evaluate(() => {
    const cm = document.querySelector('.CodeMirror').CodeMirror;
    cm.setValue('SELECT FROM V LIMIT 20');
  });
  // Switch to graph tab first so graph renders
  await clickSubTab(page, '#tab-graph-sel');
  await delay(500);
  await page.click('[data-testid="execute-query-button"]');
  await delay(3000);
  await screenshot(page, 'studio-graph-default.png');

  // Click on a node using Cytoscape API - try all possible global variable names
  const nodeClicked = await page.evaluate(() => {
    // Search all window properties for a Cytoscape instance
    for (const key of Object.keys(window)) {
      const obj = window[key];
      if (obj && typeof obj === 'object' && typeof obj.nodes === 'function') {
        try {
          const nodes = obj.nodes();
          if (nodes.length > 0) {
            nodes[0].emit('tap');
            return key;
          }
        } catch(e) {}
      }
    }
    // Also check if there's a cytoscape container with a reference
    const cyDiv = document.getElementById('cy');
    if (cyDiv && cyDiv._cyreg && cyDiv._cyreg.cy) {
      const nodes = cyDiv._cyreg.cy.nodes();
      if (nodes.length > 0) {
        nodes[0].emit('tap');
        return 'cy-div';
      }
    }
    return null;
  });
  if (nodeClicked) {
    console.log(`  Found cy instance as: ${nodeClicked}`);
    await delay(1000);
    await screenshot(page, 'studio-graph-node-panel.png');
  } else {
    // Fallback: click in the center of the graph area
    const cyEl = await page.$('#cy');
    if (cyEl) {
      const box = await cyEl.boundingBox();
      if (box) {
        // Try multiple click positions to hit a node
        const positions = [
          [box.x + box.width * 0.5, box.y + box.height * 0.5],
          [box.x + box.width * 0.3, box.y + box.height * 0.3],
          [box.x + box.width * 0.6, box.y + box.height * 0.4],
          [box.x + box.width * 0.4, box.y + box.height * 0.6],
        ];
        for (const [x, y] of positions) {
          await page.mouse.click(x, y);
          await delay(500);
          // Check if properties panel appeared
          const panelVisible = await page.evaluate(() => {
            const panel = document.getElementById('graphPropertiesPanel') ||
                          document.querySelector('.node-properties, .properties-panel, [id*="properties"]');
            return panel && panel.offsetHeight > 0;
          });
          if (panelVisible) {
            await screenshot(page, 'studio-graph-node-panel.png');
            break;
          }
        }
      }
    }
    console.log('  ⚠ Graph node panel - used fallback click approach');
  }

  // JSON result
  await clickSubTab(page, '#tab-json-sel');
  await delay(500);
  await screenshot(page, 'studio-json.png');

  // === DATABASE TAB ===
  console.log('\n📸 Database Tab');
  await clickTab(page, '#tab-database-sel');
  await delay(1500);
  await screenshot(page, 'studio-database.png');

  // Click on a type to show schema detail
  const typeItem = await page.$('.type-item, .schema-type, [onclick*="displaySchema"]');
  if (typeItem) {
    await typeItem.click();
    await delay(800);
  }
  await screenshot(page, 'studio-database-schema.png');

  // Database Settings sub-tab
  await clickSubTab(page, '#tab-db-settings-sel');
  await delay(800);
  await screenshot(page, 'studio-database-settings.png');

  // Database Backup sub-tab
  await clickSubTab(page, '#tab-db-backup-sel');
  await delay(800);
  await screenshot(page, 'studio-database-backup.png');

  // === SERVER TAB ===
  console.log('\n📸 Server Tab');
  await clickTab(page, '#tab-server-sel');
  await delay(1500);
  await screenshot(page, 'studio-server.png');

  // Sessions
  await clickSubTab(page, '#tab-server-sessions-sel');
  await delay(800);
  await screenshot(page, 'studio-server-sessions.png');

  // Events
  await clickSubTab(page, '#tab-server-events-sel');
  await delay(800);
  await screenshot(page, 'studio-server-events.png');

  // Metrics
  await clickSubTab(page, '#tab-metrics-sel');
  await delay(800);
  await screenshot(page, 'studio-server-metrics.png');

  // Backup
  await clickSubTab(page, '#tab-server-backup-sel');
  await delay(800);
  await screenshot(page, 'studio-server-backup.png');

  // MCP
  await clickSubTab(page, '#tab-server-mcp-sel');
  await delay(800);
  await screenshot(page, 'studio-server-mcp.png');

  // === SECURITY TAB ===
  console.log('\n📸 Security Tab');
  await clickTab(page, '#tab-security-sel');
  await delay(1500);
  await screenshot(page, 'studio-security.png');

  // Groups
  await clickSubTab(page, '#tab-security-groups-sel');
  await delay(800);
  await screenshot(page, 'studio-security-groups.png');

  // Tokens
  await clickSubTab(page, '#tab-security-tokens-sel');
  await delay(800);
  await screenshot(page, 'studio-security-tokens.png');

  // === API TAB ===
  console.log('\n📸 API Tab');
  await clickTab(page, '#tab-api-sel');
  await delay(1500);
  await screenshot(page, 'studio-api.png');

  // Try to expand an endpoint for playground view
  const endpoint = await page.$('.api-endpoint');
  if (endpoint) {
    await endpoint.click();
    await delay(800);
    await screenshot(page, 'studio-api-playground.png');
  }

  // === INFO TAB ===
  console.log('\n📸 Info Tab');
  await clickTab(page, '#tab-resources-sel');
  await delay(1500);
  await screenshot(page, 'studio-info.png');

  // === SETTINGS TAB ===
  console.log('\n📸 Settings Tab');
  await clickTab(page, '#tab-settings-sel');
  await delay(1000);
  await screenshot(page, 'studio-settings.png');

  console.log('\n✅ All screenshots captured!');
  await browser.close();
})();
