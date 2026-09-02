import EnergyKit
import Foundation

@available(iOS 27.0, *)
func makeElectricalLoadDevice() -> ElectricalLoadDevice {
    ElectricalLoadDevice(
        id: "compile-fixture-vehicle",
        name: "Compile Fixture Vehicle",
        type: .electricVehicle
    )
}

@available(iOS 27.0, *)
func makeVehicleLoadEvent(
    measurement: ElectricVehicleLoadEvent.ElectricalMeasurement,
    session: ElectricVehicleLoadEvent.Session,
    device: ElectricalLoadDevice
) -> ElectricVehicleLoadEvent {
    ElectricVehicleLoadEvent(
        timestamp: .now,
        measurement: measurement,
        session: session,
        device: device
    )
}
