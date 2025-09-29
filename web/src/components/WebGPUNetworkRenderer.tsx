// START OF FILE web/src/components/WebGPUNetworkRenderer.tsx
/**
 * HAI-Net WebGPU Network Renderer
 * Constitutional compliance: Decentralization + Performance + Community Focus
 * Hardware-accelerated network visualization using WebGPU
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box, Alert, Typography } from '@mui/material';

// WebGPU Type declarations (until @types/webgpu is available)
declare global {
  interface Navigator {
    gpu?: GPU;
  }
  
  interface GPU {
    requestAdapter(options?: GPURequestAdapterOptions): Promise<GPUAdapter | null>;
    getPreferredCanvasFormat(): GPUTextureFormat;
  }
  
  interface GPUAdapter {
    requestDevice(descriptor?: GPUDeviceDescriptor): Promise<GPUDevice>;
  }
  
  interface GPUDevice {
    createShaderModule(descriptor: GPUShaderModuleDescriptor): GPUShaderModule;
    createBuffer(descriptor: GPUBufferDescriptor): GPUBuffer;
    createBindGroupLayout(descriptor: GPUBindGroupLayoutDescriptor): GPUBindGroupLayout;
    createBindGroup(descriptor: GPUBindGroupDescriptor): GPUBindGroup;
    createRenderPipeline(descriptor: GPURenderPipelineDescriptor): GPURenderPipeline;
    createPipelineLayout(descriptor: GPUPipelineLayoutDescriptor): GPUPipelineLayout;
    createCommandEncoder(descriptor?: GPUCommandEncoderDescriptor): GPUCommandEncoder;
    queue: GPUQueue;
  }
  
  interface GPUCanvasContext {
    configure(configuration: GPUCanvasConfiguration): void;
    getCurrentTexture(): GPUTexture;
  }
  
  interface HTMLCanvasElement {
    getContext(contextId: 'webgpu'): GPUCanvasContext | null;
  }
  
  // Additional WebGPU interfaces
  interface GPUBuffer {}
  interface GPUBindGroup {}
  interface GPURenderPipeline {}
  interface GPUShaderModule {}
  interface GPUBindGroupLayout {}
  interface GPUPipelineLayout {}
  interface GPUCommandEncoder {
    beginRenderPass(descriptor: GPURenderPassDescriptor): GPURenderPassEncoder;
    finish(): GPUCommandBuffer;
  }
  interface GPUQueue {
    writeBuffer(buffer: GPUBuffer, bufferOffset: number, data: ArrayBufferView): void;
    submit(commandBuffers: GPUCommandBuffer[]): void;
  }
  interface GPUTexture {
    createView(): GPUTextureView;
  }
  interface GPUTextureView {}
  interface GPUCommandBuffer {}
  interface GPURenderPassEncoder {
    setPipeline(pipeline: GPURenderPipeline): void;
    setBindGroup(index: number, bindGroup: GPUBindGroup): void;
    setVertexBuffer(slot: number, buffer: GPUBuffer): void;
    draw(vertexCount: number): void;
    end(): void;
  }
  
  // WebGPU Constants
  const GPUBufferUsage: {
    VERTEX: number;
    COPY_DST: number;
    UNIFORM: number;
  };
  
  const GPUShaderStage: {
    VERTEX: number;
    FRAGMENT: number;
  };
  
  // WebGPU Types
  type GPUTextureFormat = string;
  type GPURequestAdapterOptions = any;
  type GPUDeviceDescriptor = any;
  type GPUShaderModuleDescriptor = { label?: string; code: string };
  type GPUBufferDescriptor = { label?: string; size: number; usage: number };
  type GPUBindGroupLayoutDescriptor = any;
  type GPUBindGroupDescriptor = any;
  type GPURenderPipelineDescriptor = any;
  type GPUPipelineLayoutDescriptor = any;
  type GPUCommandEncoderDescriptor = any;
  type GPUCanvasConfiguration = any;
  type GPURenderPassDescriptor = any;
}

// Network node data structure
export interface NetworkNode {
  id: string;
  type: 'local' | 'master' | 'slave' | 'candidate';
  status: 'active' | 'inactive' | 'connecting';
  constitutional_compliant: boolean;
  trust_level: number;
  position: { x: number; y: number };
  connections: string[];
  uptime: number;
}

// Network connection data
export interface NetworkConnection {
  from: string;
  to: string;
  strength: number;
  constitutional_compliant: boolean;
}

// Shader sources
const vertexShaderSource = `
struct VertexOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) color: vec3<f32>,
  @location(1) uv: vec2<f32>,
}

struct Uniforms {
  resolution: vec2<f32>,
  time: f32,
  zoom: f32,
  offset: vec2<f32>,
}

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

@vertex
fn vs_main(
  @location(0) position: vec2<f32>,
  @location(1) color: vec3<f32>,
  @location(2) size: f32,
  @location(3) uv: vec2<f32>
) -> VertexOutput {
  var output: VertexOutput;
  
  // Transform position to screen coordinates
  let scaled_pos = (position + uniforms.offset) * uniforms.zoom;
  let screen_pos = (scaled_pos / uniforms.resolution) * 2.0 - 1.0;
  
  // Apply size scaling
  let final_pos = screen_pos + (uv - 0.5) * size * 2.0 / uniforms.resolution;
  
  output.position = vec4<f32>(final_pos.x, -final_pos.y, 0.0, 1.0);
  output.color = color;
  output.uv = uv;
  
  return output;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  // Create circular nodes
  let center = vec2<f32>(0.5, 0.5);
  let dist = distance(input.uv, center);
  
  // Constitutional glow effect
  let glow = smoothstep(0.5, 0.3, dist);
  let alpha = smoothstep(0.5, 0.4, dist);
  
  // Pulsing effect for constitutional compliance
  let pulse = sin(uniforms.time * 3.14159 * 2.0) * 0.1 + 0.9;
  
  return vec4<f32>(input.color * glow * pulse, alpha);
}
`;

const connectionVertexShader = `
struct VertexOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) color: vec3<f32>,
  @location(1) alpha: f32,
}

struct Uniforms {
  resolution: vec2<f32>,
  time: f32,
  zoom: f32,
  offset: vec2<f32>,
}

@group(0) @binding(0) var<uniform> uniforms: Uniforms;

@vertex
fn vs_main(
  @location(0) position: vec2<f32>,
  @location(1) color: vec3<f32>,
  @location(2) alpha: f32
) -> VertexOutput {
  var output: VertexOutput;
  
  // Transform position to screen coordinates
  let scaled_pos = (position + uniforms.offset) * uniforms.zoom;
  let screen_pos = (scaled_pos / uniforms.resolution) * 2.0 - 1.0;
  
  output.position = vec4<f32>(screen_pos.x, -screen_pos.y, 0.0, 1.0);
  output.color = color;
  output.alpha = alpha;
  
  return output;
}

@fragment
fn fs_main(input: VertexOutput) -> @location(0) vec4<f32> {
  return vec4<f32>(input.color, input.alpha);
}
`;

interface WebGPUNetworkRendererProps {
  nodes: NetworkNode[];
  connections: NetworkConnection[];
  width: number;
  height: number;
  className?: string;
}

export const WebGPUNetworkRenderer: React.FC<WebGPUNetworkRendererProps> = ({
  nodes,
  connections,
  width,
  height,
  className
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [webGPUSupported, setWebGPUSupported] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // WebGPU resources
  const deviceRef = useRef<GPUDevice | null>(null);
  const contextRef = useRef<GPUCanvasContext | null>(null);
  const pipelineRef = useRef<GPURenderPipeline | null>(null);
  const connectionPipelineRef = useRef<GPURenderPipeline | null>(null);
  const uniformBufferRef = useRef<GPUBuffer | null>(null);
  const bindGroupRef = useRef<GPUBindGroup | null>(null);
  
  // Animation state
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  // Check WebGPU support
  useEffect(() => {
    const checkWebGPUSupport = async () => {
      if (!navigator.gpu) {
        setWebGPUSupported(false);
        setError('WebGPU is not supported in this browser. Falling back to Canvas 2D.');
        return;
      }

      try {
        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) {
          setWebGPUSupported(false);
          setError('No WebGPU adapter available.');
          return;
        }

        const device = await adapter.requestDevice();
        deviceRef.current = device;
        setWebGPUSupported(true);
      } catch (err) {
        setWebGPUSupported(false);
        setError(`WebGPU initialization failed: ${err}`);
      }
    };

    checkWebGPUSupport();
  }, []);

  // Initialize WebGPU
  const initWebGPU = useCallback(async () => {
    const canvas = canvasRef.current;
    const device = deviceRef.current;
    
    if (!canvas || !device) return;

    try {
      // Get context
      const context = canvas.getContext('webgpu');
      if (!context) {
        throw new Error('Could not get WebGPU context');
      }
      contextRef.current = context;

      // Configure context
      const presentationFormat = navigator.gpu.getPreferredCanvasFormat();
      context.configure({
        device,
        format: presentationFormat,
        alphaMode: 'premultiplied',
      });

      // Create shaders
      const vertexShaderModule = device.createShaderModule({
        label: 'Node Vertex Shader',
        code: vertexShaderSource,
      });

      const fragmentShaderModule = device.createShaderModule({
        label: 'Node Fragment Shader', 
        code: vertexShaderSource,
      });

      const connectionVertexShaderModule = device.createShaderModule({
        label: 'Connection Vertex Shader',
        code: connectionVertexShader,
      });

      const connectionFragmentShaderModule = device.createShaderModule({
        label: 'Connection Fragment Shader',
        code: connectionVertexShader,
      });

      // Create uniform buffer
      const uniformBuffer = device.createBuffer({
        label: 'Uniforms',
        size: 32, // vec2 + f32 + f32 + vec2 + padding
        usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
      });
      uniformBufferRef.current = uniformBuffer;

      // Create bind group layout
      const bindGroupLayout = device.createBindGroupLayout({
        label: 'Uniform Bind Group Layout',
        entries: [
          {
            binding: 0,
            visibility: GPUShaderStage.VERTEX | GPUShaderStage.FRAGMENT,
            buffer: { type: 'uniform' },
          },
        ],
      });

      // Create bind group
      const bindGroup = device.createBindGroup({
        label: 'Uniform Bind Group',
        layout: bindGroupLayout,
        entries: [
          {
            binding: 0,
            resource: { buffer: uniformBuffer },
          },
        ],
      });
      bindGroupRef.current = bindGroup;

      // Create render pipeline for nodes
      const pipeline = device.createRenderPipeline({
        label: 'Node Render Pipeline',
        layout: device.createPipelineLayout({
          bindGroupLayouts: [bindGroupLayout],
        }),
        vertex: {
          module: vertexShaderModule,
          entryPoint: 'vs_main',
          buffers: [
            {
              arrayStride: 32, // position(8) + color(12) + size(4) + uv(8)
              attributes: [
                { shaderLocation: 0, offset: 0, format: 'float32x2' },  // position
                { shaderLocation: 1, offset: 8, format: 'float32x3' },  // color
                { shaderLocation: 2, offset: 20, format: 'float32' },   // size
                { shaderLocation: 3, offset: 24, format: 'float32x2' }, // uv
              ],
            },
          ],
        },
        fragment: {
          module: fragmentShaderModule,
          entryPoint: 'fs_main',
          targets: [
            {
              format: presentationFormat,
              blend: {
                color: {
                  srcFactor: 'src-alpha',
                  dstFactor: 'one-minus-src-alpha',
                },
                alpha: {
                  srcFactor: 'one',
                  dstFactor: 'one-minus-src-alpha',
                },
              },
            },
          ],
        },
        primitive: {
          topology: 'triangle-list',
        },
      });
      pipelineRef.current = pipeline;

      // Create render pipeline for connections
      const connectionPipeline = device.createRenderPipeline({
        label: 'Connection Render Pipeline',
        layout: device.createPipelineLayout({
          bindGroupLayouts: [bindGroupLayout],
        }),
        vertex: {
          module: connectionVertexShaderModule,
          entryPoint: 'vs_main',
          buffers: [
            {
              arrayStride: 20, // position(8) + color(12)
              attributes: [
                { shaderLocation: 0, offset: 0, format: 'float32x2' },  // position
                { shaderLocation: 1, offset: 8, format: 'float32x3' },  // color
                { shaderLocation: 2, offset: 20, format: 'float32' },   // alpha
              ],
            },
          ],
        },
        fragment: {
          module: connectionFragmentShaderModule,
          entryPoint: 'fs_main',
          targets: [
            {
              format: presentationFormat,
              blend: {
                color: {
                  srcFactor: 'src-alpha',
                  dstFactor: 'one-minus-src-alpha',
                },
                alpha: {
                  srcFactor: 'one',
                  dstFactor: 'one-minus-src-alpha',
                },
              },
            },
          ],
        },
        primitive: {
          topology: 'line-list',
        },
      });
      connectionPipelineRef.current = connectionPipeline;

      // Start rendering loop
      startRenderLoop();
      
    } catch (err) {
      setError(`WebGPU setup failed: ${err}`);
    }
  }, []);

  // Render loop
  const render = useCallback(() => {
    const device = deviceRef.current;
    const context = contextRef.current;
    const pipeline = pipelineRef.current;
    const connectionPipeline = connectionPipelineRef.current;
    const uniformBuffer = uniformBufferRef.current;
    const bindGroup = bindGroupRef.current;
    
    if (!device || !context || !pipeline || !connectionPipeline || !uniformBuffer || !bindGroup) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    // Update uniforms
    const currentTime = (Date.now() - startTimeRef.current) / 1000;
    const uniformData = new Float32Array([
      canvas.width, canvas.height,  // resolution
      currentTime,                  // time
      1.0,                         // zoom
      0.0, 0.0,                    // offset
      0.0, 0.0                     // padding
    ]);
    
    device.queue.writeBuffer(uniformBuffer, 0, uniformData);

    // Create node geometry
    const nodeVertices = createNodeVertices(nodes, canvas.width, canvas.height);
    const nodeVertexBuffer = device.createBuffer({
      label: 'Node Vertices',
      size: nodeVertices.byteLength,
      usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST,
    });
    device.queue.writeBuffer(nodeVertexBuffer, 0, nodeVertices);

    // Create connection geometry
    const connectionVertices = createConnectionVertices(connections, nodes, canvas.width, canvas.height);
    const connectionVertexBuffer = device.createBuffer({
      label: 'Connection Vertices',
      size: connectionVertices.byteLength,
      usage: GPUBufferUsage.VERTEX | GPUBufferUsage.COPY_DST,
    });
    device.queue.writeBuffer(connectionVertexBuffer, 0, connectionVertices);

    // Render
    const commandEncoder = device.createCommandEncoder({ label: 'Render Commands' });
    const textureView = context.getCurrentTexture().createView();
    
    const renderPass = commandEncoder.beginRenderPass({
      label: 'Network Render Pass',
      colorAttachments: [
        {
          view: textureView,
          clearValue: { r: 0.1, g: 0.1, b: 0.1, a: 1.0 }, // Constitutional dark background
          loadOp: 'clear',
          storeOp: 'store',
        },
      ],
    });

    // Render connections first
    renderPass.setPipeline(connectionPipeline);
    renderPass.setBindGroup(0, bindGroup);
    renderPass.setVertexBuffer(0, connectionVertexBuffer);
    renderPass.draw(connectionVertices.length / 5); // 5 floats per vertex

    // Render nodes
    renderPass.setPipeline(pipeline);
    renderPass.setBindGroup(0, bindGroup);
    renderPass.setVertexBuffer(0, nodeVertexBuffer);
    renderPass.draw(nodeVertices.length / 8); // 8 floats per vertex

    renderPass.end();
    device.queue.submit([commandEncoder.finish()]);

    // Schedule next frame
    animationRef.current = requestAnimationFrame(render);
  }, [nodes, connections]);

  const startRenderLoop = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    startTimeRef.current = Date.now();
    render();
  }, [render]);

  // Create node vertex data
  const createNodeVertices = (nodes: NetworkNode[], canvasWidth: number, canvasHeight: number): Float32Array => {
    const vertices: number[] = [];
    
    nodes.forEach(node => {
      const x = (node.position.x / 100) * canvasWidth;
      const y = (node.position.y / 100) * canvasHeight;
      const size = node.type === 'local' ? 40 : (node.type === 'master' ? 30 : 20);
      
      // Constitutional color scheme
      let color: [number, number, number];
      if (!node.constitutional_compliant) {
        color = [1.0, 0.2, 0.2]; // Violation red
      } else if (node.type === 'local') {
        color = [0.3, 0.7, 0.3]; // Constitutional green
      } else if (node.type === 'master') {
        color = [0.2, 0.6, 1.0]; // Trust blue
      } else {
        color = [0.6, 0.6, 0.8]; // Slave purple
      }

      // Create quad for each node (2 triangles = 6 vertices)
      const quadVertices = [
        // Triangle 1
        [x, y, ...color, size, 0, 0],       // top-left
        [x, y, ...color, size, 1, 0],       // top-right  
        [x, y, ...color, size, 0, 1],       // bottom-left
        
        // Triangle 2
        [x, y, ...color, size, 1, 0],       // top-right
        [x, y, ...color, size, 1, 1],       // bottom-right
        [x, y, ...color, size, 0, 1],       // bottom-left
      ];
      
      vertices.push(...quadVertices.flat());
    });
    
    return new Float32Array(vertices);
  };

  // Create connection vertex data
  const createConnectionVertices = (
    connections: NetworkConnection[], 
    nodes: NetworkNode[], 
    canvasWidth: number, 
    canvasHeight: number
  ): Float32Array => {
    const vertices: number[] = [];
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    
    connections.forEach(conn => {
      const fromNode = nodeMap.get(conn.from);
      const toNode = nodeMap.get(conn.to);
      
      if (!fromNode || !toNode) return;
      
      const fromX = (fromNode.position.x / 100) * canvasWidth;
      const fromY = (fromNode.position.y / 100) * canvasHeight;
      const toX = (toNode.position.x / 100) * canvasWidth;
      const toY = (toNode.position.y / 100) * canvasHeight;
      
      // Constitutional connection color
      const color: [number, number, number] = conn.constitutional_compliant 
        ? [0.4, 0.4, 0.4] // Compliant gray
        : [1.0, 0.2, 0.2]; // Violation red
      
      const alpha = conn.strength * 0.7 + 0.3; // Base alpha + strength
      
      // Line vertices
      vertices.push(
        fromX, fromY, ...color, alpha,
        toX, toY, ...color, alpha
      );
    });
    
    return new Float32Array(vertices);
  };

  // Initialize when WebGPU is ready
  useEffect(() => {
    if (webGPUSupported && deviceRef.current) {
      initWebGPU();
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [webGPUSupported, initWebGPU]);

  // Update canvas size
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.width = width;
      canvas.height = height;
    }
  }, [width, height]);

  if (webGPUSupported === false) {
    return (
      <Alert severity="warning" sx={{ m: 2 }}>
        <Typography variant="body2">
          WebGPU is not supported in this browser. Please use a WebGPU-compatible browser for hardware-accelerated visualization.
        </Typography>
      </Alert>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        <Typography variant="body2">{error}</Typography>
      </Alert>
    );
  }

  return (
    <Box className={className} sx={{ position: 'relative', width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          width: '100%',
          height: '100%',
          border: '1px solid #333',
          borderRadius: 4,
          background: '#1a1a1a',
        }}
      />
      
      {/* Constitutional compliance indicator */}
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          left: 8,
          px: 1,
          py: 0.5,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderRadius: 1,
          color: '#4CAF50',
          fontSize: '0.75rem',
        }}
      >
        ⚖️ Constitutional WebGPU Visualization
      </Box>
    </Box>
  );
};

export default WebGPUNetworkRenderer;
