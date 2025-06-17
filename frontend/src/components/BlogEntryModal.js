import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import './BlogEntryModal.css';

const BlogEntryModal = ({ lugar, onClose }) => {
  const [heroOpacity, setHeroOpacity] = useState(1);

  // Fade-out hero while scrolling
  useEffect(() => {
    // Reset scroll to top so hero is visible
    window.scrollTo({ top: 0, left: 0 });

    const onScroll = () => {
      const progress = Math.min(window.scrollY / (window.innerHeight * 0.6), 1);
      setHeroOpacity(1 - progress);
    };
    
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

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

  return (
    <div className="modal-backdrop">
      {/* Top Navigation */}
      <nav className="top-navigation">
        <button className="nav-button" onClick={onClose}>
          Mapa
        </button>
      </nav>

      {/* HERO */}
      <section className="blog-hero" style={{ opacity: heroOpacity }}>
        <div className="hero-overlay">
          <h1 className="blog-title">{lugar.blogEntry?.title || lugar.name}</h1>
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
              {new Date(lugar.blogEntry.date).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
              }).toUpperCase()}
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