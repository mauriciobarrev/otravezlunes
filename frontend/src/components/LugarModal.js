import React, { useState, useEffect } from 'react';
import './LugarModal.css'; // Crearemos este archivo CSS después

const LugarModal = ({ lugar, onClose }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [errorLoading, setErrorLoading] = useState(false);
  const [imageOpacity, setImageOpacity] = useState(1);

  useEffect(() => {
    // Usar activePhotoIndex si está disponible, sino usar 0
    if (lugar && lugar.activePhotoIndex !== undefined && lugar.activePhotoIndex >= 0) {
      setCurrentIndex(lugar.activePhotoIndex);
    } else {
      setCurrentIndex(0);
    }
    
    // Reiniciar estado de carga de imagen
    setImageLoaded(false);
    setErrorLoading(false);
    
    // Añadir listener para la tecla Escape
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    // Permitir scroll en el body para la página completa de la galería
    document.body.style.overflow = 'auto';
    
    window.addEventListener('keydown', handleEscape);
    
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const fadeEnd = window.innerHeight * 0.6; // 60% viewport height
      const newOpacity = Math.max(1 - scrollTop / fadeEnd, 0);
      setImageOpacity(newOpacity);
    };
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('keydown', handleEscape);
      // Restaurar scroll del body
      document.body.style.overflow = 'unset';
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lugar, onClose]);

  if (!lugar || !lugar.photos || lugar.photos.length === 0) {
    return null; // No mostrar nada si no hay lugar o no hay fotos
  }

  const currentPhoto = lugar.photos[currentIndex];
  
  // Verificar si tenemos una URL válida
  const hasValidUrl = currentPhoto && currentPhoto.url && typeof currentPhoto.url === 'string';
  
  // Procesar la URL para asegurar que sea accesible
  const getImageUrl = (url) => {
    if (!url) return '';
    
    // Si es una URL absoluta (http o https), usarla directamente
    if (url.startsWith('http://') || url.startsWith('https://')) {
      // Si contiene /thumbnails/, intentar obtener la versión completa
      if (url.includes('/thumbnails/')) {
        return url.replace('/thumbnails/', '/').replace('_thumb.', '.');
      }
      return url;
    }
    
    // Si la URL comienza con /media/, usar la URL completa con el host actual
    if (url.startsWith('/media/')) {
      // Si contiene /thumbnails/, intentar obtener la versión completa
      const fullUrl = `${window.location.protocol}//${window.location.host}${url}`;
      if (url.includes('/thumbnails/')) {
        return fullUrl.replace('/thumbnails/', '/').replace('_thumb.', '.');
      }
      return fullUrl;
    }
    
    // Si no comienza con /, agregar / al principio
    if (!url.startsWith('/')) {
      url = `/media/photos/${url}`;
    }
    
    // Construir la URL completa
    return `${window.location.protocol}//${window.location.host}${url}`;
  };
  
  // Obtener URL procesada
  const imageUrl = hasValidUrl ? getImageUrl(currentPhoto.url) : '';

  const goToPrevious = () => {
    const isFirstPhoto = currentIndex === 0;
    const newIndex = isFirstPhoto ? lugar.photos.length - 1 : currentIndex - 1;
    setCurrentIndex(newIndex);
    setImageLoaded(false);
    setErrorLoading(false);
  };

  const goToNext = () => {
    const isLastPhoto = currentIndex === lugar.photos.length - 1;
    const newIndex = isLastPhoto ? 0 : currentIndex + 1;
    setCurrentIndex(newIndex);
    setImageLoaded(false);
    setErrorLoading(false);
  };

  // Prevenir que el clic dentro del modal lo cierre
  const handleModalContentClick = (e) => {
    e.stopPropagation();
  };
  
  // Manejar el evento de carga de la imagen
  const handleImageLoad = () => {
    setImageLoaded(true);
    setErrorLoading(false);
  };
  
  // Manejar el error de carga de la imagen
  const handleImageError = () => {
    console.error("Error al cargar la imagen:", imageUrl);
    setErrorLoading(true);
    setImageLoaded(false);
  };

  return (
    <div className="modal-backdrop"> {/* Remove onClick since this is now a full page */}
      <div className="gallery-modal-content" onClick={handleModalContentClick}>
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        
        <div className="gallery-image-container" style={{ opacity: imageOpacity }}>
          {!imageLoaded && !errorLoading && (
            <div className="loading-image">Cargando imagen...</div>
          )}
          
          {errorLoading && (
            <div className="error-image">
              <p>Error al cargar la imagen.</p>
              <small>URL: {imageUrl}</small>
            </div>
          )}
          
          {hasValidUrl && (
            <img 
              src={imageUrl} 
              alt={currentPhoto.caption || lugar.name} 
              className={`gallery-photo ${imageLoaded ? 'loaded' : ''}`}
              onLoad={handleImageLoad}
              onError={handleImageError}
              draggable={false}
            />
          )}
          
          {lugar.photos.length > 1 && (
            <>
              <button className="gallery-nav-button prev" onClick={goToPrevious}>&#10094;</button>
              <button className="gallery-nav-button next" onClick={goToNext}>&#10095;</button>
            </>
          )}

          {lugar.photos.length > 1 && (
            <div className="photo-counter-image">
              {currentIndex + 1} / {lugar.photos.length}
            </div>
          )}
        </div>

        <div className="gallery-content">
          {/* Remove gallery-header and show blog entry first */}

          {lugar.blogEntry && (
            <div className="blog-entry-info">
              <h2 className="blog-title">{lugar.blogEntry.title}</h2>
              {lugar.blogEntry.date && (
                <p className="blog-date">
                  {new Date(lugar.blogEntry.date).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              )}
              <div className="blog-content">
                {(lugar.blogEntry.contenido_procesado || lugar.blogEntry.content) && (
                  <div dangerouslySetInnerHTML={{
                    __html: (lugar.blogEntry.contenido_procesado || lugar.blogEntry.content).replace(/\n/g, '<br/>')
                  }} />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LugarModal; 