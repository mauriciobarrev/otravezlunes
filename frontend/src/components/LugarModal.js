import React, { useState, useEffect } from 'react';
import './LugarModal.css'; // Crearemos este archivo CSS después

const LugarModal = ({ lugar, onClose }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [errorLoading, setErrorLoading] = useState(false);

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
    
    window.addEventListener('keydown', handleEscape);
    
    return () => {
      window.removeEventListener('keydown', handleEscape);
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
    <div className="modal-backdrop" onClick={onClose}> {/* El backdrop cierra el modal */}
      <div className="gallery-modal-content" onClick={handleModalContentClick}>
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        
        <div className="gallery-image-container">
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
            />
          )}
          
          {lugar.photos.length > 1 && (
            <>
              <button className="gallery-nav-button prev" onClick={goToPrevious}>&#10094;</button>
              <button className="gallery-nav-button next" onClick={goToNext}>&#10095;</button>
            </>
          )}
        </div>

        <div className="gallery-info">
          <h3>{lugar.name}</h3>
          <div className="location-info">
            {lugar.city && lugar.country && (
              <p className="location">{lugar.city}, {lugar.country}</p>
            )}
          </div>
          {currentPhoto.caption && <p className="photo-caption">{currentPhoto.caption}</p>}
          <p className="photo-counter">{currentIndex + 1} / {lugar.photos.length}</p>
          {currentPhoto.date && <p className="photo-date">{currentPhoto.date}</p>}
          {lugar.description && <p className="lugar-description">{lugar.description}</p>}
          {currentPhoto.description && currentPhoto.description !== lugar.description && (
            <p className="photo-description">{currentPhoto.description}</p>
          )}
        </div>

      </div>
    </div>
  );
};

export default LugarModal; 