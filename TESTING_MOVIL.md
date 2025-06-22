# 📱 Guía de Testing en Dispositivos Móviles

## 🚀 Configuración Inicial

### 1. Ejecutar el Proyecto para Testing Móvil

```bash
# Desde la raíz del proyecto
./run_dev.sh
```

Este script:
- ✅ Configura el backend y frontend para aceptar conexiones desde cualquier IP
- ✅ Muestra la IP local para conectar desde tu móvil
- ✅ Configura automáticamente las variables de entorno necesarias

### 2. Conectar desde tu iPhone 12

1. **Asegúrate de estar en la misma red WiFi** que tu computadora
2. **Toma nota de la IP que muestra el script** (ejemplo: `192.168.1.100`)
3. **Abre Safari en tu iPhone** y ve a: `http://[IP_DE_TU_COMPUTADORA]:3000`

> ⚠️ **Importante**: Usa la IP exacta que te muestra el script, no `localhost`

## 🔍 Herramientas de Debug Incluidas

### Debug Automático en iOS Safari

Cuando accedas desde tu iPhone 12, automáticamente se activará:

1. **Overlay de Debug** (esquina superior derecha):
   - Información del viewport
   - Safe area insets
   - Orientación del dispositivo
   - Se cierra automáticamente en 30 segundos

2. **Logs en Console**:
   - Abre las herramientas de desarrollador en Safari (Mac)
   - Ve a Develop → [Tu iPhone] → [Pestaña del sitio]
   - Verás logs detallados del viewport

### Comandos Manuales de Debug

Si necesitas más información, ejecuta en la consola del navegador:

```javascript
// Mostrar overlay de debug
iosDebugUtils.showDebugOverlay();

// Ver info en console
iosDebugUtils.logViewportInfo();

// Verificar si estás en iOS Safari
iosDebugUtils.isIOSSafari();
```

## 🛠️ Problemas Solucionados

### ✅ Viewport Dinámico en iOS Safari
- **Problema**: El `100vh` no funciona correctamente cuando la barra de URL se oculta/muestra
- **Solución**: Implementado sistema de `--vh` dinámico que se recalcula automáticamente

### ✅ Safe Area en iPhone 12
- **Problema**: Los elementos se cortaban en los bordes por la "safe area"
- **Solución**: Todos los elementos importantes usan `var(--safe-area-inset-*)` automáticamente

### ✅ Controles de Mapbox Cortados
- **Problema**: Los botones de zoom se cortaban en la parte inferior
- **Solución**: Márgenes dinámicos que se ajustan a la safe area del dispositivo

### ✅ Logo del Mapa
- **Problema**: Se cortaba tanto arriba como abajo dependiendo del scroll
- **Solución**: Posicionamiento dinámico que respeta la safe area

### ✅ Modal de Blog
- **Problema**: El título y fecha se cortaban
- **Solución**: Espaciado dinámico y altura de viewport correcta

## 📊 Cómo Probar

### Test 1: Página Principal (Mapa)
1. ✅ El logo se ve completo (no cortado)
2. ✅ Los botones de zoom están visibles y funcionales
3. ✅ Los marcadores se ven correctamente
4. ✅ No hay scroll horizontal

### Test 2: Abrir un Blog
1. ✅ El título se ve completo
2. ✅ La fecha es visible sin necesidad de scroll
3. ✅ La navegación superior no se corta
4. ✅ El botón "Mapa" es accesible

### Test 3: Volver al Mapa
1. ✅ El logo mantiene su posición correcta
2. ✅ Los controles de zoom siguen visibles
3. ✅ No hay elementos cortados

### Test 4: Cambio de Orientación
1. ✅ Girar el dispositivo (portrait ↔ landscape)
2. ✅ Todos los elementos se reajustan correctamente
3. ✅ El viewport se recalcula automáticamente

## 🐛 Si Encuentras Problemas

### Problema: La IP no funciona
**Solución**: 
- Verifica que estés en la misma red WiFi
- Prueba con la IP alternativa que muestra el script
- Reinicia el script: `Ctrl+C` y ejecuta `./run_dev.sh` nuevamente

### Problema: Los estilos no se aplican
**Solución**:
- Fuerza recarga en Safari: Menú → Desarrollador → Vaciar cachés
- O mantén presionado el botón de recarga

### Problema: El debug no aparece
**Solución**:
```javascript
// Ejecutar manualmente en la consola
import('../utils/ios-debug.js').then(module => {
  module.default.showDebugOverlay();
});
```

## 🔧 Herramientas Adicionales

### Safari Web Inspector (Mac)
1. Conecta tu iPhone al Mac con cable
2. En Safari (Mac): Develop → [Tu iPhone] → [Pestaña]
3. Inspecciona elementos directamente en el dispositivo

### Simulador de iOS (Mac)
```bash
# Si tienes Xcode instalado
open -a Simulator
```

## 📋 Checklist Final

Antes de pasar a producción, verifica:

- [ ] Mapa se ve completo en portrait
- [ ] Mapa se ve completo en landscape  
- [ ] Logo siempre visible y bien posicionado
- [ ] Controles de zoom accesibles
- [ ] Blogs se abren correctamente
- [ ] Navegación funciona sin problemas
- [ ] Sin scroll horizontal
- [ ] Sin elementos cortados en ninguna orientación

## 📞 Próximos Pasos

Una vez que todo funcione correctamente en local:

1. **Commit de cambios**:
```bash
git add .
git commit -m "fix: Solucionar problemas de viewport en iOS Safari"
```

2. **Deploy a producción**:
```bash
./deploy.sh
```

3. **Verificar en producción** usando la misma metodología

---

💡 **Tip**: Mantén este archivo actualizado si encuentras otros problemas específicos de iOS Safari. 