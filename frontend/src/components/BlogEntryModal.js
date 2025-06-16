import React, { useEffect, useState } from 'react';
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
      {lugar.blogEntry?.content && (
        <section
          className="blog-article"
          dangerouslySetInnerHTML={{
            __html: lugar.blogEntry.content.replace(/\n/g, '<br/>'),
          }}
        />
      )}
    </div>
  );
};

export default BlogEntryModal; 