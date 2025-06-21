import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from '!mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax
import './Map.css';

// El token de Mapbox ahora se obtiene desde variables de entorno para evitar exponerlo en el repositorio.
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || '';

if (!mapboxgl.accessToken) {
  // Token no definido - el mapa podría no funcionar correctamente
  // En desarrollo se puede verificar en las variables de entorno
}

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
  
  // Obtener estado guardado del localStorage o usar valores por defecto
  const getInitialMapState = () => {
    try {
      const savedState = localStorage.getItem('mapState');
      if (savedState) {
        return JSON.parse(savedState);
      }
    } catch (error) {
      console.warn('Error loading saved map state:', error);
    }
    
    // Valores por defecto centrados en Sudamérica
    return {
      lng: -70.6444,
      lat: -33.4423,
      zoom: 3.5,
      hasInitialFit: false
    };
  };

  const initialState = getInitialMapState();
  const [lng, setLng] = useState(initialState.lng);
  const [lat, setLat] = useState(initialState.lat);
  const [zoom, setZoom] = useState(initialState.zoom);
  const [hasInitialFit, setHasInitialFit] = useState(initialState.hasInitialFit);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [places, setPlaces] = useState([]);

  // Función para guardar el estado del mapa
  const saveMapState = (newLng, newLat, newZoom) => {
    try {
      const mapState = {
        lng: newLng,
        lat: newLat,
        zoom: newZoom,
        hasInitialFit: true
      };
      localStorage.setItem('mapState', JSON.stringify(mapState));
    } catch (error) {
      console.warn('Error saving map state:', error);
    }
  };

  // Función para calcular bounds que incluyan todos los marcadores
  const fitBoundsToMarkers = (mapInstance, placesData) => {
    if (!mapInstance || !placesData || placesData.length === 0) return;

    try {
      // Crear bounds object
      const bounds = new mapboxgl.LngLatBounds();

      // Añadir cada coordenada a los bounds
      placesData.forEach(place => {
        if (place.coordinates && place.coordinates.length === 2) {
          bounds.extend(place.coordinates);
        }
      });

      // Verificar que tenemos bounds válidos
      if (!bounds.isEmpty()) {
        // Hacer fit con padding para mejor visualización
        mapInstance.fitBounds(bounds, {
          padding: {
            top: 50,
            bottom: 50,
            left: 50,
            right: 50
          },
          maxZoom: 12, // Evitar zoom excesivo si los puntos están muy cerca
          duration: 1000 // Animación suave
        });
        
        // Marcar que ya se hizo el fit inicial
        setHasInitialFit(true);
        
        // Guardar el estado después del fit (con un pequeño delay para que termine la animación)
        setTimeout(() => {
          const center = mapInstance.getCenter();
          const newLng = Number(center.lng.toFixed(4));
          const newLat = Number(center.lat.toFixed(4));
          const newZoom = Number(mapInstance.getZoom().toFixed(2));
          
          saveMapState(newLng, newLat, newZoom);
        }, 1100); // Ligeramente después de que termine la animación (1000ms)
      }
    } catch (error) {
      console.warn('Error fitting bounds to markers:', error);
    }
  };

  // Efecto para cargar los datos de la API
  useEffect(() => {
    async function fetchData() {
      try {
        setIsLoading(true);
        
        const response = await fetch('/api/mapa-data/');
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
          setPlaces(data);
        } else {
          setPlaces(photosDataFallback);
        }
      } catch (err) {
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
    
    try {
      // Crear el mapa
      const mapInstance = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/dark-v10',
        center: [lng, lat],
        zoom: zoom,
        interactive: true // Asegurar que el mapa sea interactivo
      });
      
      // Agregar controles de navegación (zoom +/-)
      const navControl = new mapboxgl.NavigationControl({
        showCompass: false, // Ocultar brújula, solo mostrar zoom
        showZoom: true
      });
      mapInstance.addControl(navControl, 'bottom-right');
      
      // Agregar control de geolocalización
      const geolocateControl = new mapboxgl.GeolocateControl({
        positionOptions: {
          enableHighAccuracy: true
        },
        trackUserLocation: false, // No seguir automáticamente
        showUserHeading: false,
        showAccuracyCircle: true,
        fitBoundsOptions: {
          maxZoom: 15 // Zoom máximo cuando localiza al usuario
        }
      });
      mapInstance.addControl(geolocateControl, 'bottom-right');
      
      // Guardar la instancia del mapa en el estado
      setMap(mapInstance);
      
      // Configurar eventos del mapa para guardar estado
      let moveTimeout;
      mapInstance.on('move', () => {
        const center = mapInstance.getCenter();
        const newLng = Number(center.lng.toFixed(4));
        const newLat = Number(center.lat.toFixed(4));
        const newZoom = Number(mapInstance.getZoom().toFixed(2));
        
        setLng(newLng);
        setLat(newLat);
        setZoom(newZoom);
      });
      
      // Guardar estado cuando termine el movimiento (debounced)
      mapInstance.on('moveend', () => {
        clearTimeout(moveTimeout);
        moveTimeout = setTimeout(() => {
          const center = mapInstance.getCenter();
          const newLng = Number(center.lng.toFixed(4));
          const newLat = Number(center.lat.toFixed(4));
          const newZoom = Number(mapInstance.getZoom().toFixed(2));
          
          saveMapState(newLng, newLat, newZoom);
        }, 300); // Debounce de 300ms
      });
      
    } catch (err) {
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
    
    // Limpiar marcadores existentes
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];
    
    // Añadir nuevos marcadores
    places.forEach(place => {
      // Verificar que tenemos coordenadas válidas
      const coordinates = place.coordinates;
      if (!coordinates || coordinates.length !== 2) {
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
        
        // Verificar el tipo de marcador
        if (place.tipo_marcador === 'foto_blog') {
          // Es un marcador individual de foto de entrada de blog
          (async () => {
            try {
              // Usar slug si está disponible, sino usar ID como fallback
              const url = place.entrada_slug 
                ? `/api/blog/${place.entrada_slug}/galeria/${place.foto_id}/`
                : `/api/entrada-blog-galeria/${place.entrada_id}/${place.foto_id}/`;
              
              const response = await fetch(url);
              if (!response.ok) {
                throw new Error(`Error al cargar la entrada de blog: ${response.status}`);
              }
              
              const galeriaData = await response.json();
              
              const placeData = {
                id: galeriaData.lugar.id,
                name: galeriaData.lugar.nombre || 'Lugar sin nombre',
                city: galeriaData.lugar.ciudad || '',
                country: galeriaData.lugar.pais || '',
                description: galeriaData.lugar.descripcion || 'Sin descripción',
                blogEntry: {
                  id: galeriaData.entrada.id,
                  slug: galeriaData.entrada.slug,
                  title: galeriaData.entrada.titulo,
                  content: galeriaData.entrada.contenido_procesado || galeriaData.entrada.content || galeriaData.entrada.contenido_markdown,
                  contenido_procesado: galeriaData.entrada.contenido_procesado || galeriaData.entrada.content || galeriaData.entrada.contenido_markdown,
                  date: galeriaData.entrada.fecha_publicacion,
                  description: galeriaData.entrada.descripcion || ''
                },
                activePhotoIndex: galeriaData.foto_activa_index,
                photos: galeriaData.fotos.map(foto => ({
                  id: foto.id || foto.uuid,
                  url: processImageUrl(foto.url),
                  thumbnail: processImageUrl(foto.thumbnail),
                  caption: foto.caption || foto.description || '',
                  date: foto.date || '',
                  description: foto.description || foto.caption || '',
                  orden: foto.orden || 0
                }))
              };
              
              onMarkerClick(placeData);
            } catch (err) {
              // Fallback usando los datos del marcador
              const placeData = {
                id: place.lugar_id,
                name: place.nombre || 'Lugar sin nombre',
                city: place.ciudad || '',
                country: place.pais || '',
                description: place.descripcion || 'Sin descripción',
                blogEntry: place.entrada_slug ? {
                  id: place.entrada_id,
                  slug: place.entrada_slug,
                  title: place.entrada_titulo
                } : null,
                activePhotoIndex: 0,
                photos: [{
                  id: place.foto_id,
                  url: processImageUrl(place.imagen_completa) || processImageUrl(place.thumbnail),
                  thumbnail: processImageUrl(place.thumbnail),
                  caption: place.foto_descripcion || place.entrada_titulo || '',
                  date: '',
                  description: place.foto_descripcion || ''
                }]
              };
              
              onMarkerClick(placeData);
            }
          })();
        } else {
          // Comportamiento original para lugares simples sin entradas de blog
          (async () => {
            try {
              const response = await fetch(`/api/lugares/${place.lugar_id}/`);
              if (!response.ok) {
                throw new Error(`Error al cargar el lugar: ${response.status}`);
              }
              
              const lugarData = await response.json();
              
              // Preparar fotos para la galería (comportamiento original)
              const fotos = lugarData.fotografias || [];
              
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
              
              onMarkerClick(placeData);
            } catch (err) {
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
              
              onMarkerClick(placeData);
            }
          })();
        }
      });
    });
    
    // Solo hacer auto-fit en la primera carga, no en recargas posteriores
    if (!hasInitialFit && places.length > 0) {
      fitBoundsToMarkers(map, places);
    }
    
  }, [map, places, onMarkerClick, hasInitialFit]);

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
      {/* Mapa */}
      <div 
        ref={mapContainerRef} 
        className="map-container"
        style={{
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0
        }}
      />
      
      {/* Logo */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        left: 'auto',
        zIndex: 1000,
        backgroundColor: 'transparent',
        pointerEvents: 'none',
        maxWidth: '180px',
        maxHeight: '50px'
      }}>
        <img 
          src="/logo.svg"
          alt="LUNES Logo"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            objectPosition: 'right center'
          }}
          onError={(e) => {
            console.error('Error loading logo');
            e.target.onerror = null;
            e.target.src = window.location.origin + '/logo.svg';
          }}
        />
      </div>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {isLoading && (
        <div className="loading">Cargando mapa...</div>
      )}
    </div>
  );
}

export default Map;