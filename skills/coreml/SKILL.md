---
name: coreml
description: "Integrates and profiles Core ML models for on-device inference. Use for mlmodel/mlpackage loading, generated or feature-provider predictions, compute-unit selection, MLTensor, Vision integration, MLComputePlan, model pipelines, deployment, or performance analysis."
---

# Core ML Swift Integration

Load, configure, and run Core ML models in iOS apps. Covers Swift model loading, synchronous/async inference, batch prediction, MLTensor, profiling, and memory management.

> **Scope boundary:** Python-side model conversion, quantization, and pruning belong in `apple-on-device-ai`. This skill owns Swift-side integration only.

## Contents

- [Loading Models](#loading-models)
- [Model Configuration](#model-configuration)
- [Making Predictions](#making-predictions)
- [MLTensor (iOS 18+)](#mltensor-ios-18)
- [Vision Integration](#vision-integration)
- [Performance & Memory](#performance--memory)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Loading Models

- **Auto-Generated Class**: Add `.mlmodel` or `.mlpackage` to the target; Xcode generates typed input/output classes.
- **Async Loading (iOS 15+)**: Avoid blocking the main thread: `try await MLModel.load(contentsOf: url, configuration: config)`.
- **Runtime Compilation (iOS 16+)**: Compile downloaded packages with `MLModel.compileModel(at: url)`. Cache the resulting `.mlmodelc` URL in Application Support; recompiling on every launch is an error.

```swift
import CoreML

let config = MLModelConfiguration()
config.computeUnits = .all

// Typed model initialization
let classifier = try MyImageClassifier(configuration: config)

// Dynamic async loading
let model = try await MLModel.load(contentsOf: modelURL, configuration: config)
```

## Model Configuration

`MLModelConfiguration` controls compute dispatch:

| Value | Hardware Target | Best For |
|---|---|---|
| `.all` | CPU + GPU + Neural Engine | Default. Best overall performance. |
| `.cpuAndNeuralEngine` | CPU + Neural Engine | Energy efficiency, keeping GPU free for rendering. |
| `.cpuAndGPU` | CPU + GPU | Models with operations unsupported by Neural Engine. |
| `.cpuOnly` | CPU only | Deterministic tests, profiling baseline, background tasks. |

## Making Predictions

`MLModel.prediction(...)` is synchronous. Keep model loading asynchronous, then dispatch synchronous predictions from an actor or background task without adding `await` to `prediction()`.

```swift
// 1. Typed prediction
let input = MyImageClassifierInput(image: pixelBuffer)
let output = try classifier.prediction(input: input)

// 2. Dynamic feature provider
let features = try MLDictionaryFeatureProvider(dictionary: ["image": MLFeatureValue(pixelBuffer: pixelBuffer)])
let dynamicOutput = try model.prediction(from: features)

// 3. Batch prediction (better throughput)
let batch = try MLArrayBatchProvider(array: featureArray)
let batchResults = try model.predictions(fromBatch: batch)

// 4. Stateful prediction (iOS 18+ for sequences/LLMs)
let state = model.makeState()
let stateOutput = try model.prediction(from: features, using: state)
```

Predictions sharing the same `MLState` must be serialized; allocate independent `MLState` instances for concurrent streams.

## MLTensor (iOS 18+)

`MLTensor` provides Swift-native multidimensional tensor math with lazy evaluation:

```swift
let tensor = MLTensor([1.0, 2.0, 3.0, 4.0]).reshaped(to: [2, 2])
let softmax = tensor.softmax(alongAxis: -1)

// Materialize asynchronously
let shapedArray = await softmax.shapedArray(of: Float.self)
let multiArray = try MLMultiArray(shapedArray)
```

## Vision Integration

Prefer Vision pipelines to automatically handle image orientation, resizing, and pixel buffer formatting:

- **iOS 18+**: Use `CoreMLRequest` with Swift async/await concurrency.
- **Legacy (iOS 11-17)**: Use `VNCoreMLModel(for: model)` with `VNCoreMLRequest` and `VNImageRequestHandler`.

## Performance & Memory

- **MLComputePlan (iOS 17.4+)**: Inspect execution dispatch per operation prior to inference: `try await MLComputePlan.load(contentsOf: url, configuration: config)`.
- **Instruments**: Profile with the Core ML template outside Xcode debugger to measure latency and ANE offload.
- **Lifecycle & Cache**: Manage models inside an `actor`, unload on memory pressure or background transitions, and share instances rather than reloading per request.

## Common Mistakes

- **Loading models on the main thread**: Blocks UI rendering. Always use `MLModel.load(contentsOf:configuration:)` asynchronously.
- **Recreating MLModel instances per prediction**: Model compilation and weight initialization are expensive. Cache and reuse model instances in an actor.
- **Recompiling models on every launch**: Always persist runtime `.compileModel(at:)` outputs to Application Support.
- **Concurrent inference with shared MLState**: An `MLState` instance is not thread-safe for concurrent calls. Serialize predictions or create separate states.
- **Preprocessing images manually**: Manual cropping and scaling causes color space and orientation bugs. Use Vision's `CoreMLRequest` instead.

## Review Checklist

- [ ] Model loaded asynchronously without stalling the main thread
- [ ] Runtime-compiled models persisted and reused across app launches
- [ ] Appropriate `computeUnits` chosen based on profiling and thermal constraints
- [ ] Single model instance shared via actor rather than re-instantiated
- [ ] Batch predictions (`predictions(fromBatch:)`) used for multi-sample throughput
- [ ] Vision framework (`CoreMLRequest`) utilized for image inputs
- [ ] `MLComputePlan` inspected on iOS 17.4+ to verify Neural Engine offload
- [ ] Memory warnings handled by releasing cached model instances

## References

- Actor-based caching, MLBatchProvider, and MLComputePlan recipes: [references/coreml-swift-integration.md](references/coreml-swift-integration.md)
- Model quantization and coremltools conversion: covered in `apple-on-device-ai`
- [Core ML Framework](https://sosumi.ai/documentation/coreml)
- [MLModel](https://sosumi.ai/documentation/coreml/mlmodel)
- [MLTensor](https://sosumi.ai/documentation/coreml/mltensor)
- [MLComputePlan](https://sosumi.ai/documentation/coreml/mlcomputeplan-1w21n)
- [Background Assets](https://sosumi.ai/documentation/backgroundassets)
