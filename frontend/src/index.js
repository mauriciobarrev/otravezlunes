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

// Medidas de seguridad y protección de contenido

// Silenciar console.* en producción para no exponer información
if (process.env.NODE_ENV === 'production') {
  ['log', 'warn', 'error', 'info', 'debug'].forEach(method => {
    // eslint-disable-next-line no-console
    console[method] = () => {};
  });
}

// Protección básica de imágenes - deshabilitar menú contextual y arrastrar
document.addEventListener('DOMContentLoaded', () => {
  // Deshabilitar clic derecho en imágenes
  document.addEventListener('contextmenu', (e) => {
    if (e.target && e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
      e.preventDefault();
    }
  });

  // Deshabilitar arrastrar imágenes
  document.addEventListener('dragstart', (e) => {
    if (e.target && e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
      e.preventDefault();
    }
  });

  // Deshabilitar selección de imágenes
  document.addEventListener('selectstart', (e) => {
    if (e.target && e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
      e.preventDefault();
    }
  });
});
