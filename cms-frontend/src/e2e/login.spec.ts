import puppeteer, { Browser, Page } from 'puppeteer';
import 'dotenv/config';

jest.setTimeout(60000);

describe('CMS Frontend E2E', () => {
  let browser!: Browser;
  let page!: Page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: true,
      slowMo: 100,
      args: ['--window-size=1280,800']
    });
    page = await browser.newPage();
  });

  afterAll(async () => {
    if (browser) await browser.close();
  });

  it('should load the login page', async () => {
    const baseUrl = process.env['STAGING_URL'] || '';
    await page.goto('http://localhost:4200/login', { waitUntil: 'networkidle0' });
    const title = await page.title();
    expect(title).toContain('CmsFrontend');
  });
});