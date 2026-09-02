struct CompileWorkItem: Sendable {
    let value: Int
}

actor CompileAccumulator {
    private var total = 0

    func add(_ value: Int) {
        total += value
    }

    func result() -> Int {
        total
    }
}

func concurrentSum(_ items: [CompileWorkItem]) async -> Int {
    await withTaskGroup(of: Int.self, returning: Int.self) { group in
        for item in items {
            group.addTask { item.value }
        }

        var total = 0
        for await value in group {
            total += value
        }
        return total
    }
}
