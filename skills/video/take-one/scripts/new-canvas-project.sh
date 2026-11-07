#!/bin/bash
# Scaffold a canvas film project. Usage: new-canvas-project.sh <dir>
set -e; d="$1"; S="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$d/assets"; cp "$S/serve.mjs" "$S/frames.mjs" "$S/export.mjs" "$S/springs.js" "$d/"
cd "$d"; [ -f package.json ] || echo '{"name":"film","private":true,"type":"module"}' > package.json
npm install --silent playwright-core >/dev/null 2>&1
[ -f film.html ] || cat > film.html <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><title>film</title>
<style>html,body{margin:0;background:#111}canvas{display:block;width:100vw;height:auto;max-height:100vh;object-fit:contain}</style>
<script src="springs.js"></script></head>
<body><canvas id="c"></canvas><script>
const P=new URLSearchParams(location.search).has('portrait');const W=P?1080:1920,H=P?1350:1080;
const c=document.getElementById('c');c.width=W;c.height=H;const g=c.getContext('2d');
window.FILM_DURATION=10;
// motion = springs (Spring.to: one spring per target change, closed form, any t in any order). Linear motion = never.
const CARD_X=[[0,-400],[0.4,W/2-300],[3,W/2-100],[6,W+100]];
window.renderFrame=t=>{g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.filter='none';
  g.fillStyle='#fafaf8';g.fillRect(0,0,W,H);
  const x=Spring.to(t,CARD_X,'camera'),s=0.6+0.4*Spring.unit(t-0.4,'playful');
  g.save();g.translate(x+300,H/2);g.scale(s,s);g.fillStyle='#111';g.font='700 120px system-ui';g.textAlign='center';g.fillText('t = '+t.toFixed(2),0,40);g.restore();};
document.fonts.ready.then(()=>{window.READY=true;if(navigator.webdriver)return;let s=performance.now();const loop=n=>{window.renderFrame(((n-s)/1000)%window.FILM_DURATION);requestAnimationFrame(loop)};requestAnimationFrame(loop);});
</script></body></html>
HTML
echo "project ready at $d (edit film.html; springs in springs.js; review with: node frames.mjs 0 0,1,2)"
