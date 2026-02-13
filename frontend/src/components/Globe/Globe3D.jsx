import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { getLGAData, getTrackedSatellites } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

// Map cache keys for this component
const GLOBE_CACHE_KEYS = {
    LGAS: CACHE_KEYS.LGAS || 'lga_data',
    SATELLITES: CACHE_KEYS.SATELLITE_TRACKED || 'satellite_tracked'
};

// Kebbi State boundary polygon — more accurate coordinates (lon, lat format)
const KEBBI_BOUNDARY = [
    [3.60, 13.05], [3.75, 13.10], [3.90, 13.05], [4.05, 13.00],
    [4.20, 12.95], [4.35, 12.90], [4.50, 12.80], [4.65, 12.70],
    [4.80, 12.55], [4.95, 12.40], [5.10, 12.20], [5.20, 12.00],
    [5.25, 11.80], [5.30, 11.60], [5.25, 11.40], [5.20, 11.20],
    [5.10, 11.00], [4.90, 10.90], [4.70, 10.85], [4.50, 10.80],
    [4.30, 10.85], [4.10, 10.90], [3.90, 11.00], [3.75, 11.10],
    [3.65, 11.30], [3.55, 11.50], [3.50, 11.70], [3.50, 11.90],
    [3.55, 12.10], [3.55, 12.30], [3.55, 12.50], [3.55, 12.70],
    [3.55, 12.90], [3.60, 13.05],
];

// Nigeria outline (simplified)
const NIGERIA_OUTLINE = [
    [2.7, 6.4], [3.3, 6.4], [4.5, 6.3], [5.6, 5.9], [6.5, 6.1], [7.5, 6.0],
    [8.5, 6.5], [9.5, 6.5], [10.0, 7.0], [11.0, 7.0], [12.0, 7.5],
    [13.0, 8.0], [13.5, 9.0], [14.0, 10.0], [14.5, 11.0], [14.0, 12.0],
    [13.5, 13.0], [13.0, 13.5], [12.0, 13.5], [11.0, 13.3], [10.0, 13.3],
    [9.0, 13.5], [8.0, 13.3], [7.0, 13.5], [6.0, 13.5], [5.0, 13.5],
    [4.0, 13.5], [3.5, 13.3], [3.0, 12.5], [2.7, 11.5], [2.7, 10.0],
    [2.7, 8.5], [2.7, 7.5], [2.7, 6.4],
];

const KEBBI_CENTER = { lat: 12.0, lon: 4.2 };
const RISK_COLORS = { critical: '#ff0040', high: '#ff6600', medium: '#f0ff00', low: '#00ff80' };

function latLonToVec3(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
        -radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
    );
}

