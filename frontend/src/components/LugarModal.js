import React, { useState, useEffect } from 'react';
import './LugarModal.css'; // Crearemos este archivo CSS después

const LugarModal = ({ lugar, onClose }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    // Usar activePhotoIndex si está disponible, sino usar 0
    if (lugar && lugar.activePhotoIndex !== undefined && lugar.activePhotoIndex >= 0) {
      setCurrentIndex(lugar.activePhotoIndex);
    } else {
      setCurrentIndex(0);
    }
  }, [lugar]);

  if (!lugar || !lugar.photos || lugar.photos.length === 0) {
    return null; // No mostrar nada si no hay lugar o no hay fotos
  }

  const currentPhoto = lugar.photos[currentIndex];

  const goToPrevious = () => {
    const isFirstPhoto = currentIndex === 0;
    const newIndex = isFirstPhoto ? lugar.photos.length - 1 : currentIndex - 1;
    setCurrentIndex(newIndex);
  };

  const goToNext = () => {
    const isLastPhoto = currentIndex === lugar.photos.length - 1;
    const newIndex = isLastPhoto ? 0 : currentIndex + 1;
    setCurrentIndex(newIndex);
  };

  // Prevenir que el clic dentro del modal lo cierre si el backdrop también tiene un onClick para cerrar.
  const handleModalContentClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}> {/* El backdrop cierra el modal */}
      <div className="gallery-modal-content" onClick={handleModalContentClick}>
        <button className="modal-close-button" onClick={onClose}>&times;</button>
        
        <div className="gallery-image-container">
          <img src={currentPhoto.url} alt={currentPhoto.caption || lugar.name} className="gallery-photo" />
          {lugar.photos.length > 1 && (
            <>
              <button className="gallery-nav-button prev" onClick={goToPrevious}>&#10094;</button>
              <button className="gallery-nav-button next" onClick={goToNext}>&#10095;</button>
            </>
          )}
        </div>

        <div className="gallery-info">
          <h3>{lugar.name}</h3>
          {currentPhoto.caption && <p className="photo-caption">{currentPhoto.caption}</p>}
          <p className="photo-counter">{currentIndex + 1} / {lugar.photos.length}</p>
          <p className="lugar-description">{lugar.description}</p>
          {/* Aquí podrías añadir un botón para la entrada de blog si existe */}
        </div>

      </div>
    </div>
  );
};

export default LugarModal; 