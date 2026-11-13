// tools/lib/browser.mjs — one place that finds and launches the browser for every studio tool.
//
// Why: the upstream tools each launched Chrome their own way (`channel: 'chrome'` on a Mac, the first path that
// exists elsewhere). In a cloud container the first path was a shell wrapper and the page never loaded. This picks a
// real browser binary, adds the right GPU flags per platform, and gives every tool the same timeout.
//
// Environment:
//   CHROME_PATH=/path/to/chrome     use this browser
//   STUDIO_GL=soft                  no GPU: render WebGL in software (SwiftShader), slow but works
//   STUDIO_GL=vulkan | gl-egl       headless Linux with an NVIDIA GPU (see tools/gpu_probe.mjs)
//   STUDIO_TIMEOUT_MS=600000        page start-up timeout (default 120 s, 600 s with STUDIO_GL=soft)
import { existsSync, readdirSync, openSync, readSync, closeSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const newestFirst = (dir, re) => {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((n) => re.test(n)).sort((a, b) => Number(b.split('-').pop()) - Number(a.split('-').pop())).map((n) => join(dir, n));
};

// A shell script that execs a browser is not a browser: puppeteer/playwright talk to it over a pipe and hang.
function isBinary(p) {
  try {
    if (!statSync(p).isFile()) return false;
    const fd = openSync(p, 'r'), b = Buffer.alloc(2); readSync(fd, b, 0, 2, 0); closeSync(fd);
    return b.toString() !== '#!';
  } catch { return false; }
}

export function chromeCandidates() {
  const pw = [...newestFirst('/opt/pw-browsers', /^chromium-\d+$/), ...newestFirst(join(homedir(), '.cache/ms-playwright'), /^chromium-\d+$/)]
    .flatMap((d) => [join(d, 'chrome-linux64/chrome'), join(d, 'chrome-linux/chrome'), join(d, 'chrome-mac/Chromium.app/Contents/MacOS/Chromium')]);
  return [
    process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    ...pw,
    '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ].filter(Boolean);
}

export function findChrome() {
  for (const p of chromeCandidates()) if (existsSync(p) && (process.platform === 'win32' || isBinary(p))) return p;
  return null;
}

export const softGL = () => process.env.STUDIO_GL === 'soft';
export const navTimeout = () => Number(process.env.STUDIO_TIMEOUT_MS || (softGL() ? 600000 : 120000));

export function chromeArgs(extra = []) {
  const gl = process.env.STUDIO_GL;
  const gpu = gl === 'soft' ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
    : gl === 'vulkan' ? ['--use-angle=vulkan', '--enable-features=Vulkan']
    : gl === 'gl-egl' ? ['--use-angle=gl-egl']
    : process.platform === 'darwin' ? ['--use-angle=metal']
    : process.platform === 'win32' ? ['--use-angle=d3d11'] : ['--use-gl=angle'];
  // Ubuntu 23.10+ and root containers block Chrome's sandbox in headless use; local files need no sandbox.
  const sandbox = process.platform === 'linux' ? ['--no-sandbox'] : [];
  return [...sandbox, '--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--disable-renderer-backgrounding',
    '--disable-background-timer-throttling', '--allow-file-access-from-files', ...gpu, ...extra];
}

// Launch options for playwright-core's chromium.launch(). Falls back to the installed Chrome channel.
export function playwrightOptions(extra = []) {
  const exe = findChrome();
  if (!exe) return { channel: 'chrome', headless: true, args: chromeArgs(extra) };
  return { executablePath: exe, headless: true, args: chromeArgs(extra) };
}

export async function launch(extra = []) {
  const { chromium } = await import('playwright-core');
  return chromium.launch(playwrightOptions(extra));
}

// The canvas a film is captured from: window.FILM_CANVAS if the page names one, else the largest canvas.
export const CANVAS_PICK = `(window.FILM_CANVAS || [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0])`;

if (process.argv[1] && process.argv[1].endsWith('browser.mjs')) {
  console.log(JSON.stringify({ chrome: findChrome(), candidates: chromeCandidates(), args: chromeArgs(), timeoutMs: navTimeout() }, null, 2));
}
