import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import BlogEntryModal from '../components/BlogEntryModal';

function processImageUrl(url) {
  if (!url) return 'https://via.placeholder.com/800x600?text=No+Image';
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  if (url.startsWith('/media/')) {
    return `${window.location.protocol}//${window.location.host}${url}`;
  }
  if (!url.startsWith('/')) {
    return `${window.location.protocol}//${window.location.host}/media/${url}`;
  }
  return `${window.location.protocol}//${window.location.host}${url}`;
}

const GalleryPage = () => {
  const { entradaId, slug } = useParams(); // Extraer tanto entradaId como slug
  const [searchParams] = useSearchParams();
  const initialFotoId = searchParams.get('foto');

  const navigate = useNavigate();
  const [lugar, setLugar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchGallery() {
      try {
        setLoading(true);
        
        // Determinar si usar slug o ID
        let endpoint;
        if (slug) {
          // Usar la nueva URL con slug
          endpoint = initialFotoId
            ? `/api/blog/${slug}/galeria/${initialFotoId}/`
            : `/api/blog/${slug}/galeria/`;
        } else if (entradaId) {
          // Usar la URL antigua con ID (para compatibilidad)
          endpoint = initialFotoId
            ? `/api/entrada-blog-galeria/${entradaId}/${initialFotoId}/`
            : `/api/entrada-blog-galeria/${entradaId}/`;
        } else {
          throw new Error('No se proporcionó ni slug ni ID de entrada');
        }
        
        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`);
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
            title: galeriaData.entrada.titulo,
            description: galeriaData.entrada.descripcion,
            contenido_procesado: galeriaData.entrada.contenido_procesado || galeriaData.entrada.content,
            content: galeriaData.entrada.content || galeriaData.entrada.contenido_procesado,
            date: galeriaData.entrada.fecha_publicacion,
            fecha_display: galeriaData.entrada.fecha_display,
            mostrar_solo_mes_anio: galeriaData.entrada.mostrar_solo_mes_anio
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

        setLugar(placeData);
      } catch (err) {
        // Error al cargar la galería - mostrar mensaje de error
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchGallery();
  }, [entradaId, slug, initialFotoId]);

  const handleClose = () => {
    navigate('/');
  };

  if (loading) return <div className="loading">Cargando galería...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!lugar) return null;

  return <BlogEntryModal lugar={lugar} onClose={handleClose} />;
};

export default GalleryPage; 