import React from 'react';
import { useNavigate } from 'react-router-dom';
import Map from '../components/Map';

const HomePage = () => {
  const navigate = useNavigate();

  const handleMarkerClick = (lugar) => {
    if (lugar.blogEntry && lugar.blogEntry.id) {
      navigate(`/p/${lugar.blogEntry.id}`);
    } else {
      // Si no hay entrada de blog, podríamos mostrar algún mensaje o un modal opcional
      console.warn('Este marcador no tiene entrada de blog asociada');
    }
  };

  return <Map onMarkerClick={handleMarkerClick} />;
};

export default HomePage; 