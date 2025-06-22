import React, { useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import GalleryPage from './pages/GalleryPage';

function App() {
  // Calcular altura real del viewport para iOS Safari
  useEffect(() => {
    const setVH = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    // Ejecutar al montar
    setVH();

    // Ejecutar en resize y orientationchange para iOS
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', () => {
      // Delay para iOS orientationchange bug
      setTimeout(setVH, 100);
    });

    // Específico para iOS Safari - listener para cambios de viewport
    const handleViewportChange = () => {
      const vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    // Detectar cambios de viewport en iOS (cuando se oculta/muestra la barra de URL)
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleViewportChange();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });

    // Cleanup
    return () => {
      window.removeEventListener('resize', setVH);
      window.removeEventListener('orientationchange', setVH);
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/blog/:slug" element={<GalleryPage />} />
        {/* Mantener ruta antigua por compatibilidad */}
        <Route path="/p/:entradaId" element={<GalleryPage />} />
      </Routes>
    </Router>
  );
}

export default App;
