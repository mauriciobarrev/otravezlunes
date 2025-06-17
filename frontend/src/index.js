import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

// Silenciar console.* en producción y prevenir descarga sencilla de imágenes
if (process.env.NODE_ENV === 'production') {
  ['log', 'warn', 'error', 'info', 'debug'].forEach(method => {
    // eslint-disable-next-line no-console
    console[method] = () => {};
  });
}

// Deshabilitar menú contextual sobre imágenes para dificultar la descarga
// (no es una protección absoluta, pero evita la vía rápida «clic derecho ➜ Guardar»)
document.addEventListener('contextmenu', (e) => {
  if (e.target && e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
    e.preventDefault();
  }
});
