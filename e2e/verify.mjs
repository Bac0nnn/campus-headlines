import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE = 'http://127.0.0.1:5173';
const OUT = path.resolve(__dirname, '../docs/screenshots');
const FIXTURES = path.resolve(__dirname, 'fixtures');
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(FIXTURES, { recursive: true });

const results = [];
const problems = [];
let currentStep = 'init';
const step = (name) => { currentStep = name; console.log('\n== ' + name + ' =='); };

async function checkPage(label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (overflow > 2) problems.push(label + ': 横向溢出 ' + overflow + 'px');
  const broken = await page.evaluate(() => Array.from(document.images)
    .filter((img) => img.complete && img.naturalWidth === 0).map((img) => img.getAttribute('src')));
  if (broken.length) problems.push(label + ': 图片加载失败 ' + broken.join(', '));
}

async function shot(name, fullPage = true) {
  await page.waitForTimeout(450);
  if (fullPage) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(350);
  }
  await checkPage(name);
  const file = path.join(OUT, name + '.png');
  await page.screenshot({ path: file, fullPage });
  results.push({ name, size: fs.statSync(file).size, step: currentStep });
  console.log('  截图 -> ' + name + '.png');
}

const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'msedge' });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const page = await context.newPage();

page.on('console', (msg) => { if (msg.type() === 'error') problems.push(currentStep + ': console ' + msg.text().slice(0, 300)); });
page.on('pageerror', (err) => problems.push(currentStep + ': pageerror ' + err.message.slice(0, 300)));
page.on('response', (res) => {
  if (res.status() >= 400 && res.url().startsWith('http://127.0.0.1:5173')) problems.push(currentStep + ': HTTP ' + res.status() + ' ' + res.url());
});

