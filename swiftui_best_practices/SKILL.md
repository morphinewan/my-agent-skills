---
name: swiftui_best_practices
description: 当被要求进行 SwiftUI 开发时，使用此技能。要求所写代码需要符合此技能要求的SwiftUI 与现代 Swift 开发通用最佳实践经验库，涵盖通知、并发及生命周期管理。
---

# SwiftUI Development Rules

## Instruction
作为 SwiftUI 专家，你的目标是编写类型安全、高性能且易于维护的代码。在开发过程中，必须严格遵守以下约束条件（Constraints），并参考范例（Examples）进行实现。

## Constraints

### 1. 消息通知 (Notifications)
- **强制强类型**: 严禁使用 `[AnyHashable: Any]` 字典传递数据。必须定义符合 `NotificationMessage` 协议的 Struct。
- **并发安全**: 消息体必须符合 `Sendable` 协议，禁止包含非线程安全类型（如 `Error?`，应转换为 `String`）。
- **主线程调度**: 接收通知并更新 UI 状态时，**必须** 显式调度到主线程 (`receive(on: RunLoop.main)` 或 `@MainActor`)。

### 2. 并发与生命周期 (Concurrency & Lifecycle)
- **优先使用 `.task`**: 所有涉及 `await` 的异步初始化逻辑（如数据加载），**必须** 使用 `.task` 修饰符，而非 `.onAppear`。
- **拒绝僵尸任务**: 禁止在 ViewModel 的 `init` 中直接启动无管理的 `Task { }`。
- **结构化并发**: 确保所有后台任务都能随视图销毁自动取消。

### 3. 本地化 (Localization)
- **英文键值**: 所有 UI 显示的字符串 Key **必须** 使用英文。
- **中文注释**: **必须** 为每个本地化字符串提供中文 `comment`，用于解释上下文。
- **格式规范**: 使用 `Text("English", comment: "中文")` 或 `String(localized: "English", comment: "中文")`。

### 4. 编译性能 (Compilation Performance)
- **拆分视图**: 遇到复杂视图或编译器超时警告时，必须将 `body` 拆分为小的 `@ViewBuilder` 属性或独立的 `struct`。
- **显式类型**: 在复杂的闭包（如 SwiftData 的 `@Query` 或 `Predicate`）中，**必须** 显式声明参数类型和泛型，减轻编译器推断压力。
- **扁平化层级**: 容器（`VStack`/`HStack`）内子视图数量建议不超过 10 个，过多时使用 `Group` 分组。

---

## Examples

### 1. 强类型通知实现 (Strongly Typed Notifications)

**基础工具 (Infrastructure):**
```swift
// Utils/NotificationMessage.swift
import Combine
import Foundation

public protocol NotificationMessage: Sendable {
    static var name: Notification.Name { get }
}

public extension NotificationCenter {
    func post<T: NotificationMessage>(_ message: T, object: Any? = nil) {
        var info = [AnyHashable: Any]()
        info["dev.kun.kuncore.notification.message"] = message
        post(name: T.name, object: object, userInfo: info)
    }

    func publisher<T: NotificationMessage>(for type: T.Type, object: AnyObject? = nil) -> AnyPublisher<T, Never> {
        return publisher(for: T.name, object: object)
            .compactMap { $0.userInfo?["dev.kun.kuncore.notification.message"] as? T }
            .eraseToAnyPublisher()
    }
}
```

**正确用法 (Usage):**
```swift
// 1. 定义消息
struct DownloadProgressMessage: NotificationMessage {
    static let name = Notification.Name("Module.downloadProgress")
    let taskId: String
    let progress: Double
}

// 2. 接收消息 (ViewModel)
NotificationCenter.default.publisher(for: DownloadProgressMessage.self)
    .receive(on: RunLoop.main) // ✅ Constraint: Explicit Main Thread
    .sink { msg in
        self.progress = msg.progress
    }
    .store(in: &cancellables)
```

### 2. 生命周期与并发 (Lifecycle)

```swift
// ✅ Correct: 使用 .task 管理生命周期
struct UserProfileView: View {
    @StateObject private var vm = ProfileViewModel()
    
    var body: some View {
        List(vm.items) { item in
            // ...
        }
        .task { 
            // View 消失时自动取消，再次出现时重新执行
            await vm.loadData() 
        }
    }
}

// ❌ Incorrect: onAppear 无法自动取消异步任务
.onAppear {
    Task { await vm.loadData() } 
}
```

### 3. 本地化规范 (Localization)

```swift
// ✅ Correct
Text("Settings", comment: "设置页面标题")
Button(String(localized: "Delete", comment: "删除按钮")) { ... }

// ❌ Incorrect
Text("设置") // 错误：使用了中文 Key
Text("Settings") // 错误：缺少中文注释
```

### 4. 编译优化配置 (Compilation Optimization)

**Build Settings -> Other Swift Flags:**
(Add each flag on a new line)
```text
-Xfrontend
-warn-long-function-bodies=100
-Xfrontend
-warn-long-expression-type-checking=100
```