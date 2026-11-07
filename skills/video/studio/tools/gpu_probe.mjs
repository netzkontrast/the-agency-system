// Which GPU does headless Chrome's WebGL land on? Prints the unmasked renderer for each flag set, so you can pick
// STUDIO_GL (see tools/lib/browser.mjs). Usage: node <studio>/tools/gpu_probe.mjs [chrome path]
import { chromium } from 'playwright-core';
import { findChrome } from './lib/browser.mjs';

const chrome = process.argv[2] || findChrome();
const base = ['--no-sandbox', '--ignore-gpu-blocklist', '--enable-gpu-rasterization'];
const candidates = {
  'default (STUDIO_GL unset)': process.platform === 'darwin' ? ['--use-angle=metal'] : ['--use-gl=angle'],
  'STUDIO_GL=vulkan': ['--use-angle=vulkan', '--enable-features=Vulkan'],
  'STUDIO_GL=gl-egl': ['--use-angle=gl-egl'],
  'STUDIO_GL=soft': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
};
console.log(`browser: ${chrome}`);
for (const [name, flags] of Object.entries(candidates)) {
  let browser;
  try {
    browser = await chromium.launch({ executablePath: chrome, headless: true, args: [...base, ...flags] });
    const page = await browser.newPage();
    const info = await page.evaluate(() => {
      const gl = document.createElement('canvas').getContext('webgl2') || document.createElement('canvas').getContext('webgl');
      if (!gl) return 'no WebGL context';
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
    });
    console.log(`${name.padEnd(26)} ${info}`);
  } catch (e) {
    console.log(`${name.padEnd(26)} FAILED: ${e.message.split('\n')[0]}`);
  } finally {
    await browser?.close();
  }
}
