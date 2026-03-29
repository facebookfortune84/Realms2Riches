import { useRef, useEffect } from 'react';
import * as THREE from 'three';

export default function NeuralGlobe() {
  const containerRef = useRef();

  useEffect(() => {
    if (!containerRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(600, 600);
    containerRef.current.appendChild(renderer.domElement);

    // Create a sphere of "Neural Nodes"
    const geometry = new THREE.BufferGeometry();
    const vertices = [];
    const nodeCount = 500;

    for (let i = 0; i < nodeCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / nodeCount);
      const theta = Math.sqrt(nodeCount * Math.PI) * phi;
      
      const x = 200 * Math.cos(theta) * Math.sin(phi);
      const y = 200 * Math.sin(theta) * Math.sin(phi);
      const z = 200 * Math.cos(phi);
      
      vertices.push(x, y, z);
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    
    const material = new THREE.PointsMaterial({
      color: 0x00ff88,
      size: 2,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    // Add connections (Lines)
    const lineMaterial = new THREE.LineBasicMaterial({ 
      color: 0x00ff88, 
      transparent: true, 
      opacity: 0.1 
    });
    
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = [];
    
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < i + 5; j++) {
        const idx1 = i * 3;
        const idx2 = (j % nodeCount) * 3;
        linePositions.push(
          vertices[idx1], vertices[idx1+1], vertices[idx1+2],
          vertices[idx2], vertices[idx2+1], vertices[idx2+2]
        );
      }
    }
    
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    camera.position.z = 400;

    const animate = () => {
      requestAnimationFrame(animate);
      points.rotation.y += 0.002;
      points.rotation.x += 0.001;
      lines.rotation.y += 0.002;
      lines.rotation.x += 0.001;
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      renderer.dispose();
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div className="relative">
      <div ref={containerRef} className="opacity-60" />
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-1 h-1 bg-primary rounded-full shadow-[0_0_50px_20px_rgba(0,255,136,0.2)]" />
      </div>
    </div>
  );
}
