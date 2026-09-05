# NaturalLanguage Processing Patterns

Code recipes and implementation patterns for Apple's `NaturalLanguage` framework. Covers tokenization, language recognition, part-of-speech tagging, named entity recognition, text embeddings, and custom Core ML models.

## Contents

- [Tokenization](#tokenization)
- [Language Identification](#language-identification)
- [Part-of-Speech Tagging](#part-of-speech-tagging)
- [Named Entity Recognition](#named-entity-recognition)
- [Sentiment Analysis](#sentiment-analysis)
- [Text Embeddings](#text-embeddings)
- [Custom NLModel Classifiers](#custom-nlmodel-classifiers)

## Tokenization

Segment text into words, sentences, or paragraphs with `NLTokenizer`. Note that `NLTokenizer` is not thread-safe.

```swift
import NaturalLanguage

func tokenizeWords(in text: String) -> [String] {
    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = text
    let range = text.startIndex..<text.endIndex
    return tokenizer.tokens(for: range).map { String(text[$0]) }
}

func enumerateTokensWithAttributes(in text: String) {
    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = text

    tokenizer.enumerateTokens(in: text.startIndex..<text.endIndex) { range, attributes in
        if attributes.contains(.numeric) {
            print("Number: \(text[range])")
        }
        if attributes.contains(.emoji) {
            print("Emoji: \(text[range])")
        }
        return true
    }
}
```

## Language Identification

Detect dominant language and confidence hypotheses with `NLLanguageRecognizer`.

```swift
func detectLanguage(for text: String) -> NLLanguage? {
    NLLanguageRecognizer.dominantLanguage(for: text)
}

func languageHypotheses(for text: String, max: Int = 5) -> [NLLanguage: Double] {
    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    return recognizer.languageHypotheses(withMaximum: max)
}

func constrainedLanguageRecognition(for text: String) -> NLLanguage? {
    let recognizer = NLLanguageRecognizer()
    recognizer.languageConstraints = [.english, .french, .spanish]
    recognizer.processString(text)
    return recognizer.dominantLanguage
}
```

## Part-of-Speech Tagging

Identify lexical classes (nouns, verbs, adjectives) using `NLTagger`.

```swift
func tagPartsOfSpeech(in text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.lexicalClass])
    tagger.string = text

    var results: [(String, NLTag)] = []
    let range = text.startIndex..<text.endIndex
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace]

    tagger.enumerateTags(in: range, unit: .word, scheme: .lexicalClass, options: options) { tag, tokenRange in
        if let tag {
            results.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return results
}
```

## Named Entity Recognition

Extract people, places, and organizations with `.nameType`.

```swift
func extractEntities(from text: String) -> [(String, NLTag)] {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    var entities: [(String, NLTag)] = []
    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace, .joinNames]

    tagger.enumerateTags(
        in: text.startIndex..<text.endIndex,
        unit: .word,
        scheme: .nameType,
        options: options
    ) { tag, tokenRange in
        if let tag, tag != .other {
            entities.append((String(text[tokenRange]), tag))
        }
        return true
    }
    return entities
}
```

## Sentiment Analysis

Score text sentiment from -1.0 (negative) to +1.0 (positive).

```swift
func sentimentScore(for text: String) -> Double? {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    let (tag, _) = tagger.tag(
        at: text.startIndex,
        unit: .paragraph,
        scheme: .sentimentScore
    )
    return tag.flatMap { Double($0.rawValue) }
}
```

## Text Embeddings

Compute semantic distance and find neighbor words with `NLEmbedding`.

```swift
func wordSimilarity(_ word1: String, _ word2: String) -> Double? {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return nil }
    return embedding.distance(between: word1, and: word2, distanceType: .cosine)
}

func findSimilarWords(to word: String, count: Int = 5) -> [(String, Double)] {
    guard let embedding = NLEmbedding.wordEmbedding(for: .english) else { return [] }
    return embedding.neighbors(for: word, maximumCount: count, distanceType: .cosine)
}

func sentenceSimilarity(_ s1: String, _ s2: String) -> Double? {
    guard let embedding = NLEmbedding.sentenceEmbedding(for: .english) else { return nil }
    return embedding.distance(between: s1, and: s2, distanceType: .cosine)
}
```

## Custom NLModel Classifiers

Load Core ML trained text classifiers into `NLModel`.

```swift
import CoreML

func classifyText(_ text: String, modelName: String) throws -> String? {
    guard let modelURL = Bundle.main.url(forResource: modelName, withExtension: "mlmodelc") else {
        return nil
    }
    let compiledModel = try MLModel(contentsOf: modelURL)
    let customModel = try NLModel(mlModel: compiledModel)
    return customModel.predictedLabel(for: text)
}
```
