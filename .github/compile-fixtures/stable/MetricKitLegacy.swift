import Foundation
import MetricKit

final class LegacyMetricSubscriber: NSObject, MXMetricManagerSubscriber {
    func didReceive(_ payloads: [MXMetricPayload]) {
        _ = payloads.map(\.timeStampEnd)
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        _ = payloads.map(\.timeStampEnd)
    }
}

@available(iOS 13.0, *)
func registerLegacyMetricSubscriber(_ subscriber: LegacyMetricSubscriber) {
    MXMetricManager.shared.add(subscriber)
}
