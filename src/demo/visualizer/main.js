import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { VRButton } from 'three/addons/webxr/VRButton.js';


// SCENE
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x888888);

// CAMERA
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 5000);
camera.position.set(0, 1, 3); // Position the camera for VR


// RENDERER
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// WEBXR
renderer.xr.enabled = true; // Enable WebXR for VR functionality
document.body.appendChild(VRButton.createButton(renderer));
// Movement variables
const movementSpeed = 0.05; // Adjust the speed of movement
const direction = new THREE.Vector3(); // To calculate movement direction
const quaternion = new THREE.Quaternion(); // To rotate based on the headset's orientation


// Add OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // Smooth out the motion
controls.dampingFactor = 0.1;
controls.screenSpacePanning = false; // Prevent panning up and down
controls.minDistance = 0.5; // Minimum zoom distance
controls.maxDistance = 10; // Maximum zoom distance

// Set up WebSocket to receive point cloud data
const ws = new WebSocket(`ws://${window.location.hostname}:8765`);
ws.binaryType = "arraybuffer"; // Receive data as an ArrayBuffer

// Geometry
let dynamicGeometry = new THREE.BufferGeometry();
const material = new THREE.PointsMaterial({ size: 0.025, vertexColors: true });
const points = new THREE.Points(dynamicGeometry, material);
let maxPoints = 300000; // Throttle with 300 000 intial points
scene.add(points);

// Intialize with maxPoints
dynamicGeometry.setAttribute(
    'position',
    new THREE.BufferAttribute(new Float32Array(maxPoints * 3), 3)
);
dynamicGeometry.setAttribute(
    'color',
    new THREE.Uint8BufferAttribute(new Uint8Array(maxPoints * 3), 3, true)
);


let gotNewFrame = false;

const pointSize = 2 * 3; // 3 * float16
const colorSize = 3;     // 3 * uint8
const stride = pointSize + colorSize;

ws.onopen = () => {
    console.log('Connected to WebSocket server');
};

// WebSocket receiving loop
ws.onmessage = (event) => {
    const buffer = event.data;
    let pointCount = buffer.byteLength / stride;

    if (!Number.isInteger(pointCount)) {
        console.error("Invalid data size");
        return;
    }

    // Allocate buffers if point count grows
    if (pointCount > maxPoints) {
        pointCount = maxPoints;
    }

    // Decode positions (float16 to float32)
    const uint16Array = new Uint16Array(buffer, 0, pointCount * 3);
    const positions = dynamicGeometry.getAttribute('position').array;
    for (let i = 0; i < uint16Array.length; i++) {
        positions[i] = THREE.DataUtils.fromHalfFloat(uint16Array[i]) * 0.006; 
    }

    // Copy colors directly, normalized in shader
    const colorOffset = pointCount * 6;
    const colors = new Uint8Array(buffer, colorOffset, pointCount * 3);
    dynamicGeometry.getAttribute('color').array.set(colors);

    // Set draw range to the actual number of points
    dynamicGeometry.setDrawRange(0, pointCount);

    dynamicGeometry.attributes.position.needsUpdate = true;
    dynamicGeometry.attributes.color.needsUpdate = true;

    gotNewFrame = true;
};


let initialCenter = null; // To store the center for the first frame

// Center the point cloud in front of the user
function centerPointCloud() {
    if (!dynamicGeometry) return;

    if (initialCenter === null) {
        // Compute bounding box and center only for the first frame
        dynamicGeometry.computeBoundingBox();
        const box = dynamicGeometry.boundingBox;
        initialCenter = new THREE.Vector3();
        box.getCenter(initialCenter);

        console.log("Initial center computed:", initialCenter);
    }

    // Translate geometry using the precomputed center
    dynamicGeometry.translate(-initialCenter.x, -initialCenter.y + 1, -initialCenter.z);
}



// FPS counting
let minFrameTimeMs = 1000 / 60;
let lastRender = 0;

renderer.setAnimationLoop((nowMs) => {
    controls.update(); // smooth even at high XR FPS

    // Throttle to incoming WebSocket FPS OR render whenever a new frame arrives
    //if ((gotNewFrame && nowMs - lastRender >= minFrameTimeMs) || renderer.xr.isPresenting) {
    if ((gotNewFrame && nowMs - lastRender >= minFrameTimeMs) ) {
        renderer.render(scene, camera);
        lastRender = nowMs;
        gotNewFrame = false;
    }
});