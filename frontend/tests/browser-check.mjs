import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const base = process.env.BASE_URL || 'http://127.0.0.1:5173';
const out = '../.impeccable/review';
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const errors = [];
const desktop = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
  reducedMotion: 'reduce'
});
const page = await desktop.newPage();
page.on('pageerror', (e) => errors.push(e.message));
async function shot(p, name) {
  await p.evaluate(() => document.fonts.ready);
  if (!process.env.NO_SCREENSHOTS)
    await p.screenshot({ path: `${out}/${name}.png`, fullPage: true });
  assert(
    await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    `${name}: horizontal overflow`
  );
}
await page.goto(base);
await page.getByRole('heading', { name: 'Le squadre', exact: true }).waitFor();
assert.equal(await page.title(), 'Nome in codice');
assert.equal(
  await page.getByRole('link', { name: 'NOME IN CODICE' }).count(),
  1
);
await shot(page, 'desktop');
const mobileContext = await browser.newContext({
  viewport: { width: 390, height: 844 },
  reducedMotion: 'reduce',
  isMobile: true,
  hasTouch: true
});
const mobile = await mobileContext.newPage();
await mobile.goto(base);
await mobile
  .getByRole('heading', { name: 'Le squadre', exact: true })
  .waitFor();
await shot(mobile, 'mobile');
for (let i = 0; i < 3; i++)
  await page.getByRole('button', { name: 'Aggiungi una squadra' }).click();
await page.getByRole('button', { name: '5 × 6' }).click();
await page.getByLabel('Civili', { exact: true }).fill('0');
await page.getByLabel('Civili', { exact: true }).blur();
await page
  .getByLabel('Codice Spymaster facoltativo, almeno 8 caratteri')
  .fill('missione-test');
const createdPromise = page.waitForResponse(
  (r) => r.url().endsWith('/api/games') && r.request().method() === 'POST'
);
await page.getByRole('button', { name: 'Avvia la missione' }).click();
const created = await (await createdPromise).json();
assert(created.game, JSON.stringify(created));
const id = created.game.id;
await page.locator('.word-card').first().waitFor();
assert.equal(await page.locator('.word-card').count(), 30);
await page.getByLabel('Indizio', { exact: true }).waitFor();
await shot(page, 'board-desktop');
const spectator = await browser.newPage({
  viewport: { width: 1440, height: 1000 }
});
await spectator.goto(`${base}/g/${id}`);
await spectator.locator('.word-card').first().waitFor();
assert.equal(await spectator.locator('.clue-form').count(), 0);
const publicData = await (
  await page.request.get(`${base}/api/games/${id}`)
).json();
assert(publicData.cards.every((c) => !('owner' in c)));
await mobile.goto(`${base}/g/${id}/spy`);
await mobile.getByLabel('Codice Spymaster', { exact: true }).fill('wrong-code');
await mobile.getByRole('button', { name: 'Apri la mappa segreta' }).click();
await mobile.getByRole('alert').waitFor();
await mobile
  .getByLabel('Codice Spymaster', { exact: true })
  .fill('missione-test');
await mobile.getByRole('button', { name: 'Apri la mappa segreta' }).click();
await mobile.locator('.word-card').first().waitFor();
await shot(mobile, 'spy-mobile');
await mobile.setViewportSize({ width: 1440, height: 1000 });
await shot(mobile, 'spy-desktop');
await mobile.setViewportSize({ width: 390, height: 844 });
await page.getByLabel('Indizio', { exact: true }).fill('Segnalazione');
await page.getByLabel('Numero', { exact: true }).fill('1');
await page.getByRole('button', { name: 'Conferma indizio' }).click();
await page.locator('.clue-display strong').waitFor();
const aiCalls = [];
await page.route('https://classifier.dev/v1/classify', async (route) => {
  if (route.request().method() === 'OPTIONS') {
    await route.fulfill({
      status: 204,
      headers: {
        'access-control-allow-origin': '*',
        'access-control-allow-methods': 'POST, OPTIONS',
        'access-control-allow-headers': 'content-type'
      }
    });
    return;
  }
  const body = JSON.parse(route.request().postData());
  aiCalls.push(body);
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    headers: { 'access-control-allow-origin': '*' },
    body: JSON.stringify({
      results: body.inputs.map((_, i) => ({
        label: body.labels[i < 2 ? 0 : 1],
        scores: {
          [body.labels[0]]: i < 2 ? 0.9 : 0.1,
          [body.labels[1]]: i < 2 ? 0.1 : 0.9
        }
      }))
    })
  });
});
await page.getByRole('button', { name: 'Chiedi all’AI' }).click();
await page.locator('.word-card.ai-suggested').first().waitFor();
assert.equal(aiCalls[0].inputs.length, 30);
assert.equal(await page.locator('.word-card.ai-suggested').count(), 2);
assert.equal(await page.locator('.ai-words').count(), 0);
await page.getByRole('button', { name: 'Nascondi suggerimenti' }).click();
assert.equal(await page.locator('.word-card.ai-suggested').count(), 0);
await page.getByRole('button', { name: 'Mostra suggerimenti' }).click();
assert.equal(await page.locator('.word-card.ai-suggested').count(), 2);
assert.equal(aiCalls.length, 1);
const secret = await (
  await page.request.get(`${base}/api/games/${id}/spy`, {
    headers: { 'X-Spy-Code': 'missione-test' }
  })
).json();
const own = secret.cards.findIndex((c) => c.owner === secret.active);
await page.locator('.word-card').nth(own).click();
await page.getByRole('button', { name: 'Ripensaci' }).click();
assert.equal(await page.locator('.word-card.revealed').count(), 0);
await page.locator('.word-card').nth(own).click();
await page
  .getByRole('button', { name: 'Rivela la carta', exact: true })
  .click();
