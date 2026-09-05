---
name: apple-on-device-ai
description: "Designs private on-device AI for Apple platforms with Foundation Models, Core ML, MLX Swift, or llama.cpp. Use for local LLM runtime selection, Apple Intelligence chat or tool use, Apple Silicon inference, model conversion/compression, or backend comparison; route Core ML prediction code to coreml."
---

# On-Device AI for Apple Platforms

Architect and deploy private on-device machine learning and LLMs on Apple Silicon. Covers framework selection between Apple Foundation Models, Core ML, MLX Swift, and llama.cpp, plus model optimization and quantization.

> **Scope Boundary:** Swift-side Core ML inference and model caching live in `coreml`. This skill owns backend selection, architecture, model conversion, and LLM runtimes.

## Contents

- [Framework Selection Router](#framework-selection-router)
- [Apple Foundation Models](#apple-foundation-models)
- [Core ML & Model Conversion](#core-ml--model-conversion)
- [MLX Swift & Open Weights](#mlx-swift--open-weights)
- [Model Compression & Optimization](#model-compression--optimization)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Framework Selection Router

| Framework | Best For | Pros | Constraints |
|---|---|---|---|
| **Apple Foundation Models** (iOS 26+) | Text generation, structured output, tool calling | Zero app download footprint, native system UI integration | Requires Apple Intelligence eligible device |
| **Core ML** | Computer vision, audio, classification, custom transformer models | Best Neural Engine offload, lowest power consumption | Fixed compute graph; slower autoregressive text generation |
| **MLX Swift** | Custom open-weights LLMs/VLMs (Llama, Mistral, Gemma) | Full control over model architecture and generation parameters | Consumes user storage and unified RAM (high memory pressure) |
| **llama.cpp** | Cross-platform C++ runtime, CPU fallback | Broadest quantization support (GGUF), battle-tested | Higher power usage than Neural Engine pipelines |

## Apple Foundation Models

Leverage system-provided generative models on iOS 26+ without bundling model weights:

```swift
import FoundationModels

let session = LanguageModelSession()
let response = try await session.respond(to: "Summarize today's highlights in 3 bullet points.")
print(response.text)
```

Use `@Generable` to extract structured data directly from model prompts.

## Core ML & Model Conversion

Convert PyTorch and Hugging Face models using Python `coremltools`:

```python
import coremltools as ct
import torch

model = MyPyTorchModel().eval()
traced = torch.jit.trace(model, torch.randn(1, 3, 224, 224))

mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(name="input", shape=(1, 3, 224, 224))],
    compute_units=ct.ComputeUnit.ALL
)
mlmodel.save("Model.mlpackage")
```

## MLX Swift & Open Weights

Run open-source LLMs leveraging Apple Silicon unified memory:

```swift
import MLXLLM

let model = try await LLMModelFactory.shared.load(modelName: "mlx-community/Llama-3.2-3B-Instruct-4bit")
let output = try await model.generate(prompt: "Explain relativity in simple terms.")
```

## Model Compression & Optimization

- **Quantization**: Compress weights to 4-bit (int4) or 8-bit (int8) via `coremltools.optimize.coreml` to reduce memory bandwidth bottlenecks.
- **Palettization**: Cluster weights into lookup tables for smaller download sizes.
- **Pruning**: Zero out non-critical weights to accelerate inference.

## Common Mistakes

- **Bundling massive LLMs in app bundles**: Causes app review rejection or slow downloads. Use Background Assets or system Foundation Models.
- **Ignoring device memory limits**: Loading a 4-bit 7B LLM requires >4GB RAM, risking immediate OOM termination on devices with 6GB or 8GB unified memory.
- **Running autoregressive LLMs without KV-cache**: Re-evaluating the full token prompt at each step slows generation exponentially.
- **Neglecting thermal throttling**: Sustained GPU/CPU inference causes thermal throttling within minutes. Leverage the Neural Engine for sustained workloads.

## Review Checklist

- [ ] Appropriate framework selected for latency, power, and storage constraints
- [ ] System Foundation Models prioritized when Apple Intelligence features suffice
- [ ] Memory footprint measured on the lowest supported physical device target
- [ ] Models quantized to 4-bit or 8-bit to fit within memory budgets
- [ ] Neural Engine dispatch verified using `MLComputePlan` or Instruments

## References

- [Foundation Models API](references/foundation-models.md) -- LanguageModelSession, `@Generable`, tool calling, prompt design
- [Core ML Conversion](references/coreml-conversion.md) -- Model conversion from PyTorch, TensorFlow, other frameworks
- [Core ML Optimization](references/coreml-optimization.md) -- Quantization, palettization, pruning, performance tuning
- [MLX Swift & llama.cpp](references/mlx-swift.md) -- MLX Swift patterns, llama.cpp integration, memory management
