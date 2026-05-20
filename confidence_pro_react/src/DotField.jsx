import { useRef, useEffect } from 'react';

const DotField = ({
  dotRadius = 1.5,
  dotSpacing = 14,
  cursorRadius = 500,
  cursorForce = 0.1,
  bulgeOnly = true,
  bulgeStrength = 67,
  glowRadius = 160,
  sparkle = false,
  waveAmplitude = 0,
  gradientFrom = 'rgba(168, 85, 247, 0.35)',
  gradientTo = 'rgba(180, 151, 207, 0.25)',
  glowColor = '#120F17',
  className = ""
}) => {
  const canvasRef = useRef(null);
  const mouseRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      initPoints();
    };

    let points = [];
    const initPoints = () => {
      const cols = Math.ceil(canvas.width / dotSpacing);
      const rows = Math.ceil(canvas.height / dotSpacing);
      const dotCount = cols * rows;

      points = [];
      for (let i = 0; i < dotCount; i++) {
        const x = (i % cols) * dotSpacing;
        const y = Math.floor(i / cols) * dotSpacing;
        points.push({
          x, y,
          originX: x,
          originY: y,
          vx: 0, vy: 0,
          size: dotRadius,
          sparkleFactor: Math.random() > 0.97 ? 1.5 : 1
        });
      }
    };

    window.addEventListener('resize', resize);
    resize();

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    };

    canvas.addEventListener('mousemove', handleMouseMove);

    const render = (time) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw Glow
      if (glowRadius > 0) {
        const gradient = ctx.createRadialGradient(
          mouseRef.current.x, mouseRef.current.y, 0,
          mouseRef.current.x, mouseRef.current.y, glowRadius
        );
        gradient.addColorStop(0, glowColor);
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      // Draw Dots
      points.forEach(p => {
        const dx = mouseRef.current.x - p.x;
        const dy = mouseRef.current.y - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < cursorRadius) {
          const force = (cursorRadius - dist) / cursorRadius;
          if (bulgeOnly) {
            const angle = Math.atan2(dy, dx);
            const bulge = force * bulgeStrength;
            p.x = p.originX - Math.cos(angle) * bulge;
            p.y = p.originY - Math.sin(angle) * bulge;
          } else {
            p.vx += dx * force * cursorForce;
            p.vy += dy * force * cursorForce;
          }
        }

        // Wave effect
        if (waveAmplitude > 0) {
          p.y += Math.sin(time * 0.002 + p.x * 0.01) * waveAmplitude;
        }

        // Physics return to origin
        if (!bulgeOnly) {
            p.vx *= 0.9;
            p.vy *= 0.9;
            p.x += p.vx + (p.originX - p.x) * 0.1;
            p.y += p.vy + (p.originY - p.y) * 0.1;
        } else if (dist >= cursorRadius) {
            p.x += (p.originX - p.x) * 0.1;
            p.y += (p.originY - p.y) * 0.1;
        }

        // Sparkle
        let currentSize = p.size;
        if (sparkle) {
          currentSize *= p.sparkleFactor + Math.sin(time * 0.01) * 0.2;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, Math.max(0, currentSize), 0, Math.PI * 2);
        
        // Diagonal Gradient logic
        const colorPos = (p.x + p.y) / (canvas.width + canvas.height);
        ctx.fillStyle = colorPos > 0.5 ? gradientTo : gradientFrom;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render(0);

    return () => {
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [dotRadius, dotSpacing, cursorRadius, cursorForce, bulgeOnly, bulgeStrength, glowRadius, sparkle, waveAmplitude, gradientFrom, gradientTo, glowColor]);

  return (
    <canvas
      ref={canvasRef}
      className={`dot-field-canvas ${className}`}
      style={{ background: 'transparent', width: '100%', height: '100%' }}
    />
  );
};

export default DotField;
