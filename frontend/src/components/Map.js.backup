import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from '!mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax

// Use the token directly - copy it from your .env file
mapboxgl.accessToken = 'pk.eyJ1IjoibWF1cmljaW9iYXJyZXYiLCJhIjoiY21hdTl3bG53MTVpMjJxb3Njd2xoM2VuMiJ9.piVsma3PVk8ZcTcy4fLEng';

// Restructured data model focused on individual photos with their specific locations
const photosData = [
  // Santiago photos
  {
    id: 'scl1',
    coordinates: [-70.64827, -33.45694],
    url: 'https://images.unsplash.com/photo-1631850033735-b4c7853b16df?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Atardecer en la ciudad',
    description: 'Uno de los mejores lugares para ver el atardecer en Santiago. Con su montaña de los andes de fondo, es el lugar ideal para disfrutar de un atardecer en la ciudad.',
    location: 'Cerro San Cristóbal',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-15'
  },
  {
    id: 'scl2',
    coordinates: [-70.65254, -33.44277],
    url: 'https://images.unsplash.com/photo-1689850543263-01a52ccc6943?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Palacio de La Moneda',
    description: 'Sede del poder ejecutivo de Chile, un edificio histórico en el centro de Santiago.',
    location: 'Plaza de la Constitución',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-16'
  },
  {
    id: 'scl3',
    coordinates: [-70.63095, -33.43651],
    url: 'https://images.unsplash.com/photo-1590069521296-294e6c4bec9d?q=80&w=2073&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Cordillera desde el aire',
    description: 'Vista aérea de la Cordillera de los Andes desde Providencia.',
    location: 'Providencia',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-17'
  },
  {
    id: 'scl4',
    coordinates: [-70.62715, -33.42874],
    url: 'https://plus.unsplash.com/premium_photo-1671211752184-0171cef138cb?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Parque Bicentenario',
    description: 'Hermoso parque urbano en Vitacura con lagos y áreas verdes.',
    location: 'Vitacura',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-18'
  },
  {
    id: 'scl5',
    coordinates: [-70.66953, -33.44706],
    url: 'https://plus.unsplash.com/premium_photo-1671211752184-0171cef138cb?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Barrio Lastarria',
    description: 'Colorido barrio cultural con restaurantes y tiendas.',
    location: 'Santiago Centro',
    city: 'Santiago',
    country: 'Chile',
    date: '2022-03-19'
  },
  
  // Valparaíso photos
  {
    id: 'vpo1',
    coordinates: [-71.61269, -33.04591],
    url: 'https://plus.unsplash.com/premium_photo-1671211753023-bcf85b7a4868?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Cerros coloridos',
    description: 'Las casas de colores brillantes en los cerros de Valparaíso, Patrimonio de la Humanidad por UNESCO.',
    location: 'Cerro Alegre',
    city: 'Valparaíso',
    country: 'Chile',
    date: '2022-04-10'
  },
  {
    id: 'vpo2',
    coordinates: [-71.62684, -33.04232],
    url: 'https://plus.unsplash.com/premium_photo-1671211753023-bcf85b7a4868?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Ascensor El Peral',
    description: 'Uno de los históricos funiculares que conectan el plan con los cerros de Valparaíso.',
    location: 'Plan de Valparaíso',
    city: 'Valparaíso',
    country: 'Chile',
    date: '2022-04-11'
  },
  {
    id: 'vpo3',
    coordinates: [-71.62899, -33.05103],
    url: 'https://plus.unsplash.com/premium_photo-1671211753023-bcf85b7a4868?q=80&w=3270&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
    caption: 'Murales en las calles',
    description: 'El arte callejero es parte fundamental de la identidad cultural de Valparaíso.',
    location: 'Cerro Concepción',
    city: 'Valparaíso',
    country: 'Chile',
    date: '2022-04-12'
  },
  
  // Valdivia photos  
  {
    id: 'val1',
    coordinates: [-73.04585, -39.81422],
    url: 'https://images.unsplash.com/photo-1569300592130-31733ef767b0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80',
    caption: 'Río Calle-Calle',
    description: 'El hermoso río que atraviesa la ciudad de Valdivia, conocida como la ciudad de los ríos.',
    location: 'Costanera',
    city: 'Valdivia',
    country: 'Chile',
    date: '2022-05-20'
  },
  {
    id: 'val2',
    coordinates: [-73.25123, -39.82548],
    url: 'https://images.unsplash.com/photo-1603883462451-3aa36399185c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80',
    caption: 'Puente Pedro de Valdivia',
    description: 'Importante puente que cruza el río Valdivia, conectando el centro con la Isla Teja.',
    location: 'Centro',
    city: 'Valdivia',
    country: 'Chile',
    date: '2022-05-21'
  }
];

