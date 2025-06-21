import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import './BlogEntryModal.css';

const BlogEntryModal = ({ lugar, onClose }) => {
  const [heroOpacity, setHeroOpacity] = useState(1);

  useEffect(() => {
    // Reset scroll to top so hero is visible
    window.scrollTo({ top: 0, left: 0 });

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const fadeStart = windowHeight * 0.3;
      const fadeEnd = windowHeight * 0.8;
      
      if (scrollY <= fadeStart) {
        setHeroOpacity(1);
      } else if (scrollY >= fadeEnd) {
        setHeroOpacity(0);
      } else {
        const range = fadeEnd - fadeStart;
        const progress = (scrollY - fadeStart) / range;
      setHeroOpacity(1 - progress);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Detect very long titles (e.g., Tayrona) to tweak max-width & font-size via CSS
  const isVeryLongTitle = (title) => {
    if (!title) return false;
    return title.length > 45; // threshold tuned for current design
  };

  const getHeroOverlayClasses = (title) => {
    let classes = 'hero-overlay';
    if (isVeryLongTitle(title)) classes += ' hero-overlay-long-title';
    return classes;
  };

  const getTitleClasses = (title) => {
    let classes = 'blog-title';
    if (isVeryLongTitle(title)) classes += ' blog-title-very-long';
    return classes;
  };

  // Lazy fade-in of every feed image
  useEffect(() => {
    const imgs = document.querySelectorAll('.feed-photo');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    imgs.forEach((img) => observer.observe(img));
    return () => observer.disconnect();
  }, [lugar]);

  // Allow whole-page scroll while modal is open
  useEffect(() => {
    const original = document.body.style.overflow;
    document.body.style.overflow = 'auto';
    return () => {
      document.body.style.overflow = original;
    };
  }, []);

  if (!lugar || !lugar.photos || lugar.photos.length === 0) return null;

  // Helper to normalise photo URLs (copiado de LugarModal)
  const getImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) {
      if (url.includes('/thumbnails/')) {
        return url.replace('/thumbnails/', '/').replace('_thumb.', '.');
      }
      return url;
    }
    if (url.startsWith('/media/')) {
      const fullUrl = `${window.location.protocol}//${window.location.host}${url}`;
      if (url.includes('/thumbnails/')) {
        return fullUrl.replace('/thumbnails/', '/').replace('_thumb.', '.');
      }
      return fullUrl;
    }
    if (!url.startsWith('/')) {
      url = `/media/photos/${url}`;
    }
    return `${window.location.protocol}//${window.location.host}${url}`;
  };

  const firstPhoto = lugar.photos[0];

  // Función para formatear fechas inteligentemente
  const formatDisplayDate = (dateString, showOnlyMonthYear = false) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    if (showOnlyMonthYear) {
      // Formato: "mayo 2024"
      return date.toLocaleDateString('es-ES', {
        month: 'long',
        year: 'numeric'
      }).toUpperCase();
    } else {
      // Formato: "17 JUN 2025"
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      }).toUpperCase();
    }
  };

  // Función para obtener la fecha a mostrar (prioriza fecha_display si existe)
  const getDateToDisplay = (blogEntry) => {
    if (!blogEntry) return null;
    
    // Usar fecha_display si está disponible, sino usar date como fallback
    const dateString = blogEntry.fecha_display || blogEntry.date;
    const showOnlyMonthYear = blogEntry.mostrar_solo_mes_anio || false;
    
    return {
      dateString,
      showOnlyMonthYear,
      formatted: formatDisplayDate(dateString, showOnlyMonthYear)
    };
  };

  return (
    <div className="modal-backdrop">
      {/* Top Navigation */}
      <nav className="top-navigation">
        <div style={{
          position: 'absolute',
          left: '15px',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '200px',
          height: '60px',
          display: 'flex',
          alignItems: 'center',
          backgroundColor: 'transparent',
          pointerEvents: 'none'
        }}>
          <img 
            src="/logo.svg"
            alt="LUNES Logo"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              objectPosition: 'left center',
              pointerEvents: 'none'
            }}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = window.location.origin + '/logo.svg';
            }}
          />
        </div>
        <button className="nav-button" onClick={onClose}>
          Mapa
        </button>
      </nav>

      {/* HERO */}
      <section className="blog-hero" style={{ opacity: heroOpacity }}>
          <div className={getHeroOverlayClasses(lugar.blogEntry?.title || lugar.name)}>
            <h1 className={getTitleClasses(lugar.blogEntry?.title || lugar.name)}>{lugar.blogEntry?.title || lugar.name}</h1>
          {lugar.blogEntry?.description && (
            <p className="blog-description">
              {lugar.blogEntry.description}
            </p>
          )}
        </div>
        
        {/* Scroll indicator */}
        {lugar.blogEntry?.date && (
          <div className="scroll-indicator" style={{ opacity: heroOpacity * 0.7 }}>
            <div className="scroll-arrow"></div>
            <span className="scroll-date">
              {getDateToDisplay(lugar.blogEntry)?.formatted}
            </span>
          </div>
        )}
      </section>

      {/* IMAGE FEED */}
      <section className="blog-photo-feed">
        {lugar.photos.map((photo, idx) => (
          <img
            key={photo.id || idx}
            src={getImageUrl(photo.url)}
            alt={photo.caption || ''}
            className="feed-photo"
            loading="lazy"
          />
        ))}
      </section>

      {/* ARTICLE */}
      {(lugar.blogEntry?.contenido_procesado || lugar.blogEntry?.content) && (
        <section className="blog-article">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw, rehypeSanitize]}
            components={{
              // Personalizar componentes de renderizado
              h1: ({ children }) => <h1 className="blog-h1">{children}</h1>,
              h2: ({ children }) => <h2 className="blog-h2">{children}</h2>,
              h3: ({ children }) => <h3 className="blog-h3">{children}</h3>,
              h4: ({ children }) => <h4 className="blog-h4">{children}</h4>,
              h5: ({ children }) => <h5 className="blog-h5">{children}</h5>,
              h6: ({ children }) => <h6 className="blog-h6">{children}</h6>,
              p: ({ children }) => <p className="blog-paragraph">{children}</p>,
              blockquote: ({ children }) => <blockquote className="blog-quote">{children}</blockquote>,
              code: ({ inline, className, children, ...props }) => {
                return inline ? (
                  <code className="blog-inline-code" {...props}>
                    {children}
                  </code>
                ) : (
                  <code className="blog-code-block" {...props}>
                    {children}
                  </code>
                );
              },
              pre: ({ children }) => <pre className="blog-pre">{children}</pre>,
              img: ({ src, alt }) => (
                <img
                  src={src}
                  alt={alt}
                  className="blog-image"
                  loading="lazy"
                  draggable={false}
                />
              ),
              a: ({ href, children }) => (
                <a 
                  href={href} 
                  className="blog-link"
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  {children}
                </a>
              ),
              table: ({ children }) => <table className="blog-table">{children}</table>,
              ul: ({ children }) => <ul className="blog-list">{children}</ul>,
              ol: ({ children }) => <ol className="blog-ordered-list">{children}</ol>,
              li: ({ children }) => <li className="blog-list-item">{children}</li>,
            }}
          >
            {lugar.blogEntry?.contenido_procesado || lugar.blogEntry?.content || ''}
          </ReactMarkdown>
        </section>
      )}
    </div>
  );
};

export default BlogEntryModal; 