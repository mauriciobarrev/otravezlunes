import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from '!mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax
import './Map.css';

// Token de Mapbox
mapboxgl.accessToken = 'pk.eyJ1IjoibWF1cmljaW9iYXJyZXYiLCJhIjoiY21hdTl3bG53MTVpMjJxb3Njd2xoM2VuMiJ9.piVsma3PVk8ZcTcy4fLEng';

// Datos de ejemplo para usar en caso de fallo
const photosDataFallback = [
  // Santiago photos
  {
    id: 'scl1',
    coordinates: [-70.64827, -33.45694],
    url: 'https://images.unsplash.com/photo-1631850033735-b4c7853b16df?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Atardecer en la ciudad',
    description: 'Uno de los mejores lugares para ver el atardecer en Santiago.',
    location: 'Cerro San Cristóbal',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-15'
  },
  // Más datos de ejemplo...
];

function Map({ onMarkerClick }) {
  const mapContainerRef = useRef(null);
  const [map, setMap] = useState(null);
  const markersRef = useRef([]);
  
  const [lng, setLng] = useState(-70.6444);
  const [lat, setLat] = useState(-33.4423);
  const [zoom, setZoom] = useState(3.5);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [places, setPlaces] = useState([]);

  // Efecto para cargar los datos de la API
  useEffect(() => {
    async function fetchData() {
      try {
        console.log("Intentando cargar datos de la API...");
        setIsLoading(true);
        
        const response = await fetch('/api/mapa-data/');
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Datos recibidos de la API:", data);
        
        if (Array.isArray(data) && data.length > 0) {
          setPlaces(data);
        } else {
          console.warn("No se recibieron datos válidos, usando fallback");
          setPlaces(photosDataFallback);
        }
      } catch (err) {
        console.error("Error al cargar datos:", err);
        setError(err.message);
        setPlaces(photosDataFallback);
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchData();
  }, []);

  // Efecto para inicializar el mapa (solo una vez)
  useEffect(() => {
    if (isLoading) return;
    if (!mapContainerRef.current) return;
    if (map) return; // Prevenir múltiples inicializaciones
    
    console.log("Inicializando mapa");
    
    try {
      // Crear el mapa
      const mapInstance = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/dark-v10',
        center: [lng, lat],
        zoom: zoom,
        interactive: true // Asegurar que el mapa sea interactivo
      });
      
      // Guardar la instancia del mapa en el estado
      setMap(mapInstance);
      
      // Configurar eventos del mapa
      mapInstance.on('move', () => {
        const center = mapInstance.getCenter();
        setLng(center.lng.toFixed(4));
        setLat(center.lat.toFixed(4));
        setZoom(mapInstance.getZoom().toFixed(2));
      });
    } catch (err) {
      console.error("Error al inicializar mapa:", err);
      setError(`Error al inicializar mapa: ${err.message}`);
    }
    
    // Limpieza al desmontar
    return () => {
      if (map) {
        map.remove();
      }
    };
  }, [isLoading, lng, lat, zoom, map]);

  // Efecto para añadir marcadores cuando el mapa está listo
  useEffect(() => {
    if (!map || places.length === 0) return;
    
    console.log("Mapa listo, añadiendo marcadores:", places.length);
    
    // Limpiar marcadores existentes
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];
    
    // Añadir nuevos marcadores
    places.forEach(place => {
      // Verificar que tenemos coordenadas válidas
      const coordinates = place.coordinates;
      if (!coordinates || coordinates.length !== 2) {
        console.warn(`Saltando lugar sin coordenadas válidas:`, place);
        return;
      }
      
      const imgUrl = processImageUrl(place.thumbnail);
      
      // Crear elemento para el marcador
      const el = document.createElement('div');
      el.className = 'custom-marker';
      el.style.backgroundImage = `url(${imgUrl})`;
      el.style.width = '50px';
      el.style.height = '50px';
      el.style.backgroundSize = 'cover';
      el.style.borderRadius = '50%';
      el.style.border = '3px solid white';
      el.style.cursor = 'pointer';
      el.style.boxShadow = '0 2px 10px rgba(0,0,0,0.5)';
      
      // Manejar errores de carga de la imagen de fondo
      const img = new Image();
      img.onload = () => {
        // La imagen cargó correctamente, no hacer nada especial
      };
      img.onerror = () => {
        // Error al cargar la imagen, usar un color de fondo como respaldo
        console.warn(`Error al cargar la imagen para el marcador: ${imgUrl}`);
        el.style.backgroundImage = 'none';
        el.style.backgroundColor = '#51bbd6';
        
        // Agregar la primera letra del nombre como texto
        el.textContent = (place.nombre || 'L').charAt(0).toUpperCase();
        el.style.display = 'flex';
        el.style.alignItems = 'center';
        el.style.justifyContent = 'center';
        el.style.color = 'white';
        el.style.fontSize = '24px';
        el.style.fontWeight = 'bold';
      };
      img.src = imgUrl;
      
      // Crear marcador
      const marker = new mapboxgl.Marker({
        element: el,
        anchor: 'center'
      })
      .setLngLat(coordinates)
      .addTo(map);
      
      // Guardar referencia al marcador
      markersRef.current.push(marker);
      
      // Añadir evento click
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        console.log("Marcador clickeado:", place);
        
        // Intentar obtener información completa del lugar desde la API
        (async () => {
          try {
            const response = await fetch(`/api/lugares/${place.id}/`);
            if (!response.ok) {
              throw new Error(`Error al cargar el lugar: ${response.status}`);
            }
            
            const lugarData = await response.json();
            console.log("Datos del lugar desde API:", lugarData);
            
            // Preparar fotos para la galería
            const fotos = lugarData.fotografias || [];
            
            // Preparar datos para el modal
            const placeData = {
              id: lugarData.id,
              name: lugarData.nombre || place.nombre || 'Lugar sin nombre',
              city: lugarData.ciudad || place.ciudad || '',
              country: lugarData.pais || place.pais || '',
              description: lugarData.descripcion_corta || place.descripcion || 'Sin descripción',
              activePhotoIndex: 0,
              photos: fotos.length > 0 ? fotos.map(foto => ({
                id: foto.id || foto.uuid,
                url: foto.imagen_alta_calidad_url || getHighQualityImageUrl(foto.imagen_url) || foto.imagen_url,
                caption: foto.direccion_captura || `${lugarData.nombre}, ${lugarData.ciudad}, ${lugarData.pais}`,
                date: foto.fecha_toma || '',
                description: foto.descripcion || ''
              })) : [{
                id: place.id || 'photo1',
                url: place.imagen_completa || getHighQualityImageUrl(place.thumbnail) || place.thumbnail || '',
                caption: place.nombre || '',
                date: '',
                description: place.descripcion || 'Sin descripción'
              }]
            };
            
            // Llamar al callback con los datos
            onMarkerClick(placeData);
          } catch (err) {
            console.error("Error al cargar detalles del lugar:", err);
            
            // Usar datos del marcador como fallback
            const placeData = {
              id: place.id,
              name: place.nombre || 'Lugar sin nombre',
              city: place.ciudad || '',
              country: place.pais || '',
              description: place.descripcion || 'Sin descripción',
              activePhotoIndex: 0,
              photos: [{
                id: place.id || 'photo1',
                url: place.imagen_completa || getHighQualityImageUrl(place.thumbnail) || place.thumbnail || '',
                caption: place.nombre || '',
                date: '',
                description: place.descripcion || 'Sin descripción'
              }]
            };
            
            // Llamar al callback con los datos de fallback
            onMarkerClick(placeData);
          }
        })();
      });
    });
    
    // Si hay lugares, centrar el mapa en el primero
    if (places.length > 0 && places[0].coordinates) {
      map.flyTo({
        center: places[0].coordinates,
        zoom: 5,
        essential: true
      });
    }
    
  }, [map, places, onMarkerClick]);

  // Función para procesar URLs de imágenes
  function processImageUrl(url) {
    if (!url) return 'https://via.placeholder.com/800x600?text=No+Image';
    
    // Si ya es una URL completa, devolverla sin cambios
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    
    // Asegurarse de que tenga el formato correcto
    if (url.startsWith('/media/')) {
      return `${window.location.protocol}//${window.location.host}${url}`;
    }
    
    // Si no es una ruta completa, añadir /media/
    if (!url.startsWith('/')) {
      return `${window.location.protocol}//${window.location.host}/media/${url}`;
    }
    
    // Para otros casos, devolver la URL con el host actual
    return `${window.location.protocol}//${window.location.host}${url}`;
  }

  // Función para obtener la URL de alta calidad desde una URL de thumbnail
  function getHighQualityImageUrl(url) {
    if (!url) return '';
    // Reemplazar _thumb. por .
    return url.replace('_thumb.', '.');
  }

  return (
    <div className="map-wrapper">
      <div className="sidebar">
        Longitud: {lng} | Latitud: {lat} | Zoom: {zoom}
      </div>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {isLoading ? (
        <div className="loading">Cargando mapa...</div>
      ) : (
        <div 
          ref={mapContainerRef} 
          className="map-container"
        />
      )}
    </div>
  );
}

export default Map;