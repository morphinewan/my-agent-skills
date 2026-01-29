---
name: swiftui_best_practices
description: SwiftUI 与现代 Swift 开发通用最佳实践经验库，涵盖通知、并发及生命周期管理。持续迭代中。
---

# SwiftUI & Modern Swift 开发最佳实践

本文档用于沉淀在项目开发过程中积累的通用经验、设计模式及针对新 API 的适配方案。将会不断迭代更新。

---

## 目录

1.  [消息通知与通信 (Notifications)](#1-消息通知与通信-notifications)
2.  [并发与异步任务 (Concurrency)](#2-并发与异步任务-concurrency)
3.  [视图生命周期 (View Lifecycle)](#3-视图生命周期-view-lifecycle)
4.  [界面本地化 (Localization)](#4-界面本地化-localization)


---

## 1. 消息通知与通信 (Notifications)

### 场景描述
在 Swift 6 之前，`NotificationCenter` 缺乏类型安全且容易引发并发数据竞争。本方案借鉴了 Fatbobman 关于 `NotificationCenter.Message` 的设计理念 (Swift 6.2+)，通过轻量级封装实现强类型且并发安全的消息总线。

### 核心原则
*   **强类型**: 使用 Struct 替代字典 (`userInfo`)。
*   **无魔法字符串**: 集中管理 `Notification.Name`。
*   **并发安全**: 结合 Combine 显式调度线程，并强制消息体符合 `Sendable` 协议以便在异步环境安全传输。

### 实现方案

#### 1.1 基础协议
在 `Utils/NotificationMessage.swift` 定义：

```swift
import Combine
import Foundation

public protocol NotificationMessage: Sendable {
    static var name: Notification.Name { get }
}

public extension NotificationCenter {
    /// 发送强类型消息
    func post<T: NotificationMessage>(_ message: T, object: Any? = nil, userInfo: [AnyHashable: Any]? = nil) {
        var info = userInfo ?? [AnyHashable: Any]()
        info["dev.kun.kuncore.notification.message"] = message
        post(name: T.name, object: object, userInfo: info)
    }

    /// 观察强类型消息 (Combine)
    func publisher<T: NotificationMessage>(for type: T.Type, object: AnyObject? = nil) -> AnyPublisher<T, Never> {
        return publisher(for: T.name, object: object)
            .compactMap { $0.userInfo?["dev.kun.kuncore.notification.message"] as? T }
            .eraseToAnyPublisher()
    }
}
```

#### 1.2 使用范例

**定义消息**:
```swift
// 1. 在 Notification+Names.swift 集中定义 Name
extension Notification.Name {
    static let downloadProgress = Notification.Name("Module.downloadProgress")
}

// 2. 定义 Message 结构体 (必须显式或隐式符合 Sendable)
struct DownloadProgressMessage: NotificationMessage {
    static let name = Notification.Name.downloadProgress
    let taskId: String
    let progress: Double
}

// ⚠️ 避雷：不要在消息中包含非 Sendable 类型 (如 Error?)
// 推荐做法：将 Error 降级为 String 或自定义 Sendable 错误枚举
struct TaskErrorMessage: NotificationMessage {
    static let name = Notification.Name("TaskError")
    let errorMessage: String?
}
```

**发送**:
```swift
NotificationCenter.default.post(DownloadProgressMessage(taskId: "1", progress: 0.5))
```

**接收 (在 ViewModel 中)**:
```swift
NotificationCenter.default.publisher(for: DownloadProgressMessage.self)
    .receive(on: RunLoop.main) // 关键：确保 UI 线程安全
    .sink { msg in
        print("Progress: \(msg.progress)")
    }
    .store(in: &cancellables)
```

#### 1.3 主线程安全 (Main Thread Safety)

**原则**: `NotificationCenter` 的通知回调线程取决于发送者所在的线程。如果发送者是在后台线程或 Actor (如 `WhisperModelManager`) 中发送的，回调也会在后台执行。

**规则**: 当在 `.onReceive` 或 Combine 的 `sink` 中修改 SwiftUI 的状态（如 `@State`, `@Published`）时，**必须确保操作在主线程执行**。

**推荐方案**:

1.  **Combine 操作符 (推荐)**: 在 `publisher` 后紧跟 `.receive(on: RunLoop.main)`。
    ```swift
    .onReceive(
        NotificationCenter.default.publisher(for: Message.self)
            .receive(on: RunLoop.main) // 强制调度到主线程
    ) { message in
        self.someState = message.value
    }
    ```
2.  **异步闭包**: 在闭包内使用 `MainActor.run` 或 `Task { @MainActor in ... }`。
    ```swift
    .onReceive(NotificationCenter.default.publisher(for: Message.self)) { message in
        Task { @MainActor in
            self.someState = message.value
        }
    }
    ```

---

## 2. 并发与异步任务 (Concurrency)

### 2.1 结构化并发 (Structured Concurrency)

*   **避免散漫的 Task**: 尽量不要在 ViewModel `init` 中直接启动 `Task { ... }`，因为这会产生即使 View 销毁了仍在后台运行的“僵尸任务”。
*   **推荐做法**:
    *   在 SwiftUI 中使用 `.task` 修饰符（它会自动跟随 View 生命周期取消）。
    *   如果需要在 ViewModel 内部启动任务，必须持有 `Task` 句柄并在 `deinit` 或清理方法中调用 `.cancel()`。

---

## 3. 视图生命周期 (View Lifecycle)

### 3.1 `.onAppear` vs `.task`

| 修饰符 | 特性 | 推荐场景 |
| :--- | :--- | :--- |
| `.onAppear` | 同步执行，无自动取消机制 | 简单的状态重置、日志记录、UI 初始配置 |
| `.task` | 异步执行，View 消失自动取消，View 出现重新执行 | 数据加载、状态同步、订阅异步流 |

**最佳实践**: 涉及到异步操作（await）的初始化逻辑，一律优先使用 `.task`。

```swift
// ❌ 不推荐
.onAppear {
    Task {
        await viewModel.loadData()
    }
}

// ✅ 推荐
.task {
    await viewModel.loadData()
}
```

---

## 4. 界面本地化 (Localization)

### 核心原则
*   **优先英文 (Content in English)**: 所有的文本标签（Label）内容应优先使用英文书写。
*   **中文注释 (Chinese Comments)**: 使用 `comment` 参数提供中文解释，这有助于翻译人员理解语境，也方便中文开发者阅读代码。

### 推荐实践

#### 4.1 直接支持注解的控件 (如 Text)
对于 `Text` 等直接支持 `LocalizedStringKey` 和 `comment` 的组件，直接在构造函数中定义。

```swift
// ✅ 推荐做法
Text("English Label", comment: "中文的注释")
```

#### 4.2 不直接支持注解的场景 (动态文本或属性)
对于不支持直接传入 `comment` 的场景（如 `Button` 的 title 字符串，或者非 UI 的字符串常量），使用 `String(localized:comment:)`。

```swift
// ✅ 对于动态场景或不支持注解的控件
let label = String(localized: "English label", comment: "中文注释")
Button(label) {
    // action
}
```

### 为什么这样做？
1.  **代码即文档**: 中文注释让逻辑一目了然。
2.  **提取自动化**: 本地化工具（如 `xcstrings`）能自动提取这些内容并展示注释。
3.  **多语种友好**: 英文作为 Key 是国际化开发的通用准则，避免了跨平台或跨系统时的编码问题。

---

*(后续迭代请在此添加新章节)*

