import React, { useRef, useEffect } from 'react';
import TruthMeter from './TruthMeter';
import MagicBento from './MagicBento';
import DotField from './DotField';
import logoImage from './assets/logo-image.png';
import logoText from './assets/logo-text.png';
import { gsap } from 'gsap';
import './App.css';

const CustomCursor = () => {
    const cursorRef = useRef(null);
    const followerRef = useRef(null);

    useEffect(() => {
        const moveCursor = (e) => {
            gsap.to(cursorRef.current, {
                x: e.clientX,
                y: e.clientY,
                duration: 0.1
            });
            gsap.to(followerRef.current, {
                x: e.clientX,
                y: e.clientY,
                duration: 0.3
            });
        };

        window.addEventListener('mousemove', moveCursor);
        return () => window.removeEventListener('mousemove', moveCursor);
    }, []);

    return (
        <>
            <div className="cursor-dot" ref={cursorRef}></div>
            <div className="cursor-follower" ref={followerRef}></div>
        </>
    );
};

const App = () => {
    return (
        <div className="app-wrapper">
            <CustomCursor />

            {/* Main Branding Header (Below DotField but above background) */}
            <header className="main-branding-header">
                <img src={logoImage} alt="OpenOcchio Logo" className="main-logo-image" />
                <img src={logoText} alt="OpenOcchio" className="main-logo-text" />
            </header>

            {/* Background Layer: DotField & MagicBento Grid */}
            <div className="background-layer">
                <div style={{ width: '100vw', height: '100vh', position: 'fixed', top: 0, left: 0, zIndex: 10 }}>
                  <DotField
                    dotRadius={1.5}
                    dotSpacing={30}
                    cursorRadius={350}
                    cursorForce={0.31}
                    bulgeOnly={true}
                    bulgeStrength={60}
                    glowRadius={280}
                    sparkle
                    waveAmplitude={0}
                    gradientFrom="#25cbcf"
                    gradientTo="#ff6a6a"
                    glowColor="#120F17"
                  />
                </div>
                <MagicBento 
                    textAutoHide={true}
                    enableStars={true}
                    enableSpotlight={true}
                    enableBorderGlow={true}
                    enableTilt={true}
                    enableMagnetism={false}
                    clickEffect={true}
                    spotlightRadius={660}
                    particleCount={12}
                    glowColor="132, 0, 255"
                    disableAnimations={false}
                />
            </div>

            {/* Foreground Layer: Chat Interface */}
            <main className="chat-container-fixed">
                <div className="chat-glow-border">
                    <TruthMeter />
                </div>
            </main>
        </div>
    );
};

export default App;
