import SwiftData

@Model
final class CompileFixtureItem {
    var title: String

    init(title: String) {
        self.title = title
    }
}

@MainActor
func makeCompileFixtureContainer() throws -> ModelContainer {
    try ModelContainer(for: CompileFixtureItem.self)
}
