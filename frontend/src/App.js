import React, { useState } from 'react';
import './App.css';
import Map from './components/Map';
import LugarModal from './components/LugarModal'; // Descomentado

function App() {
  const [lugarSeleccionado, setLugarSeleccionado] = useState(null);

  const handleMarkerClick = (lugar) => {
    console.log('Lugar seleccionado en App.js:', lugar);
    setLugarSeleccionado(lugar);
  };

  const handleCloseModal = () => {
    setLugarSeleccionado(null);
  };

  return (
    <div className="App">
      <Map onMarkerClick={handleMarkerClick} />
      {/* Usar el componente LugarModal real */}
      {lugarSeleccionado && (
        <LugarModal 
          lugar={lugarSeleccionado} 
          onClose={handleCloseModal} 
        />
      )}
    </div>
  );
}

export default App;