await page.locator('.word-card.revealed').waitFor();
await page.locator('.word-card.ai-suggested').first().waitFor({ state: 'hidden' });
await page.getByRole('button', { name: 'Chiedi all’AI' }).click();
await page.locator('.word-card.ai-suggested').first().waitFor();
assert.equal(aiCalls[1].inputs.length, 29);
assert.equal(await page.locator('.word-card.ai-suggested').count(), 2);
assert(!aiCalls[1].inputs.includes(secret.cards[own].word));
await spectator.locator('.word-card.revealed').waitFor({ timeout: 10000 });
await mobile.locator('.word-card.revealed').waitFor({ timeout: 10000 });
await page.reload();
await page
  .getByRole('button', { name: 'Passa il turno', exact: false })
  .waitFor();
assert.equal(await page.locator('.word-card.revealed').count(), 1);
await page
  .getByRole('button', { name: 'Passa il turno', exact: false })
  .click();
await page
  .getByRole('dialog')
  .getByRole('button', { name: 'Passa il turno', exact: true })
  .click();
await page.locator('.clue-form').waitFor();
await mobile.goto(`${base}/g/${id}`);
await mobile.locator('.word-card').first().waitFor();
await shot(mobile, 'board-mobile');
await mobile.goto(`${base}/g/AAAAAA`);
await mobile.getByRole('heading', { name: 'Missione non trovata.' }).waitFor();
const openSetup = await browser.newPage();
await openSetup.goto(base);
await openSetup.getByRole('button', { name: 'Avvia la missione' }).click();
await openSetup.locator('.word-card').first().waitFor();
const openId = new URL(openSetup.url()).pathname.split('/').pop();
await mobile.goto(`${base}/g/${openId}/spy`);
await mobile.locator('.word-card').first().waitFor();
assert.equal(await mobile.locator('.spy-login').count(), 0);
const openSpy = await (
  await page.request.get(`${base}/api/games/${openId}/spy`)
).json();
assert(openSpy.cards.every((card) => 'owner' in card));
await shot(mobile, 'spy-open-mobile');
await openSetup.getByLabel('Indizio', { exact: true }).fill('Segnalazione');
await openSetup.getByRole('button', { name: 'Conferma indizio' }).click();
await openSetup.locator('.clue-display strong').waitFor();
await openSetup.locator('.word-card').first().click();
const otherHostKey = await openSetup.evaluate((gameId) => localStorage.getItem(`host:${gameId}`), openId);
const latestState = await (await page.request.get(`${base}/api/games/${openId}`)).json();
const passFromAnotherDevice = await page.request.post(`${base}/api/games/${openId}/actions`, {
  headers: { 'X-Host-Key': otherHostKey },
  data: { kind: 'pass', revision: latestState.revision }
});
assert.equal(passFromAnotherDevice.status(), 200);
await openSetup.getByRole('dialog').waitFor({ state: 'hidden', timeout: 10000 });
assert.equal(await openSetup.locator('.word-card.revealed').count(), 0);
assert.deepEqual(errors, []);
console.log(
  JSON.stringify({
    ok: true,
    id,
    checks: [
      '5 teams / 30 cards / zero civilians',
      'public identity redaction',
      'wrong spy password',
      'two-device synchronization',
      'confirmation cancellation',
      'reveal persistence',
      'host recovery on reload',
      'AI highlights suggested cards, toggles without a new request, and resets after a reveal',
      'turn passing',
      'unknown game',
      'open Spymaster without a code',
      'stale reveal confirmation closes after another device acts',
      'desktop/mobile overflow'
    ],
    screenshots: process.env.NO_SCREENSHOTS ? 0 : 7
  })
);
await browser.close();
