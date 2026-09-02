import MetricKit

@available(iOS 27.0, macOS 27.0, *)
@MainActor
final class ModernMetricConsumer {
    private let manager = MetricManager()
    private var metricTask: Task<Void, Never>?
    private var diagnosticTask: Task<Void, Never>?

    func start() {
        guard metricTask == nil, diagnosticTask == nil else { return }

        metricTask = Task {
            for await report in manager.metricReports {
                _ = report
            }
        }
        diagnosticTask = Task {
            for await report in manager.diagnosticReports {
                _ = report
            }
        }
    }

    func stop() {
        metricTask?.cancel()
        diagnosticTask?.cancel()
        metricTask = nil
        diagnosticTask = nil
    }
}
