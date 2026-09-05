---
name: natural-language
description: "Tokenize, tag, and analyze natural language text using Apple's NaturalLanguage framework and translate between languages with the Translation framework. Use when adding language identification, sentiment analysis, named entity recognition, part-of-speech tagging, text embeddings, or in-app translation to iOS/macOS/visionOS apps."
---

# NaturalLanguage + Translation

Analyze natural language text for tokenization, part-of-speech tagging, named entity recognition, sentiment analysis, language identification, and embeddings using `NaturalLanguage`. Translate text with `Translation`. Targets Swift 6.3 / iOS 26+.

## Contents

- [Framework Scope and Boundaries](#framework-scope-and-boundaries)
- [Core Capabilities Matrix](#core-capabilities-matrix)
- [Thread Safety and Performance](#thread-safety-and-performance)
- [Translation Availability](#translation-availability)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Framework Scope and Boundaries

- **`NaturalLanguage`**: On-device text analysis (`NLTokenizer`, `NLTagger`, `NLLanguageRecognizer`, `NLEmbedding`, `NLModel`). Requires no special entitlements.
- **`Translation`**: In-app UI and programmatic language translation (`TranslationSession`, `LanguageAvailability`).
- **Boundaries**: Route OCR and image text recognition to `vision-framework`; route audio speech-to-text to `speech-recognition`; route generative LLM features to `apple-on-device-ai`; route static localization to `ios-localization`.

## Core Capabilities Matrix

| Capability | Primary Class | Key Output |
|---|---|---|
| Tokenization | `NLTokenizer` | Substrings segmented by word, sentence, or paragraph |
| Language ID | `NLLanguageRecognizer` | `NLLanguage` (e.g. `.english`, `.vietnamese`) with confidence |
| Part of Speech | `NLTagger` (`.lexicalClass`) | `NLTag` (.noun, .verb, .adjective, .pronoun) |
| Named Entities | `NLTagger` (`.nameType`) | Personal names, place names, organization names |
| Sentiment | `NLTagger` (`.sentimentScore`) | Continuous score between -1.0 and +1.0 |
| Semantic Distance | `NLEmbedding` | Cosine distance and neighbor queries for words/sentences |
| System Translation | `.translationPresentation()` | Native system modal translation sheet |
| Batch Translation | `TranslationSession` | Async batch translated strings |

## Thread Safety and Performance

> [!IMPORTANT]
> `NLTokenizer` and `NLTagger` are **not thread-safe**. Do not share instances across concurrent tasks or queues. Create instances on demand or isolate them within a serial actor. `NLEmbedding` instances are read-only and thread-safe once loaded into memory.

## Translation Availability

- `.translationPresentation(isPresented:text:)`: iOS 17.4+, macOS 14.4+, visionOS 1.1+
- `TranslationSession`, `.translationTask()`, and `LanguageAvailability`: iOS 18.0+, macOS 15.0+, visionOS 2.0+
- Offline programmatic translation via `TranslationSession(installedSource:target:)` requires the target language packs to be already installed on device.

## Route by Task

- For word/sentence tokenization, language recognition, and emoji/numeric detection, read [Tokenization and Language ID](references/nlp-patterns.md#tokenization).
- For POS tagging, entity extraction, sentiment analysis, and embeddings, read [Tagging and Embeddings](references/nlp-patterns.md#part-of-speech-tagging).
- For custom Core ML text classifiers and taggers with `NLModel`, read [Custom NLModel Classifiers](references/nlp-patterns.md#custom-nlmodel-classifiers).
- For SwiftUI translation sheets, batch translation, and language pack availability, read [Translation Patterns](references/translation-patterns.md).

## Common Mistakes

- Sharing an `NLTokenizer` or `NLTagger` across concurrent threads or Tasks without isolation.
- Passing empty strings to `NLEmbedding` or checking similarity without unwrapping optionals.
- Using `TranslationSession` offline when language packs are not installed on device.
- Performing synchronous NLP tagging or sentence embedding on the main thread during UI scrolling.
- Misinterpreting sentiment scores: scores range from -1.0 to 1.0 (0.0 is neutral, nil indicates untagged).

## Review Checklist

- [ ] `NLTokenizer` and `NLTagger` used from a single thread or isolated in an actor
- [ ] Availability guards applied for `TranslationSession` (iOS 18+) vs presentation sheet (iOS 17.4+)
- [ ] Language availability verified with `LanguageAvailability.status()` before programmatic translation
- [ ] Long text analysis dispatched off `@MainActor` to background tasks
- [ ] `NLEmbedding.wordEmbedding(for:)` checked for nil availability in the target language
- [ ] Tag options include `.omitWhitespace` and `.omitPunctuation` where appropriate

## References

- [NaturalLanguage text analysis patterns](references/nlp-patterns.md)
- [Translation framework patterns and SwiftUI views](references/translation-patterns.md)
- [NaturalLanguage documentation](https://sosumi.ai/documentation/naturallanguage)
- [Translation documentation](https://sosumi.ai/documentation/translation)
- [NLTokenizer](https://sosumi.ai/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://sosumi.ai/documentation/naturallanguage/nltagger)
- [NLEmbedding](https://sosumi.ai/documentation/naturallanguage/nlembedding)
