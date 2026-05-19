import React, { useRef, useEffect } from 'react';
import TruthMeter from './TruthMeter';
import MagicBento from './MagicBento';
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
            {/* Background Layer: MagicBento Grid */}
            <div className="background-layer">
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
