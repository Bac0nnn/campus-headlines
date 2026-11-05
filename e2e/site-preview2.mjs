import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true, channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });
const errors = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
await page.goto('http://127.0.0.1:8099/', { waitUntil: 'networkidle' });
await page.evaluate(() => document.querySelectorAll('img').forEach(i => i.loading = 'eager'));
await page.waitForTimeout(2200);
const broken = await page.$$eval('img', imgs => imgs.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src')));
console.log(JSON.stringify({ height: await page.evaluate(() => document.body.scrollHeight), broken, errors }));
for (const [name, y] of [['features', 900], ['flow', 1900], ['gallery', 2900], ['tech', 4300], ['docs', 5600]]) {
  await page.evaluate(v => window.scrollTo(0, v), y);
  await page.waitForTimeout(700);
  await page.screenshot({ path: 'F:/IDEA/YXP-QM/campus-headlines/docs/site-' + name + '.png' });
}
await browser.close();
const mobile = await chromium.launch({ headless: true, channel: 'msedge' });
const m = await mobile.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
await m.goto('http://127.0.0.1:8099/', { waitUntil: 'networkidle' });
await m.waitForTimeout(1500);
await m.screenshot({ path: 'F:/IDEA/YXP-QM/campus-headlines/docs/site-mobile.png', fullPage: false });
await mobile.close();