try {
  const fp = await context.newPage();
  await fp.setViewportSize({ width: 800, height: 450 });
  await fp.setContent('<body style="margin:0"><div style="width:800px;height:450px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0ea5e9,#22c55e);color:#fff;font:700 46px Microsoft YaHei,sans-serif;">校园秋景 · 数据库封面</div></body>');
  await fp.screenshot({ path: path.join(FIXTURES, 'upload.png') });
  await fp.setViewportSize({ width: 400, height: 400 });
  await fp.setContent('<body style="margin:0"><div style="width:400px;height:400px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2f6bff,#7c3aed);color:#fff;font:700 180px Microsoft YaHei,sans-serif;">林</div></body>');
  await fp.screenshot({ path: path.join(FIXTURES, 'avatar.png') });
  await fp.close();

  step('01 作者/审核员登录页');
  await page.goto(BASE + '/media/login', { waitUntil: 'networkidle' });
  await page.waitForSelector('text=作者 / 审核员登录');
  await shot('01-media-login');

  step('02 三端注册页');
  await page.goto(BASE + '/register', { waitUntil: 'networkidle' });
  await page.locator('.role-card').filter({ hasText: '作者用户' }).click();
  await page.getByPlaceholder('手机号').fill('13900003333');
  await page.getByPlaceholder('昵称（2-20 个字符）').fill('校园摄影师');
  await page.getByPlaceholder('密码（6-20 位）').fill('abc123');
  await page.getByPlaceholder('再次输入密码').fill('abc123');
  await page.locator('.el-checkbox').click();
  await page.waitForTimeout(300);
  await shot('02-register-role');

  step('03 注册作者并进入创作中心');
  await page.getByRole('button', { name: '注册并登录' }).click();
  await page.waitForURL('**/media/publish', { timeout: 15000 });
  await page.goto(BASE + '/media/material', { waitUntil: 'networkidle' });
  await page.waitForSelector('.upload-tile');
  await shot('03-author-material');

  step('04 上传封面图片（入库）');
  const before = await page.locator('.material-item').count();
  await page.locator('input[type=file]').first().setInputFiles(path.join(FIXTURES, 'upload.png'));
  await page.waitForFunction((n) => document.querySelectorAll('.material-item').length > n, before, { timeout: 20000 });
  await page.waitForTimeout(700);
  await shot('04-author-uploaded');

  step('05 发布文章（封面来自数据库）');
  await page.goto(BASE + '/media/publish', { waitUntil: 'networkidle' });
  await page.locator('.title-input').fill('校园秋日摄影展开幕（数据库封面）');
  const editor = page.locator('.w-e-text-container [contenteditable="true"]').first();
  await editor.click();
  await page.keyboard.type('本次摄影展的封面图片直接从数据库读取，重新登录后依然可以查看。');
  await page.locator('.side-card .el-select').click();
  await page.locator('.el-select-dropdown__item').filter({ hasText: '校园' }).first().click();
  await page.locator('.label-input input').fill('摄影');
  await page.keyboard.press('Enter');
  await page.locator('.cover-type').filter({ hasText: '单图' }).click();
  await page.locator('.add-cover').click();
  await page.locator('.el-dialog').waitFor({ state: 'visible' });
  await page.locator('.picker-item').first().click();
  await page.locator('.el-dialog__footer button').filter({ hasText: '确定选择' }).click();
  await page.locator('.el-dialog').waitFor({ state: 'hidden' });
  await page.waitForTimeout(400);
  await shot('05-publish-db-cover');

  step('06 提交审核');
  await page.getByRole('button', { name: '提交审核' }).click();
  await page.waitForURL('**/media/content', { timeout: 15000 });
  await page.locator('.status-tab').filter({ hasText: '待审核' }).click();
  await page.waitForTimeout(700);
  await shot('06-content-pending');

  step('07 切换到审核员');
  await page.locator('.logout').click();
  await page.locator('.el-message-box').waitFor({ state: 'visible' });
  await page.locator('.el-message-box__btns button.el-button--primary').click();
  await page.waitForURL('**/media/login', { timeout: 15000 });
  await page.getByPlaceholder('请输入手机号或用户名').fill('13900000001');
  await page.getByPlaceholder('请输入密码').fill('123456');
  await page.getByRole('button', { name: '登录创作中心' }).click();
  await page.waitForURL('**/media/audit', { timeout: 15000 });
  await page.waitForSelector('.audit-row');
  await shot('07-audit-pending');

  step('08 审核员查看全文');
  await page.locator('.audit-row').first().getByRole('button', { name: '查看全文' }).click();
  await page.locator('.el-dialog').waitFor({ state: 'visible' });
  await page.waitForTimeout(400);
  await shot('08-audit-detail', false);

  step('09 审核通过');
  await page.locator('.el-dialog__footer button').filter({ hasText: '通过并发布' }).click();
  await page.locator('.el-message-box').waitFor({ state: 'visible' });
  await page.locator('.el-message-box__btns button.el-button--primary').click();
  await page.waitForSelector('.el-message--success');
  await page.locator('.el-dialog').waitFor({ state: 'hidden' });
  await page.locator('.tab').filter({ hasText: '已通过' }).click();
  await page.waitForTimeout(800);
  await shot('09-audit-passed');

  step('10 普通用户登录');
  await page.locator('.logout').click();
  await page.locator('.el-message-box').waitFor({ state: 'visible' });
  await page.locator('.el-message-box__btns button.el-button--primary').click();
  await page.waitForURL('**/media/login', { timeout: 15000 });
  await page.goto(BASE + '/login', { waitUntil: 'networkidle' });
  await page.locator('.mode-tabs button').filter({ hasText: '密码登录' }).click();
  await page.getByPlaceholder('请输入手机号').fill('13800138000');
  await page.getByPlaceholder('请输入密码').fill('123456');
  await shot('10-reader-login');
  await page.getByRole('button', { name: '开始使用' }).click();
  await page.waitForFunction(() => location.pathname === '/', { timeout: 15000 });
  await page.waitForSelector('.hero-card');
  await page.waitForTimeout(900);
  await shot('11-reader-home');

  step('11 查看数据库封面文章');
  await page.locator('.article-card').filter({ hasText: '数据库封面' }).first().click();
  await page.waitForSelector('.article-body');
  await page.waitForTimeout(700);
  await shot('12-reader-detail');

  step('12 普通用户上传头像');
  await page.goto(BASE + '/profile', { waitUntil: 'networkidle' });
  await page.waitForSelector('.form-card');
  await page.getByRole('button', { name: '更换头像' }).click();
  await page.locator('.el-dialog').waitFor({ state: 'visible' });
  await page.waitForTimeout(300);
  await shot('13-avatar-dialog', false);
  await page.locator('.el-dialog input[type=file]').setInputFiles(path.join(FIXTURES, 'avatar.png'));
  await page.waitForSelector('text=头像已上传并保存到数据库', { timeout: 15000 });
  await page.locator('.el-dialog__footer button').filter({ hasText: '确定' }).click();
  await page.waitForTimeout(800);
  await shot('14-profile-avatar');

  step('13 移动端');
  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const mobilePage = await mobile.newPage();
  mobilePage.on('pageerror', (err) => problems.push('mobile: pageerror ' + err.message));
  await mobilePage.goto(BASE + '/', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1200);
  await mobilePage.screenshot({ path: path.join(OUT, '15-mobile-home.png') });
  results.push({ name: '15-mobile-home', size: fs.statSync(path.join(OUT, '15-mobile-home.png')).size });
  await mobilePage.goto(BASE + '/article/25', { waitUntil: 'networkidle' }).catch(() => {});
  await mobilePage.waitForTimeout(1000);
  await mobilePage.screenshot({ path: path.join(OUT, '16-mobile-detail.png') });
  results.push({ name: '16-mobile-detail', size: fs.statSync(path.join(OUT, '16-mobile-detail.png')).size });
  await mobile.close();
} catch (error) {
  problems.push('FATAL @' + currentStep + ': ' + error.message);
  try { await page.screenshot({ path: path.join(OUT, 'error-state.png'), fullPage: true }); } catch (e) {}
  console.error('FAILED:', error);
} finally {
  fs.writeFileSync(path.resolve(__dirname, 'report.json'), JSON.stringify({ base: BASE, time: new Date().toISOString(), results, problems }, null, 2), 'utf8');
  await browser.close();
  console.log('\n=== 完成 ===');
  console.log('截图数量:', results.length);
  console.log('问题数量:', problems.length);
  problems.forEach((p) => console.log(' - ' + p));
}
