import EnergyKit
import Foundation

@available(iOS 26.0, *)
func firstShiftGuidance(for venueID: UUID) async throws -> ElectricityGuidance? {
    let query = ElectricityGuidance.Query(suggestedAction: .shift)
    let guidance = ElectricityGuidance.sharedService.guidance(using: query, at: venueID)

    for try await value in guidance {
        return value
    }
    return nil
}