export default function Globe3D() {
    const mountRef = useRef(null);
    const [lgas, setLgas] = useState([]);
    const [satellites, setSatellites] = useState([]);
    const [hoveredLga, setHoveredLga] = useState(null);

    useEffect(() => {
        // Load from cache first
        const cachedLGAs = dataCache.get(GLOBE_CACHE_KEYS.LGAS);
        const cachedSats = dataCache.get(GLOBE_CACHE_KEYS.SATELLITES);
        if (cachedLGAs?.lgas) setLgas(cachedLGAs.lgas);
        if (cachedSats?.satellites || cachedSats?.tracked_satellites) {
            setSatellites(cachedSats.satellites || cachedSats.tracked_satellites || []);
        }
        
        // Then fetch fresh
        getLGAData().then(d => {
            if (d?.lgas) {
                setLgas(d.lgas);
                dataCache.set(GLOBE_CACHE_KEYS.LGAS, d);
            }
        }).catch(() => { });
        
        getTrackedSatellites().then(d => {
            const sats = d?.satellites || d?.tracked_satellites || [];
            if (sats.length > 0) {
                setSatellites(sats);
                dataCache.set(GLOBE_CACHE_KEYS.SATELLITES, d);
            }
        }).catch(() => { });
    }, []);

    useEffect(() => {
        if (!mountRef.current) return;

        const container = mountRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight || 600;

        // Scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050508);
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);

        // Position camera to look at Kebbi State region (West Africa)
        const kebbiPos = latLonToVec3(KEBBI_CENTER.lat, KEBBI_CENTER.lon, 5.5);
        camera.position.copy(kebbiPos);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.innerHTML = '';
        container.appendChild(renderer.domElement);

        // Single parent group for all rotating objects
        const worldGroup = new THREE.Group();
        scene.add(worldGroup);

        // Globe sphere (dark earth)
        const globeGeometry = new THREE.SphereGeometry(2, 64, 64);
        const globeMaterial = new THREE.MeshPhongMaterial({
            color: 0x0a1428,
            emissive: 0x050a14,
            shininess: 30,
        });
        worldGroup.add(new THREE.Mesh(globeGeometry, globeMaterial));

        // Wireframe overlay (subtle latitude/longitude lines)
        const wireGeometry = new THREE.SphereGeometry(2.003, 36, 18);
        const wireMaterial = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            wireframe: true,
            transparent: true,
            opacity: 0.06,
        });
        worldGroup.add(new THREE.Mesh(wireGeometry, wireMaterial));

        // Atmosphere glow
        const atmosGeometry = new THREE.SphereGeometry(2.12, 64, 64);
        const atmosMaterial = new THREE.ShaderMaterial({
            vertexShader: `
                varying vec3 vNormal;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vNormal;
                void main() {
                    float intensity = pow(0.6 - dot(vNormal, vec3(0,0,1.0)), 2.0);
                    gl_FragColor = vec4(0.0, 0.94, 1.0, 0.2) * intensity;
                }
            `,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide,
            transparent: true,
        });
        scene.add(new THREE.Mesh(atmosGeometry, atmosMaterial));

        // Nigeria outline
        const nigeriaPoints = NIGERIA_OUTLINE.map(([lon, lat]) => latLonToVec3(lat, lon, 2.008));
        const nigeriaGeo = new THREE.BufferGeometry().setFromPoints(nigeriaPoints);
        const nigeriaLine = new THREE.LineLoop(nigeriaGeo, new THREE.LineBasicMaterial({
            color: 0x1a5a7c,
            transparent: true,
            opacity: 0.5,
        }));
        worldGroup.add(nigeriaLine);

        // Kebbi State boundary — glowing cyan border
        const kebbiPoints = KEBBI_BOUNDARY.map(([lon, lat]) => latLonToVec3(lat, lon, 2.012));
        const kebbiGeo = new THREE.BufferGeometry().setFromPoints(kebbiPoints);
        const kebbiBorderMat = new THREE.LineBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.9,
        });
        worldGroup.add(new THREE.LineLoop(kebbiGeo, kebbiBorderMat));

        // Second border line for glow effect
        const kebbiGlow = new THREE.LineLoop(kebbiGeo.clone(), new THREE.LineBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.3,
        }));
        worldGroup.add(kebbiGlow);

        // Kebbi State filled area (semi-transparent)
        const kebbiCenter3D = latLonToVec3(KEBBI_CENTER.lat, KEBBI_CENTER.lon, 2.01);
        const kebbiPoints3D = KEBBI_BOUNDARY.map(([lon, lat]) => latLonToVec3(lat, lon, 2.01));
        const fillVertices = [];
        for (let i = 0; i < kebbiPoints3D.length - 1; i++) {
            fillVertices.push(
                kebbiCenter3D.x, kebbiCenter3D.y, kebbiCenter3D.z,
                kebbiPoints3D[i].x, kebbiPoints3D[i].y, kebbiPoints3D[i].z,
                kebbiPoints3D[i + 1].x, kebbiPoints3D[i + 1].y, kebbiPoints3D[i + 1].z
            );
        }
        const fillGeo = new THREE.BufferGeometry();
        fillGeo.setAttribute('position', new THREE.Float32BufferAttribute(fillVertices, 3));
        const fillMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.12,
            side: THREE.DoubleSide,
        });
        worldGroup.add(new THREE.Mesh(fillGeo, fillMat));

        // LGA markers with labels
        const markerMeshes = [];
        lgas.forEach(lga => {
            const pos = latLonToVec3(lga.lat, lga.lon, 2.025);
            const color = RISK_COLORS[lga.risk] || '#00ff80';
            const colorHex = new THREE.Color(color).getHex();

            // Main marker dot
            const markerGeo = new THREE.SphereGeometry(0.018, 12, 12);
            const markerMat = new THREE.MeshBasicMaterial({ color: colorHex });
            const marker = new THREE.Mesh(markerGeo, markerMat);
            marker.position.copy(pos);
            marker.userData = { name: lga.name, risk: lga.risk, lat: lga.lat, lon: lga.lon };
            worldGroup.add(marker);
            markerMeshes.push(marker);

            // Vertical line from surface
            const lineGeo = new THREE.BufferGeometry().setFromPoints([
                latLonToVec3(lga.lat, lga.lon, 2.005),
                pos,
            ]);
            const lineMat = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: 0.6 });
            worldGroup.add(new THREE.Line(lineGeo, lineMat));

            // Pulsing ring for critical/high
            if (lga.risk === 'critical' || lga.risk === 'high') {
                const ringGeo = new THREE.RingGeometry(0.022, 0.035, 24);
                const ringMat = new THREE.MeshBasicMaterial({
                    color: colorHex,
                    transparent: true,
                    opacity: 0.5,
                    side: THREE.DoubleSide,
                });
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.position.copy(pos);
                ring.lookAt(new THREE.Vector3(0, 0, 0));
                ring.userData = { pulse: true, baseOpacity: 0.5 };
                worldGroup.add(ring);
            }
        });

        // Satellite markers (larger, orange+trail)
        satellites.forEach(sat => {
            const pos = sat.position || sat;
            const lat = pos.latitude || pos.lat;
            const lon = pos.longitude || pos.lon;
            if (!lat || !lon) return;

            const satPos = latLonToVec3(lat, lon, 2.3);
            const satGeo = new THREE.SphereGeometry(0.02, 8, 8);
            const satMat = new THREE.MeshBasicMaterial({ color: 0xffaa00 });
            const satMesh = new THREE.Mesh(satGeo, satMat);
            satMesh.position.copy(satPos);
            worldGroup.add(satMesh);

            // Connection line to surface
            const surfacePos = latLonToVec3(lat, lon, 2.005);
            const connGeo = new THREE.BufferGeometry().setFromPoints([surfacePos, satPos]);
            const connMat = new THREE.LineBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0.15 });
            worldGroup.add(new THREE.Line(connGeo, connMat));
        });

        // Orbit rings (tilted at different angles)
        for (let i = 0; i < 4; i++) {
            const orbitGeo = new THREE.TorusGeometry(2.35 + i * 0.12, 0.002, 8, 100);
            const orbitMat = new THREE.MeshBasicMaterial({
                color: 0x1a3a5c,
                transparent: true,
                opacity: 0.2,
            });
            const orbit = new THREE.Mesh(orbitGeo, orbitMat);
            orbit.rotation.x = Math.PI / 2 + (i * 0.35);
            orbit.rotation.y = i * 0.6;
            scene.add(orbit); // Not in worldGroup so they stay fixed
        }

        // Starfield
        const starsGeo = new THREE.BufferGeometry();
        const starsVerts = [];
        for (let i = 0; i < 3000; i++) {
            starsVerts.push(
                (Math.random() - 0.5) * 120,
                (Math.random() - 0.5) * 120,
                (Math.random() - 0.5) * 120
            );
        }
        starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starsVerts, 3));
        const starsMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.12, transparent: true, opacity: 0.8 });
        scene.add(new THREE.Points(starsGeo, starsMat));

        // Lights
        scene.add(new THREE.AmbientLight(0x445566, 0.6));
        const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
        dirLight.position.set(5, 3, 5);
        scene.add(dirLight);
        const backLight = new THREE.DirectionalLight(0x003355, 0.4);
        backLight.position.set(-5, -2, -5);
        scene.add(backLight);

        // Mouse interaction for rotation
        let isDragging = false;
        let prevMouse = { x: 0, y: 0 };
        // Start with rotation showing Kebbi State
        let rotation = { x: 0, y: 0 };

        const onMouseDown = (e) => {
            isDragging = true;
            prevMouse = { x: e.clientX, y: e.clientY };
        };
        const onMouseMove = (e) => {
            if (!isDragging) return;
            const dx = e.clientX - prevMouse.x;
            const dy = e.clientY - prevMouse.y;
            rotation.y += dx * 0.005;
            rotation.x += dy * 0.005;
            rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x));
            prevMouse = { x: e.clientX, y: e.clientY };
        };
        const onMouseUp = () => { isDragging = false; };
        const onWheel = (e) => {
            camera.position.multiplyScalar(1 + e.deltaY * 0.001);
            const dist = camera.position.length();
            if (dist < 3) camera.position.multiplyScalar(3 / dist);
            if (dist > 12) camera.position.multiplyScalar(12 / dist);
        };

        renderer.domElement.addEventListener('mousedown', onMouseDown);
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('mouseup', onMouseUp);
        renderer.domElement.addEventListener('wheel', onWheel);

        // Animation
        let animId;
        const clock = new THREE.Clock();
        const animate = () => {
            animId = requestAnimationFrame(animate);
            const t = clock.getElapsedTime();

            // Auto-rotate slowly when not dragging
            if (!isDragging) {
                rotation.y += 0.0008;
            }

            // Apply rotation to the entire world group
            worldGroup.rotation.x = rotation.x;
            worldGroup.rotation.y = rotation.y;

            // Pulse rings animation
            worldGroup.children.forEach(child => {
                if (child.userData?.pulse) {
                    child.material.opacity = child.userData.baseOpacity * (0.3 + 0.7 * Math.abs(Math.sin(t * 2)));
                    child.scale.setScalar(1 + 0.15 * Math.sin(t * 2));
                }
            });

            renderer.render(scene, camera);
        };
        animate();

        // Resize handler
        const onResize = () => {
            const w = container.clientWidth;
            const h = container.clientHeight || 600;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        };
        window.addEventListener('resize', onResize);

        return () => {
            cancelAnimationFrame(animId);
            window.removeEventListener('resize', onResize);
            renderer.domElement.removeEventListener('mousedown', onMouseDown);
            renderer.domElement.removeEventListener('mousemove', onMouseMove);
            renderer.domElement.removeEventListener('mouseup', onMouseUp);
            renderer.domElement.removeEventListener('wheel', onWheel);
            renderer.dispose();
        };
    }, [lgas, satellites]);

    return (
        <div>
            <div className="glass-panel" style={{ padding: 12, marginBottom: 12 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.75rem', margin: '0 0 4px' }}>
                    3D ORBITAL VIEW — KEBBI STATE
                </h3>
                <div style={{ fontSize: '0.6rem', color: '#8a94a6' }}>
                    Kebbi State: {KEBBI_CENTER.lat}°N, {KEBBI_CENTER.lon}°E | {lgas.length} LGAs | {satellites.length} Satellites
                </div>
                <div style={{ display: 'flex', gap: 12, marginTop: 6, fontSize: '0.55rem', flexWrap: 'wrap' }}>
                    {Object.entries(RISK_COLORS).map(([level, color]) => (
                        <span key={level} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            <span style={{ width: 8, height: 8, borderRadius: '50%', background: color, display: 'inline-block' }} />
                            {level.charAt(0).toUpperCase() + level.slice(1)}
                        </span>
                    ))}
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ffaa00', display: 'inline-block' }} />
                        Satellite
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 10, height: 2, background: '#00f0ff', display: 'inline-block' }} />
                        Kebbi Border
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ width: 10, height: 2, background: '#1a5a7c', display: 'inline-block' }} />
                        Nigeria Border
                    </span>
                </div>
            </div>

            <div
                ref={mountRef}
                style={{
                    width: '100%',
                    height: 600,
                    borderRadius: 12,
                    overflow: 'hidden',
                    cursor: 'grab',
                }}
            />

            {/* LGA detail panel */}
            {lgas.length > 0 && (
                <div className="glass-panel" style={{ padding: 12, marginTop: 12 }}>
                    <h4 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.65rem', marginBottom: 8 }}>
                        LGA RISK MARKERS ({lgas.length})
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 6 }}>
                        {lgas.map(lga => (
                            <div
                                key={lga.name}
                                style={{
                                    padding: '4px 8px',
                                    borderRadius: 4,
                                    background: 'rgba(255,255,255,0.02)',
                                    borderLeft: `2px solid ${RISK_COLORS[lga.risk]}`,
                                    fontSize: '0.55rem',
                                    cursor: 'pointer',
                                    position: 'relative',
                                    transition: 'background 0.2s',
                                }}
                                onMouseEnter={() => setHoveredLga(lga.name)}
                                onMouseLeave={() => setHoveredLga(null)}
                            >
                                <span style={{ color: RISK_COLORS[lga.risk], fontWeight: 600 }}>{lga.name}</span>
                                <span style={{ color: '#6a7a8c', marginLeft: 4, textTransform: 'uppercase', fontSize: '0.5rem' }}>
                                    {lga.risk}
                                </span>
                                {hoveredLga === lga.name && (
                                    <div style={{
                                        position: 'absolute',
                                        bottom: '110%',
                                        left: 0,
                                        background: 'rgba(10,15,25,0.95)',
                                        border: '1px solid rgba(0,240,255,0.3)',
                                        borderRadius: 6,
                                        padding: 8,
                                        zIndex: 100,
                                        minWidth: 180,
                                        fontSize: '0.55rem',
                                        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                                    }}>
                                        <div style={{ color: '#00f0ff', fontFamily: 'Orbitron', marginBottom: 4 }}>{lga.name}</div>
                                        <div style={{ color: '#8a94a6' }}>
                                            <div>Risk: <span style={{ color: RISK_COLORS[lga.risk] }}>{lga.risk?.toUpperCase()}</span></div>
                                            <div>Coordinates: {lga.lat?.toFixed(4)}°N, {lga.lon?.toFixed(4)}°E</div>
                                            {lga.risk_score !== undefined && (
                                                <div>Risk Score: {(lga.risk_score * 100).toFixed(0)}%</div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
