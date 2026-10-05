(() => {
  let installEvent = null;
  const standalone = window.matchMedia('(display-mode: standalone)');
  const button = document.getElementById('install-civiceye');
  const installed = () => standalone.matches || navigator.standalone === true;
  const update = () => { button.hidden = !installEvent || installed(); };
  window.addEventListener('beforeinstallprompt', event => {
    if (installed()) return;
    event.preventDefault(); installEvent = event; update();
  });
  button.addEventListener('click', async () => {
    if (!installEvent || installed()) return;
    const event = installEvent; installEvent = null; update();
    try { await event.prompt(); await event.userChoice; }
    catch (error) { console.warn('Browser installation prompt unavailable:', error); }
  });
  window.addEventListener('appinstalled', () => { installEvent = null; update(); });
  standalone.addEventListener('change', update);
  update();
  if ('serviceWorker' in navigator && window.isSecureContext) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js', {scope:'/', updateViaCache:'none'})
        .catch(error => console.warn('CivicEye offline shell registration failed:', error));
    });
  }
  window.addEventListener('offline', () => {
    if (typeof scan === 'undefined' || typeof visionService === 'undefined') return;
    visionService.online = false; visionService.modelLoaded = false;
    visionService.error = 'AI SERVICE OFFLINE — internet connection unavailable.';
    scan.controller?.abort(); clearTimeout(scan.timer); scan.detections = [];
    scan.feed = scan.feed.filter(finding => finding.demo);
    if (scan.mode === 'live') scan.status = 'AI SERVICE OFFLINE';
    updateScanUi();
  });
})();
