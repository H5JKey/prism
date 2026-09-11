# Renderer

> Headless OpenGL compute shader physically based path tracer using EGL

---

## Demos

<table>
  <tr>
    <td><img src="images/cornell.png" alt="Cornell box" width="400"></td>
    <td><img src="images/room.png" alt="Room" width="400"></td>
  </tr>
  <tr>
    <td><img src="images/sponza.png" alt="Sponza" width="400"></td>
    <td><img src="images/flight-helmet.png" alt="Flight helmet" width="400"></td>
  </tr>
</table>

---

## Required Libraries

The following libraries must be installed before building with CMake:

- OpenGL 4.6
- EGL
- AWS SDK for C++
- OpenImageDenoise
- Boost
- librdkafka

Docker images include all required system dependencies.

## Build Options

### Build Modes

| Mode | CMake Flag | Docker Build Flag | Output | Description |
|------|-----------|--------|-----------|----------|
| **Core** | `-DBUILD_MODE=CORE` | `BUILD_MODE=CORE` | - | Build only core rendering library for testing |
| **CLI** | `-DBUILD_MODE=CLI` | `BUILD_MODE=CLI` | `renderer_cli` | Standalone CLI application |
| **Worker** | `-DBUILD_MODE=WORKER` | `BUILD_MODE=WORKER` | `renderer_worker` | Build renderer worker for web service |
| **Both** | `-DBUILD_MODE=BOTH` | `BUILD_MODE=BOTH` | `renderer_cli` + `renderer_worker` | Build both CLI and worker versions |

### Build Options

| Option | CMake Flag | Docker Build Flag | Description |
|--------|-----------|---------------|---------|
| **Tests** | `-DBUILD_TESTS=ON` | `BUILD_TESTS=ON` | Build unit tests |

---

## 1. CLI Version

### Build

#### Docker

```bash
docker build --file renderer/Dockerfile -t renderer --build-arg BUILD_MODE=CLI .
```

#### CMake

```bash
cd renderer
mkdir build && cd build
cmake .. -DBUILD_MODE=CLI
cmake --build .
```

### Usage

#### Docker
```bash
docker run --rm renderer renderer_cli <width> <height> <samples> <input_scene> [OPTIONS]
```

#### CMake
```bash
./renderer_cli <width> <height> <samples> <input_scene> [OPTIONS]
```

### Command Line Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `width` | `int` | Output image width |
| `height` | `int` | Output image height |
| `samples` | `int` | Number of samples per pixel |
| `input_scene` | `string` | Path to .glb/.gltf scene file |

### Command Line Options

| Option | Type | Description |
|--------|------|-------------|
| `-h, --help` | `-` | Show help message |
| `-o, --output` | `string` | Output image path (default: output.png) |
| `-v, --verbose` | `-` | Enable detailed logging |
| `-d, --debug` | `-` | Save debug images (raw, albedo, normals) |
| `-p, --plane` | `float` | Add ground plane at scene center with specified size |
| `-c, --camera` | `vec3 vec3 float` | Set camera: `position lookAt fov` |
| `-B, --background` | `vec3` | Set background color (default: vec3(0,0,0)) |
| `-S, --sun` | `vec3 vec3 float` | Set sun: `color direction exponent` |

---

## 2. Worker Version

> [!IMPORTANT] 
> Unlike CLI version, worker can only operate on .glb files (not .gltf).

### Architecture Overview

The worker version consists of two main components:

1. **Service** - Manages task lifecycle, Kafka communication, and S3 storage
2. **Renderer** - Performs the actual rendering using EGL/OpenGL

```
┌─────────┐     ┌───────────────┐    Task Pipe     ┌────────────────┐
│  Kafka  │ ◄─► │               │ ───────────────► │                │
└─────────┘     │    Service    │                  │    Renderer    │     ┌───────┐
                │               │                  │                │ ◄─► │  GPU  │
┌─────────┐     │    (parent)   │ ◄─────────────── │    (child)     │     └───────┘
│  MinIO  │ ◄─► │               │   Result Pipe    │                │
└─────────┘     └───────────────┘                  └────────────────┘

```

### Signal Handling

| Signal | Handler | Effect |
|--------|---------|--------|
| `SIGINT` | Service | Graceful shutdown, forwards to renderer |
| `SIGTERM` | Service | Graceful shutdown, forwards to renderer |
| `SIGINT` | Renderer | Stops current rendering only |
| `SIGTERM` | Renderer | Shuts down the renderer process |