// Agrupar fotos por ciudad para la galería
const photosByCity = photosData.reduce((acc, photo) => {
  if (!acc[photo.city]) {
    acc[photo.city] = [];
  }
  acc[photo.city].push(photo);
  return acc;
}, {});

// Función para seleccionar una imagen representativa basada en las coordenadas del cluster
const getRepresentativeImage = (coordinates) => {
  // Si no tenemos coordenadas, elegimos una foto al azar
  if (!coordinates || !Array.isArray(coordinates) || coordinates.length < 2) {
    const randomIndex = Math.floor(Math.random() * photosData.length);
    return photosData[randomIndex];
  }

  // Encontrar la foto más cercana a las coordenadas del cluster
  let closestPhoto = null;
  let minDistance = Infinity;

  photosData.forEach(photo => {
    // Calcular distancia aproximada usando distancia euclidiana
    const dx = photo.coordinates[0] - coordinates[0];
    const dy = photo.coordinates[1] - coordinates[1];
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < minDistance) {
      minDistance = distance;
      closestPhoto = photo;
    }
  });

  return closestPhoto || photosData[0]; // Fallback a la primera foto si algo sale mal
};

const Map = ({ onMarkerClick }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [lng, setLng] = useState(-70.9); 
  const [lat, setLat] = useState(-33.45); 
  const [zoom, setZoom] = useState(5);
  const markers = useRef([]);
  const clusters = useRef([]);
  const clusterMarkers = useRef([]);

  // Function to get basic photo info for the popup
  const getPhotoInfo = (id) => {
    return photosData.find(photo => photo.id === id);
  };

  // Function to handle marker click with enhanced data
  const handleMarkerClick = (photo) => {
    if (!photo) return;
    
    // Get all photos from the same city for the gallery
    const relatedPhotos = photosByCity[photo.city] || [];
    
    // Find the index of the clicked photo in the related photos array
    const activePhotoIndex = relatedPhotos.findIndex(p => p.id === photo.id);
    
    // Create an object structure similar to the original one
    const markerData = {
      id: photo.id,
      coordinates: photo.coordinates,
      name: `${photo.location}, ${photo.city}, ${photo.country}`,
      description: photo.description,
      iconicPhotoUrl: photo.url,
      photos: relatedPhotos.map(p => ({
        id: p.id,
        url: p.url,
        caption: p.caption,
        description: p.description
      })),
      activePhotoIndex: activePhotoIndex // Send the index of the clicked photo
    };
    
    onMarkerClick(markerData);
  };

  useEffect(() => {
    if (map.current) return; 
    if (!mapContainer.current) {
        console.error('Error: El contenedor del mapa no está disponible.');
        return;
    }
    if (!mapboxgl.accessToken || mapboxgl.accessToken.startsWith('pk.YOUR_MAPBOX_ACCESS_TOKEN') || mapboxgl.accessToken === 'tu_token_de_mapbox_aqui') {
        console.error('Error: Token de Mapbox no configurado correctamente.');
        if (mapContainer.current) {
            mapContainer.current.innerHTML = '<div style="color: red; padding: 20px;">Error: Mapbox token no configurado.</div>';
        }
        return;
    }

    try {
        map.current = new mapboxgl.Map({
          container: mapContainer.current,
          style: 'mapbox://styles/mapbox/dark-v10',
          center: [lng, lat],
          zoom: zoom
        });

        map.current.on('load', () => {
            console.log('Mapa cargado. Preparando datos para clustering...');
            
            // Add a source for the photos
            map.current.addSource('photos', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: photosData.map(photo => ({
                        type: 'Feature',
                        properties: {
                            id: photo.id,
                            url: photo.url,
                            caption: photo.caption,
                            location: photo.location,
                            city: photo.city,
                            country: photo.country
                        },
                        geometry: {
                            type: 'Point',
                            coordinates: photo.coordinates
                        }
                    }))
                },
                cluster: true,
                clusterMaxZoom: 14, // Max zoom to cluster points on
                clusterRadius: 50 // Radius of each cluster when clustering points
            });
            
            // Add a layer for the clusters - used only for hit-testing
            map.current.addLayer({
                id: 'clusters',
                type: 'circle',
                source: 'photos',
                filter: ['has', 'point_count'],
                paint: {
                    'circle-opacity': 0, // Make the circles invisible
                    'circle-radius': 35 // Keep a reasonable hit area
                }
            });
            
            // Handle click on clusters to zoom in
            map.current.on('click', 'clusters', (e) => {
                const features = map.current.queryRenderedFeatures(e.point, {
                    layers: ['clusters']
                });
                
                if (features.length === 0 || !features[0].properties.cluster_id) return;
                
                const featureClusterId = features[0].properties.cluster_id;
                map.current.getSource('photos').getClusterExpansionZoom(
                    featureClusterId,
                    (err, zoom) => {
                        if (err) return;
                        
                        map.current.easeTo({
                            center: features[0].geometry.coordinates,
                            zoom: zoom
                        });
                    }
                );
            });
            
            // Change cursor when hovering over clusters
            map.current.on('mouseenter', 'clusters', () => {
                map.current.getCanvas().style.cursor = 'pointer';
            });
            
            map.current.on('mouseleave', 'clusters', () => {
                map.current.getCanvas().style.cursor = '';
            });
            
            // Create custom markers for all features (both clusters and individual points)
            const renderMarkers = () => {
                try {
                    // Remove previous markers if they exist
                    markers.current.forEach(marker => marker.remove());
                    markers.current = [];
                    
                    clusterMarkers.current.forEach(marker => marker.remove());
                    clusterMarkers.current = [];
                    
                    // Get all points (both clustered and non-clustered)
                    const features = map.current.querySourceFeatures('photos');
                    if (!features || features.length === 0) return;
                    
                    // Create markers for clusters
                    const clusterFeatures = features.filter(f => f && f.properties && f.properties.cluster);
                    const uniqueClusters = {};
                    
                    clusterFeatures.forEach(feature => {
                        if (!feature || !feature.properties || !feature.properties.cluster_id) return;
                        
                        const featureClusterId = feature.properties.cluster_id;
                        if (!uniqueClusters[featureClusterId]) {
                            uniqueClusters[featureClusterId] = feature;
                        }
                    });
                    
                    // Create custom markers for each cluster
                    Object.values(uniqueClusters).forEach(feature => {
                        if (!feature || !feature.properties || !feature.geometry) return;
                        
                        // Seleccionar una imagen representativa basada en la ubicación del cluster
                        const representativePhoto = getRepresentativeImage(feature.geometry.coordinates);
                        
                        // Obtener el número de puntos en el cluster
                        const featurePointCount = feature.properties.point_count || 0;
                        
                        // Create a marker element
                        const el = document.createElement('div');
                        el.className = 'cluster-marker';
                        
                        // Style the marker
                        const markerSize = Math.min(featurePointCount * 3 + 30, 60);
                        el.style.width = `${markerSize}px`; // Size based on point count, but capped
                        el.style.height = `${markerSize}px`;
                        el.style.borderRadius = '50%';
                        el.style.cursor = 'pointer';
                        el.style.border = '3px solid white';
                        el.style.display = 'flex';
                        el.style.alignItems = 'center';
                        el.style.justifyContent = 'center';
                        el.style.backgroundSize = 'cover';
                        el.style.boxShadow = '0 2px 10px rgba(0,0,0,0.3)';
                        
                        // Establecer la imagen de fondo directamente si tenemos una foto representativa
                        if (representativePhoto && representativePhoto.url) {
                            el.style.backgroundImage = `url(${representativePhoto.url})`;
                        } else {
                            // Fallback styling
                            el.style.backgroundColor = '#51bbd6';
                            el.textContent = featurePointCount.toString();
                            el.style.color = 'white';
                            el.style.fontWeight = 'bold';
                            el.style.textAlign = 'center';
                        }
                        
                        // Add a number badge showing how many photos are in the cluster
                        const badge = document.createElement('div');
                        badge.className = 'cluster-count-badge';
                        badge.textContent = featurePointCount.toString();
                        badge.style.position = 'absolute';
                        badge.style.bottom = '0';
                        badge.style.right = '0';
                        badge.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                        badge.style.color = 'white';
                        badge.style.borderRadius = '50%';
                        badge.style.width = '20px';
                        badge.style.height = '20px';
                        badge.style.display = 'flex';
                        badge.style.alignItems = 'center';
                        badge.style.justifyContent = 'center';
                        badge.style.fontSize = '10px';
                        badge.style.fontWeight = 'bold';
                        badge.style.border = '1px solid white';
                        
                        el.appendChild(badge);
                        
                        // Create the marker and add it to the map
                        const marker = new mapboxgl.Marker(el)
                            .setLngLat(feature.geometry.coordinates)
                            .addTo(map.current);
                        
                        // Add click event to zoom in
                        el.addEventListener('click', (e) => {
                            e.stopPropagation();
                            
                            const source = map.current.getSource('photos');
                            if (!source || typeof source.getClusterExpansionZoom !== 'function') return;
                            
                            const clickedClusterId = feature.properties.cluster_id;
                            source.getClusterExpansionZoom(
                                clickedClusterId,
                                (err, zoom) => {
                                    if (err) return;
                                    
                                    map.current.easeTo({
                                        center: feature.geometry.coordinates,
                                        zoom: zoom
                                    });
                                }
                            );
                        });
                        
                        clusterMarkers.current.push(marker);
                    });
                    
                    // Get all non-clustered photo points
                    const individualFeatures = features.filter(f => 
                        f && f.properties && !f.properties.cluster && f.properties.id);
                    const uniqueFeatures = {};
                    
                    individualFeatures.forEach(feature => {
                        if (!feature || !feature.properties || !feature.properties.id) return;
                        
                        const id = feature.properties.id;
                        if (!uniqueFeatures[id]) {
                            uniqueFeatures[id] = feature;
                        }
                    });
                    
                    // Create markers for each unique photo
                    Object.values(uniqueFeatures).forEach(feature => {
                        if (!feature || !feature.properties || !feature.geometry) return;
                        
                        const props = feature.properties;
                        const photoInfo = getPhotoInfo(props.id);
                        
                        if (photoInfo) {
                            const el = document.createElement('div');
                            el.className = 'marker';
                            el.id = `marker-${props.id}`;
                            
                            el.style.backgroundImage = `url(${photoInfo.url})`;
                            el.style.width = '30px';
                            el.style.height = '30px';
                            el.style.backgroundSize = 'cover';
                            el.style.borderRadius = '50%';
                            el.style.cursor = 'pointer';
                            el.style.border = '2px solid white';
                            
                            const marker = new mapboxgl.Marker(el)
                                .setLngLat(feature.geometry.coordinates)
                                .addTo(map.current);
                            
                            el.addEventListener('click', (e) => {
                                e.stopPropagation();
                                handleMarkerClick(photoInfo);
                            });
                            
                            markers.current.push(marker);
                        }
                    });
                } catch (error) {
                    console.error('Error in renderMarkers:', error);
                }
            };
            
            // Call renderMarkers initially and when the data source is updated
            map.current.on('data', (e) => {
                if (e.sourceId !== 'photos' || !e.isSourceLoaded) return;
                renderMarkers();
            });
            
            // Update markers on map move and zoom
            map.current.on('moveend', renderMarkers);
            map.current.on('zoomend', renderMarkers);
        });

        map.current.on('error', (e) => {
            console.error('Error de Mapbox GL JS:', e.error ? e.error.message : e);
        });

        map.current.on('move', () => {
          setLng(map.current.getCenter().lng.toFixed(4));
          setLat(map.current.getCenter().lat.toFixed(4));
          setZoom(map.current.getZoom().toFixed(2));
        });
    } catch (error) {
        console.error('Excepción al inicializar el mapa de Mapbox:', error);
        if (mapContainer.current) {
            mapContainer.current.innerHTML = '<div style="color: red; padding: 20px;">Excepción al inicializar Mapbox.</div>';
        }
    }

    return () => {
        if (map.current) {
            map.current.remove();
            map.current = null; 
        }
    };
  }, [onMarkerClick]);

  return (
    <div>
      <div className="sidebar">
        Longitud: {lng} | Latitud: {lat} | Zoom: {zoom}
      </div>
      <div ref={mapContainer} className="map-container" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }} />
    </div>
  );
};

export default Map; 