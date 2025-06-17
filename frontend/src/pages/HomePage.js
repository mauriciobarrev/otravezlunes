import React from 'react';
import { useNavigate } from 'react-router-dom';
import Map from '../components/Map';

const HomePage = () => {
  const navigate = useNavigate();

  const handleMarkerClick = (lugar) => {
    if (lugar.blogEntry && lugar.blogEntry.id) {
      navigate(`/p/${lugar.blogEntry.id}`);
    } else {
      // Si no hay entrada de blog, no hacer nada
    }
  };

  return <Map onMarkerClick={handleMarkerClick} />;
};

export default HomePage; 