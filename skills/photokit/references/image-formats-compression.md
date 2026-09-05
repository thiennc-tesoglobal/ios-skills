# Image Formats and Compression

Use this reference when converting between HEIF/HEIC, JPEG, and PNG, controlling CGImageDestination properties, and compressing images before network upload.

## Contents

- [HEIF/HEIC Handling](#heifheic-handling)
- [Compression Before Upload](#compression-before-upload)

---

## HEIF/HEIC Handling

HEIF (High Efficiency Image Format) is the default camera format on modern iPhones. Handle detection, display, and conversion.

### Detection

```swift
import UniformTypeIdentifiers

func isHEIF(data: Data) -> Bool {
    guard data.count >= 12 else { return false }
    // Check for 'ftyp' box at byte 4
    let ftypRange = data[4..<8]
    return ftypRange.elementsEqual("ftyp".utf8)
}

func isHEIF(url: URL) -> Bool {
    guard let type = UTType(filenameExtension: url.pathExtension) else { return false }
    return type.conforms(to: .heif) || type.conforms(to: .heic)
}
```

### Conversion to JPEG

```swift
func convertHEICToJPEG(data: Data, compressionQuality: CGFloat = 0.9) -> Data? {
    guard let image = UIImage(data: data) else { return nil }
    return image.jpegData(compressionQuality: compressionQuality)
}
```

### Conversion to PNG

```swift
func convertHEICToPNG(data: Data) -> Data? {
    guard let image = UIImage(data: data) else { return nil }
    return image.pngData()
}
```

### Conversion with CGImageDestination (More Control)

```swift
import ImageIO

func convertHEICToJPEG(sourceData: Data,
                        quality: CGFloat = 0.9,
                        preserveMetadata: Bool = true) -> Data? {
    guard let source = CGImageSourceCreateWithData(sourceData as CFData, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }

    let mutableData = NSMutableData()
    guard let destination = CGImageDestinationCreateWithData(
        mutableData, UTType.jpeg.identifier as CFString, 1, nil
    ) else {
        return nil
    }

    var options: [CFString: Any] = [
        kCGImageDestinationLossyCompressionQuality: quality
    ]

    // Preserve EXIF, GPS, and other metadata
    if preserveMetadata,
       let metadata = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) {
        options[kCGImageDestinationMergeMetadata] = true
        CGImageDestinationAddImage(destination, cgImage, metadata)
    } else {
        CGImageDestinationAddImage(destination, cgImage, options as CFDictionary)
    }

    guard CGImageDestinationFinalize(destination) else { return nil }
    return mutableData as Data
}
```

---

## Compression Before Upload

Reduce file size before uploading to a server. Balance quality and size based on the use case.

### JPEG Compression with Target Size

```swift
func compressForUpload(image: UIImage,
                       maxBytes: Int = 1_000_000,
                       initialQuality: CGFloat = 0.9) -> Data? {
    var quality = initialQuality

    while quality > 0.1 {
        guard let data = image.jpegData(compressionQuality: quality) else { return nil }
        if data.count <= maxBytes {
            return data
        }
        quality -= 0.1
    }

    // Final attempt at minimum quality
    return image.jpegData(compressionQuality: 0.1)
}
```

### Resize and Compress

```swift
func resizeAndCompress(image: UIImage,
                       maxDimension: CGFloat = 1920,
                       compressionQuality: CGFloat = 0.8) -> Data? {
    let size = image.size
    let scale: CGFloat

    if max(size.width, size.height) > maxDimension {
        scale = maxDimension / max(size.width, size.height)
    } else {
        scale = 1.0
    }

    let newSize = CGSize(width: size.width * scale, height: size.height * scale)

    let renderer = UIGraphicsImageRenderer(size: newSize)
    let resized = renderer.image { _ in
        image.draw(in: CGRect(origin: .zero, size: newSize))
    }

    return resized.jpegData(compressionQuality: compressionQuality)
}
```

### HEIF Compression (Smaller Files)

```swift
func compressAsHEIF(image: UIImage, quality: CGFloat = 0.8) -> Data? {
    guard let cgImage = image.cgImage else { return nil }

    let mutableData = NSMutableData()
    guard let destination = CGImageDestinationCreateWithData(
        mutableData, UTType.heic.identifier as CFString, 1, nil
    ) else {
        return nil
    }

    let options: [CFString: Any] = [
        kCGImageDestinationLossyCompressionQuality: quality
    ]

    CGImageDestinationAddImage(destination, cgImage, options as CFDictionary)
    guard CGImageDestinationFinalize(destination) else { return nil }

    return mutableData as Data
}
```

---

