import CoreHaptics

func makeCompileFixtureHapticPattern() throws -> CHHapticPattern {
    let event = CHHapticEvent(
        eventType: .hapticTransient,
        parameters: [
            .init(parameterID: .hapticIntensity, value: 0.8),
            .init(parameterID: .hapticSharpness, value: 0.6),
        ],
        relativeTime: 0
    )
    return try CHHapticPattern(events: [event], parameters: [])
}

func configureCompileFixtureHapticEngine() throws -> CHHapticEngine {
    let engine = try CHHapticEngine()
    engine.stoppedHandler = { _ in }
    engine.resetHandler = {}
    return engine
}

@MainActor
final class CompileFixtureHapticController {
    private var engine: CHHapticEngine?
    private var player: (any CHHapticPatternPlayer)?

    func prepare() throws {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }
        guard engine == nil else { return }

        let newEngine = try CHHapticEngine()
        newEngine.isAutoShutdownEnabled = true
        newEngine.stoppedHandler = { [weak self] _ in
            Task { @MainActor in
                self?.player = nil
            }
        }
        newEngine.resetHandler = { [weak self] in
            Task { @MainActor in
                guard let self, let engine = self.engine else { return }
                self.player = nil
                try? engine.start()
            }
        }
        engine = newEngine
        try newEngine.start()
    }

    func stop() {
        player = nil
        engine?.stop()
        engine = nil
    }

    func beginContinuousFeedback() throws {
        try prepare()
        guard let engine else { return }

        let event = CHHapticEvent(
            eventType: .hapticContinuous,
            parameters: [
                .init(parameterID: .hapticIntensity, value: 1),
                .init(parameterID: .hapticSharpness, value: 0.5),
            ],
            relativeTime: 0,
            duration: 30
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        player = try engine.makePlayer(with: pattern)
        try player?.start(atTime: CHHapticTimeImmediate)
    }

    func updateContinuousFeedback(intensity: Float, sharpness: Float) throws {
        let parameters = [
            CHHapticDynamicParameter(
                parameterID: .hapticIntensityControl,
                value: max(0, min(1, intensity)),
                relativeTime: 0
            ),
            CHHapticDynamicParameter(
                parameterID: .hapticSharpnessControl,
                value: max(-1, min(1, sharpness)),
                relativeTime: 0
            ),
        ]
        try player?.sendParameters(parameters, atTime: CHHapticTimeImmediate)
    }

    func endContinuousFeedback() throws {
        try player?.stop(atTime: CHHapticTimeImmediate)
        player = nil
    }
}
