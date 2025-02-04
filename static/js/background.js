import * as THREE from 'https://cdn.skypack.dev/three@0.132.2';

class Background {
    constructor() {
        this.container = document.querySelector('#background');
        this.scene = new THREE.Scene();
        this.shapes = [];
        this.mouse = new THREE.Vector2();
        this.target = new THREE.Vector2();
        this.windowHalf = new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2);
        this.createCamera();
        this.createRenderer();
        this.setup();
        this.createShapes();
        this.createParticles();
        this.bindEvents();
        this.render();
    }

    createCamera() {
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 1000);
        this.camera.position.z = 100;
    }

    createRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
    }

    setup() {
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
        document.addEventListener('mousemove', this.onMouseMove.bind(this), false);
    }

    createShapes() {
        const colors = [0x6366f1, 0x8b5cf6, 0xec4899, 0x3b82f6];
        const geometries = [
            // Large objects
            new THREE.TorusGeometry(15, 4, 16, 100),
            new THREE.OctahedronGeometry(12),
            // Medium objects
            new THREE.TetrahedronGeometry(8),
            new THREE.IcosahedronGeometry(6),
            // Small objects
            new THREE.TorusGeometry(5, 2, 16, 100),
            new THREE.OctahedronGeometry(4),
            new THREE.TetrahedronGeometry(3),
            new THREE.IcosahedronGeometry(2)
        ];

        // Create multiple instances of each size
        for (let i = 0; i < geometries.length; i++) {
            const geometry = geometries[i];
            const material = new THREE.MeshPhongMaterial({
                color: colors[i % colors.length],
                wireframe: true,
                transparent: true,
                opacity: 0.6
            });

            // Create 2-3 instances of each shape
            const instances = i < 4 ? 2 : 3; // More small objects than large ones
            for (let j = 0; j < instances; j++) {
                const shape = new THREE.Mesh(geometry, material);
                
                // Distribute objects in a sphere-like pattern
                const radius = 100;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.random() * Math.PI;
                
                shape.position.x = radius * Math.sin(phi) * Math.cos(theta);
                shape.position.y = radius * Math.sin(phi) * Math.sin(theta);
                shape.position.z = radius * Math.cos(phi) * 0.5;
                
                this.shapes.push({
                    mesh: shape,
                    rotationSpeed: {
                        x: (Math.random() - 0.5) * 0.02,
                        y: (Math.random() - 0.5) * 0.02,
                        z: (Math.random() - 0.5) * 0.02
                    },
                    originalPosition: shape.position.clone()
                });
                
                this.scene.add(shape);
            }
        }

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 1);
        pointLight.position.set(50, 50, 50);
        this.scene.add(pointLight);
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const size = 2000;

        for (let i = 0; i < 3000; i++) {
            const x = (Math.random() - 0.5) * size;
            const y = (Math.random() - 0.5) * size;
            const z = (Math.random() - 0.5) * size;
            vertices.push(x, y, z);
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));

        const materials = [
            new THREE.PointsMaterial({
                size: 2,
                color: 0x6366f1,
                transparent: true,
                opacity: 0.8,
                sizeAttenuation: true
            }),
            new THREE.PointsMaterial({
                size: 2,
                color: 0x8b5cf6,
                transparent: true,
                opacity: 0.6,
                sizeAttenuation: true
            })
        ];

        this.particleSystems = materials.map(material => {
            const system = new THREE.Points(geometry, material);
            this.scene.add(system);
            return system;
        });
    }

    onMouseMove(event) {
        this.mouse.x = (event.clientX - this.windowHalf.x);
        this.mouse.y = (event.clientY - this.windowHalf.y);
    }

    onWindowResize() {
        this.windowHalf.set(window.innerWidth / 2, window.innerHeight / 2);
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    bindEvents() {
        window.addEventListener('resize', this.onWindowResize.bind(this));
        document.addEventListener('mousemove', this.onMouseMove.bind(this));
    }

    update() {
        // Update camera position based on mouse
        this.target.x = (1 - this.mouse.x) * 0.002;
        this.target.y = (1 - this.mouse.y) * 0.002;
        this.camera.rotation.x += (this.target.y - this.camera.rotation.x) * 0.05;
        this.camera.rotation.y += (this.target.x - this.camera.rotation.y) * 0.05;

        // Rotate shapes and add floating effect
        const time = Date.now() * 0.001;
        this.shapes.forEach((shape, i) => {
            shape.mesh.rotation.x += shape.rotationSpeed.x;
            shape.mesh.rotation.y += shape.rotationSpeed.y;
            shape.mesh.rotation.z += shape.rotationSpeed.z;

            // Floating effect
            const floatOffset = Math.sin(time + i) * 2;
            shape.mesh.position.x = shape.originalPosition.x + Math.sin(time * 0.5 + i) * 5;
            shape.mesh.position.y = shape.originalPosition.y + floatOffset;
            shape.mesh.position.z = shape.originalPosition.z + Math.cos(time * 0.5 + i) * 5;

            // Pulse effect
            const scale = 1 + Math.sin(time + i) * 0.1;
            shape.mesh.scale.set(scale, scale, scale);
        });

        // Rotate particle systems
        this.particleSystems.forEach((system, i) => {
            system.rotation.x += 0.0001 + (i * 0.0001);
            system.rotation.y += 0.0002 + (i * 0.0001);
        });
    }

    render() {
        requestAnimationFrame(this.render.bind(this));
        this.update();
        this.renderer.render(this.scene, this.camera);
    }
}

window.addEventListener('load', () => {
    new Background();
});
