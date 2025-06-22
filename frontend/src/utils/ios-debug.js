/* eslint-disable no-restricted-globals */
// Utilidades para debug en iOS Safari
export const iosDebugUtils = {
  // Detectar si estamos en iOS Safari
  isIOSSafari: () => {
    const ua = navigator.userAgent;
    const iOS = /iPad|iPhone|iPod/.test(ua);
    const webkit = /WebKit/.test(ua);
    const safari = /Safari/.test(ua) && !/Chrome|CriOS|OPiOS|mercury/.test(ua);
    return iOS && webkit && safari;
  },

  // Obtener información del viewport
  getViewportInfo: () => {
    return {
      windowWidth: window.innerWidth,
      windowHeight: window.innerHeight,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      devicePixelRatio: window.devicePixelRatio,
      orientation: window.orientation || screen.orientation?.angle || 0,
      userAgent: navigator.userAgent,
      isIOSSafari: iosDebugUtils.isIOSSafari(),
      safeAreaInsets: {
        top: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-top'),
        bottom: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-bottom'),
        left: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-left'),
        right: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-right')
      },
      customVH: getComputedStyle(document.documentElement).getPropertyValue('--vh')
    };
  },

  // Mostrar overlay de debug
  showDebugOverlay: () => {
    if (document.getElementById('ios-debug-overlay')) return;

    const overlay = document.createElement('div');
    overlay.id = 'ios-debug-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px;
      border-radius: 5px;
      font-size: 10px;
      z-index: 10000;
      font-family: monospace;
      max-width: 200px;
      word-wrap: break-word;
    `;

    const updateInfo = () => {
      const info = iosDebugUtils.getViewportInfo();
      overlay.innerHTML = `
        <div><strong>iOS Debug</strong></div>
        <div>Window: ${info.windowWidth}x${info.windowHeight}</div>
        <div>Screen: ${info.screenWidth}x${info.screenHeight}</div>
        <div>DPR: ${info.devicePixelRatio}</div>
        <div>Orientation: ${info.orientation}</div>
        <div>iOS Safari: ${info.isIOSSafari ? 'Yes' : 'No'}</div>
        <div>Custom VH: ${info.customVH}</div>
        <div>Safe Top: ${info.safeAreaInsets.top}</div>
        <div>Safe Bottom: ${info.safeAreaInsets.bottom}</div>
        <div onclick="document.getElementById('ios-debug-overlay').remove()" style="cursor: pointer; text-align: center; margin-top: 5px; color: #ff6b6b;">✕ Close</div>
      `;
    };

    updateInfo();
    document.body.appendChild(overlay);

    // Actualizar en resize y orientationchange
    const updateHandler = () => setTimeout(updateInfo, 100);
    window.addEventListener('resize', updateHandler);
    window.addEventListener('orientationchange', updateHandler);
    window.addEventListener('scroll', updateHandler);

    // Cleanup después de 30 segundos
    setTimeout(() => {
      if (overlay.parentNode) {
        overlay.remove();
        window.removeEventListener('resize', updateHandler);
        window.removeEventListener('orientationchange', updateHandler);
        window.removeEventListener('scroll', updateHandler);
      }
    }, 30000);
  },

  // Log viewport info en console
  logViewportInfo: () => {
    const info = iosDebugUtils.getViewportInfo();
    console.group('🔍 iOS Viewport Debug Info');
    console.table(info);
    console.groupEnd();
  }
};

// Auto-ejecutar debug en desarrollo si estamos en iOS
if (process.env.NODE_ENV === 'development' && iosDebugUtils.isIOSSafari()) {
  // Mostrar overlay de debug automáticamente
  setTimeout(() => {
    iosDebugUtils.showDebugOverlay();
    iosDebugUtils.logViewportInfo();
  }, 2000);
}

export default iosDebugUtils; 