### Build

#### Docker
```bash
docker build --file renderer/Dockerfile -t renderer --build-arg BUILD_MODE=WORKER .
```

#### CMake
```bash
cd renderer
mkdir build && cd build
cmake .. -DBUILD_MODE=WORKER
cmake --build .
```

### Usage

#### Docker
```bash
docker run --rm renderer service
```

#### CMake
```bash
cd renderer/build && ./service
```

### Configuration

The worker can be configured using environment variables or a `.env` file in the `prism/renderer` directory. 

> [!IMPORTANT]
> Environment variables take precedence over values defined in the `.env` file and overwrite `.env` values.

#### Service Configuration

| Variable |  Description | Required | Default |
|----------|--------------|----------|---------|
| `KAFKA_HOST` |	Kafka broker address | Yes | `-` |
| `KAFKA_GROUP_ID` |	Kafka consumer group ID |	Yes | `-` |
| `KAFKA_COMMANDS_GROUP_ID` | Kafka consumer group ID for commands | Yes | `-` |
| `KAFKA_TOPIC_TASKS` | Kafka topic to consume tasks from | Yes | `-` |
| `KAFKA_TOPIC_COMMANDS` | Kafka topic to consume commands from | Yes | `-` |
| `KAFKA_TOPIC_OUTPUT` | Kafka topic to produce messages |	Yes | `-` |
| `KAFKA_TOPIC_DLQ` | Kafka topic for dead letter queue |	Yes | `-` |
| `MAX_RETRIES` | Maximum retry attempts for failed messages |	No | `5` |
| `S3_HOST` |	S3 storage endpoint | Yes | `-` |
| `S3_ACCESS_KEY`	| S3 access key | Yes | `-` |
| `S3_SECRET_KEY`	| S3 secret key	| Yes | `-` |
| `LOG_LEVEL`	| Log level (DEBUG, INFO, WARNING, ERROR)	|	No | `INFO` |
| `LOG_DEBUG`	| Enable debug logging (true/false)	| No | `true` |
| `RENDERER_PREVIEW` | Generate image in lower resolution and only 5 samples (true/false) | No | `false` |

### Preview Mode

The worker can be configured to generate preview images. When preview mode is enabled, the renderer produces lower-quality outputs significantly faster, allowing you to verify scene composition and camera angles before committing to full-resolution renders.

<table>
  <tr>
    <th>Full Render (1920x1080, 1000 samples)</th>
    <th>Preview Mode (200x112, 5 samples)</th> 
  </tr>
  <tr>
    <td><img src="images/original.png" alt="Full render" width="400"></td>
    <td><img src="images/preview.png" alt="Preview mode" width="400"></td>
  </tr>
</table>

### Stop Command

The service supports cancelling the current rendering task via a stop command sent to the commands Kafka topic:

```json
{
  "project_id": 67,
  "command": "stop"
}
```

### Json Format

The renderer worker communicates with other services through JSON messages passed via Kafka.

#### Task

```json
{
  "project_id": 67,
  "input": {
    "bucket": "input",
    "key": "test.glb"
  },
  "output": {
    "bucket": "output",
    "key": "result.png"
  },
  "render": {
    "width": 1920,
    "height": 1080,
    "samples": 128,
    "denoiser": true,
    "gpu": true,
    "background": [0.7, 0.7, 0.95],
    "sun": {
      "direction": [1.0, 1.0, 0.0],
      "color": [20.0, 20.0, 20.0],
      "exponent": 128
    }
  }
}
```

#### Output Result

```json
{
  "project_id": 67,
  "output": {
    "bucket": "output",
    "key": "result.png"
  }
}
```

#### Dead Letter Queue (DLQ)

When a task fails after exhausting all retry attempts, it is sent to the DLQ Kafka topic.

```json
{
  "project_id": 67,
  "reason": "Failed to download scene from S3: connection timeout"
}
```
---

## 3. Testing

#### Docker
```bash
docker build --file renderer/Dockerfile -t renderer --build-arg BUILD_MODE=CORE  --build-arg BUILD_TESTS=ON .
docker run --rm --entrypoint /bin/sh renderer -c "cd build/tests && ctest --output-on-failure"
```
### CMake
```bash
cd renderer
mkdir build && cd build
cmake .. -DBUILD_MODE=CORE
cmake --build .
./test
```
