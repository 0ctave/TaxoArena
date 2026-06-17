# **Architectural Blueprint: Engineering High-Performance Terminal User Interfaces with Kotlin Mosaic and Spring Boot**

## **Executive Overview**

The convergence of command-line tools and modern generative artificial intelligence has catalyzed a profound resurgence in Terminal User Interfaces (TUIs). As artificial intelligence experiments increasingly rely on complex, real-time data streaming—encompassing inference logs, multi-agent state tracking, and dynamic code diff generation—standard sequential console output architectures are rendered obsolete. Modern AI tooling requires continuous, non-linear updates across multiple discrete screen regions, mimicking the behavior of graphical user interfaces within the constraints of a character-based terminal emulator. To address this paradigm shift, developers are increasingly leveraging declarative UI frameworks to construct advanced, state-driven terminal dashboards.

This comprehensive architectural report provides an exhaustive technical specification for integrating jakewharton/mosaic (version 0.18.0) within a Kotlin-based Spring Boot ecosystem managed by the Gradle build system. The ensuing analysis meticulously details the intricate mechanics of the Jetpack Compose compiler, the synchronization of the Spring Boot application lifecycle with blocking UI threads, and advanced terminal emulator rendering physics. Furthermore, it prescribes explicit, low-level configurations for environments such as Windows PowerShell and the IntelliJ IDEA embedded terminal. These configurations are absolutely critical to guarantee full-screen, highly responsive, and strictly flicker-free rendering for sophisticated AI experimental dashboards.

## **Ecosystem Foundations: Jetpack Compose and the Mosaic Runtime**

The Mosaic library operates fundamentally differently from legacy terminal libraries such as ncurses or Lanterna. It is not a traditional UI toolkit containing standalone rendering loops and imperative widget hierarchies. Instead, Mosaic functions as a custom Applier and rendering backend for the Jetpack Compose runtime.1 It translates Compose's intermediate representation (IR) into terminal-compatible text nodes, projecting reactive state changes into highly optimized ANSI escape sequences.1

### **The Compose Compiler Mechanics**

Understanding the Jetpack Compose compiler is critical for developing advanced AI TUIs. When a developer annotates a Kotlin function with @Composable, or specifically with the @MosaicComposable annotation, the Kotlin compiler intercepts the abstract syntax tree during the build phase.3 The @MosaicComposable annotation serves to restrict composable function usage strictly to those intended for Mosaic (such as the Text node) or general-purpose Compose functions (such as remember), preventing the accidental inclusion of Android-specific UI nodes.3

The compiler rewrites the function signature to accept an implicit Composer object. This Composer tracks the exact location of the function call within the execution tree, enabling a concept known as positional memoization. Mosaic defines its own internal node hierarchy, specifically utilizing the MosaicNode class, which holds geometric information regarding the node's calculated width and height during the measurement phase.1 Through its custom Applier implementation, Mosaic teaches the Compose runtime how to materialize these nodes and manage their lifecycle.1

When building an AI dashboard, inference metrics, token streams, and agent states are held in Compose snapshot state variables, such as mutableStateOf.1 When an AI model yields a new token over a network socket, the snapshot state mutates. The Compose runtime invalidates only the specific Mosaic nodes reading that exact state variable. It then executes a highly efficient differential update, computing the minimum number of terminal cell mutations required, rather than forcing a full terminal redraw.1

### **Gradle Build Architecture and Version Alignment**

Historically, integrating Mosaic required the application of a bespoke custom Gradle plugin that manually aligned the Compose compiler version with the specific Kotlin version in use.6 However, starting with Mosaic version 0.13.0, and continuing into the current 0.18.0 stable release, the architectural paradigm has shifted significantly.3 Mosaic now delegates compilation directly to the official JetBrains Compose compiler plugin.3

This transition ensures immediate, native compatibility with modern Kotlin releases (specifically Kotlin 2.0.0 and above) and removes the overhead of orchestrating custom compiler plugins.6 To architect the build system for a Mosaic-powered TUI, the build.gradle.kts configuration must explicitly apply the Kotlin JVM plugin, the JetBrains Compose compiler plugin, and the Mosaic runtime dependency.

| Component | Gradle Configuration Directive | Version Target |
| :---- | :---- | :---- |
| **Kotlin JVM Plugin** | kotlin("jvm") | 2.0.0+ 4 |
| **Compose Compiler** | org.jetbrains.kotlin.plugin.compose | Aligned with Kotlin Compiler 3 |
| **Mosaic Runtime** | implementation("com.jakewharton.mosaic:mosaic-runtime:0.18.0") | 0.18.0 Stable 4 |

If developers wish to utilize the bleeding-edge features of the framework, they must append the Central Portal Snapshots repository to their dependency resolution strategy and target the 0.19.0-SNAPSHOT artifact.3

### **Native Library Integration via FFM API**

An advanced feature introduced in Mosaic 0.18.0 is the modernization of its native operating system interactions. For applications executing on Java 22 or newer, Mosaic leverages the Java Foreign Function & Memory (FFM) API instead of traditional Java Native Interface (JNI) bindings to call into its underlying native libraries.3

The FFM API provides a safer, strictly typed, and highly performant mechanism for invoking C-level terminal control functions (such as ioctl on POSIX systems or the Windows Console API). While Java 11 remains the absolute minimum supported JVM version for the library, deploying the Spring Boot application on JDK 22 or higher unlocks optimized, low-overhead native terminal interactions, which is highly recommended for data-intensive AI dashboards.3 Furthermore, JVM artifacts in the 0.18.0 release can now be utilized properly as modules within the Java Module System (JPMS).3

## **Orchestrating the Spring Boot Application Lifecycle**

Integrating a highly interactive, state-driven UI framework like Mosaic into a Spring Boot application demands a precise understanding of the Spring ApplicationContext lifecycle and JVM thread management. Spring Boot is inherently designed to bootstrap asynchronous enterprise web services, expose REST controllers, or execute background batch jobs. Repurposing it as a host for a persistent, blocking Terminal UI requires deliberate thread synchronization to prevent the application from terminating prematurely or blocking background networking tasks.

### **The CommandLineRunner Execution Context**

The standard entry point for console-based Spring Boot applications is the CommandLineRunner or ApplicationRunner interface.9 These functional interfaces define a single run method that Spring Boot invokes automatically after the dependency injection container is fully initialized and all singletons are materialized.9

The defining characteristic of CommandLineRunner is that it executes strictly on the main thread of the application.9 When multiple runners are present within the context, they are executed sequentially, dictated by their respective @Order annotations.12 Because Mosaic's primary execution function is a blocking or suspending operation that holds the thread open to continuously listen for standard input and render layout frames, the runner containing the Mosaic loop must be the absolute final execution block in the Spring Boot startup sequence.1

| Runner Interface | Execution Signature | Target Use Case in Spring Boot |
| :---- | :---- | :---- |
| **CommandLineRunner** | void run(String... args) | Raw string array arguments; ideal for simple CLI flags.9 |
| **ApplicationRunner** | void run(ApplicationArguments args) | Parsed arguments with options/values; ideal for complex TUI configurations.9 |
| **Mosaic Execution** | runMosaicMain {... } | Replaces legacy runMosaicBlocking for use in main-like scenarios.15 |

### **Injecting State and Resolving Dependencies**

The primary architectural advantage of utilizing Spring Boot to drive a Mosaic TUI is the ability to leverage Spring's vast enterprise ecosystem for the underlying AI logic. An advanced AI experiment dashboard requires complex dependency-injected services to manage Large Language Model (LLM) API communication, vector database connections, context compaction, and localized data processing.9

By defining the Mosaic execution block within a Spring @Component that implements CommandLineRunner, the @Composable UI tree can directly consume Kotlin Flow streams from injected @Service beans.9 A sophisticated implementation strategy involves extracting all AI inference logic into asynchronous, non-blocking Spring services that emit StateFlow or SharedFlow updates representing model generation progress.

The Mosaic UI layer then observes these flows using Compose's collectAsState() extensions. This strictly decouples the AI network latency and token streaming mechanics from the terminal rendering loop, adhering to unidirectional data flow architectures and ensuring that the UI remains highly responsive even when the LLM API experiences severe latency.18

### **Concurrency, Blocking, and Application Termination**

Because the runMosaicMain function monopolizes the thread on which it is invoked, the Spring Boot application remains alive as long as the Compose tree is active.1 Mosaic programs must establish a clear interactive policy. The runMosaic and runMosaicMain functions accept a NonInteractivePolicy argument, which dictates the strict behavior of the framework when it detects that it cannot connect directly to a True Terminal (TTY) environment, ensuring graceful degradation during automated testing or CI/CD pipelines.3

When the user initiates a termination command within the TUI (typically by pressing Ctrl+C or a dynamically mapped exit key), the underlying Coroutine scope managing the UI canvas cancels. This cancellation releases the block on the CommandLineRunner.12 Once the run method completes, Spring Boot regains control of the main thread and gracefully initiates the teardown sequence of the ApplicationContext, publishing destruction events, terminating singletons, and closing active database connection pools.9

## **Advanced Terminal Environment Calibration**

The single most critical failure point in developing TUIs is the environment in which the compiled application executes. A terminal emulator must natively support ANSI escape codes, TrueColor (24-bit RGB) visual profiles, and strict UTF-8 text encoding.19 Standardizing these variables across Windows PowerShell and the IntelliJ IDEA embedded terminal requires rigorous environment enforcement.

### **Overcoming IntelliJ IDEA Embedded Terminal Constraints**

It is a remarkably common anti-pattern to attempt to run rich, interactive Mosaic applications directly via the ./gradlew run command or within the IntelliJ IDEA embedded "Run" execution tool window. Mosaic documentation explicitly warns that running within Gradle or IntelliJ IDEA execution windows will universally result in broken output.4

These IDE execution tools pipe processes via standard output streams that entirely lack TTY capabilities. Without an active TTY, the application cannot receive keyboard interrupts or terminal resize signals, nor can it execute the OS-level ioctl commands required to query or navigate cursor positions.4 Furthermore, IDE consoles routinely strip ANSI control characters for security and formatting reasons. When this occurs, Mosaic gracefully falls back to rendering output as successive, appended strings, resulting in a continuous vertical scroll of text rather than a static, redrawing user interface.4

If the AI dashboard must be visualized during active development within IntelliJ, developers must circumvent the standard "Run" window entirely and instead utilize the IntelliJ Embedded Terminal tool window. Even within the embedded terminal, the following configurations are mandatory to ensure accurate rendering:

| IntelliJ Configuration Category | Required Setting Parameter | Architectural Justification |
| :---- | :---- | :---- |
| **Global File Encoding** | UTF-8 | Configured in Settings \> Editor \> File Encodings. Prevents IntelliJ from interpreting bytes via legacy Windows code pages, which corrupts box-drawing glyphs into question marks.22 |
| **JVM Execution Options** | \-Dconsole.encoding=UTF-8 \-Dfile.encoding=UTF-8 | Appended via Help \> Edit Custom VM options. Forces the Java runtime to emit standard output in UTF-8, overriding the OS locale default.24 |
| **Terminal Shell Path** | pwsh.exe (PowerShell Core) | Configured in Settings \> Tools \> Terminal. Avoids the legacy cmd.exe host, ensuring superior Unicode and ANSI parsing support.26 |
| **Contrast Ratio** | Disable Enforce minimum contrast ratio | IntelliJ automatically overrides TUI foreground colors if the contrast drops below 4.5. Disabling this preserves the AI dashboard's exact hex color intent.26 |

Furthermore, IntelliJ IDEA employs two distinct terminal engines: the "Classic" engine and the "Reworked 2025" engine.26 The Reworked 2025 engine intercepts certain keystrokes for its internal command completion features, which can interfere with Mosaic's Modifier.onKeyEvent() listeners. Developers building interactive TUIs may need to ensure keystroke passthrough or revert to the Classic terminal engine during testing.26

### **Windows PowerShell and Virtual Terminal Processing**

By default, legacy Windows console hosts (conhost.exe) execute in a mode that does not process ANSI escape sequences for external compiled executables. Without explicit intervention, an advanced TUI will output garbled literal text to the console (e.g., ←\[32mgreen←\[m) instead of formatted UI blocks.27 To execute a Mosaic dashboard natively in PowerShell, the host must enable Virtual Terminal Processing.

The Windows operating system handles this via the SetConsoleMode C++ API, specifically enabling the ENABLE\_VIRTUAL\_TERMINAL\_PROCESSING (0x0004) flag on the screen buffer handle.27 While modern terminal emulators like the standalone Windows Terminal application enable this flag unconditionally, running the compiled Java application directly in a standard PowerShell host requires a systemic registry override.27

Developers must configure the Windows Registry to explicitly opt-in to global ANSI parsing by injecting a DWORD value: \`\` \-\> "VirtualTerminalLevel"=dword:00000001.27 This registry modification ensures that all terminal-oblivious executables inherit an active ANSI parsing state.27

Additionally, PowerShell must enforce strict UTF-8 character mapping. Relying on default Windows locale settings will malform the UI border lines and complex typographies generated by Mosaic. This is resolved by issuing the following command in the $PROFILE script prior to application launch: \[Console\]::OutputEncoding \=::UTF8.30

To support advanced visual feedback, including emojis or status indicators for AI agent tasks, developers must configure the terminal profile to utilize a font face with comprehensive Unicode and fallback coverage, such as Cascadia Code or Segoe UI Emoji.30

## **Visual Geometry: Architecting Responsive Full-Screen Layouts**

An advanced AI experiment dashboard typically requires a highly segmented and organized layout: a main log view for real-time generative model outputs, a side panel for multi-agent health and memory status, and a fixed input bar at the bottom for human-in-the-loop interventions. Orchestrating this visual layout requires a highly responsive geometry engine capable of adapting to arbitrary window resizes in real-time.

### **Harnessing TerminalState and the Real-Time Event Parser**

Mosaic 0.18.0 features a completely overhauled, custom-built terminal parsing library designed to capture instant resize events, terminal focus changes, and system theme shifts.3 The legacy Terminal and LocalTerminal primitives from earlier versions have been refactored into TerminalState and LocalTerminalState, respectively.3

Through the LocalTerminalState composition local, the Compose tree can dynamically query the real-time bounds and attributes of the application window.

| TerminalState Property | Functionality and Emitted Data |
| :---- | :---- |
| **focused** | A reactive boolean (defaulting to true) that updates if the terminal supports sending real-time window focus changes.3 Mosaic automatically binds this to a LifecycleOwner, enabling Android-style LifecycleResumeEffect triggers.15 |
| **theme** | Reports the terminal's color scheme as 'light', 'dark', or 'unknown'. This queries the terminal emulator's explicit color scheme, not the overarching operating system theme.3 |
| **size** | An object containing the current dimensions of the terminal window, measured in both character **cells** (columns/rows) and raw **pixels** (if supported by the host emulator).3 |

Crucially, in version 0.18.0, Mosaic tightened its strict contract with the terminal environment regarding asynchronous events. Unsolicited focus, theme, and resize signals are now explicitly ignored by the Mosaic engine unless the terminal emulator has formally reported support for these specific modes via standard device attribute handshake protocols.3 This architectural change ensures that the Terminal.capabilities value can be strictly trusted to indicate whether Terminal.state will ever actually change during execution.3

However, to maintain responsive layouts across highly varied environments (such as remote SSH sessions or legacy PowerShell), Mosaic implements a robust, platform-specific fallback. This fallback asynchronously attempts to poll and report the terminal size correctly even when explicit resize signals (such as SIGWINCH on POSIX environments or WINDOW\_BUFFER\_SIZE\_RECORD on Windows) are not successfully broadcast by the host.3

### **Composable Layout Primitives and Dynamic Breakpoints**

Responsive design in a terminal UI closely mirrors the declarative paradigms used in Android and responsive Web development. The developer avoids defining hardcoded widths, relying instead on relative, structural constraints that respond to the TerminalState.

The fundamental layout building blocks provided by Mosaic are Row, Column, Box, and Spacer.3 These primitives accept robust Modifier chains. To enforce a full-screen application layout, the absolute root container of the TUI is typically assigned Modifier.fillMaxSize(). This modifier reads the maximum dimensional constraints provided by the underlying terminal canvas and forces the Compose layout engine to occupy all available character cells, preventing the UI from collapsing to the intrinsic size of its children.3

Furthermore, horizontal and vertical spacing can be dynamically allocated using Modifier.weight(). This modifier allows the developer to size a composable proportionally to other siblings within the same parent container.3 For example, the developer can allocate a weight of 0.7f to the primary AI response window, and 0.3f to the agent status sidebar, ensuring the ratio persists regardless of the terminal's absolute width.

To achieve genuine responsiveness, the dashboard architecture must calculate conditional rendering paths based on the real-time TerminalState. Similar to the calculateWindowSizeClass utility utilized in Android Jetpack Compose, the terminal dashboard can read the TerminalState.size.columns integer.33

If the terminal width drops below a predefined logical breakpoint (e.g., 80 columns), the layout hierarchy can dynamically reconfigure from a split-pane horizontal Row design to a stacked vertical Column layout.33 Because the Jetpack Compose engine inherently relies on state observation, the exact moment the user resizes the terminal window, the size property mutates, the condition is rapidly re-evaluated, and the tree automatically recomposes into the new geometric bounds.1

## **Advanced Terminal Artifacts: Operating the Alternate Screen Buffer**

A persistent, deeply technical challenge with building advanced, full-screen TUIs—such as a complex dashboard for monitoring LLM agents—is properly managing the terminal scrollback history. By default, console applications write their output to the primary screen buffer. If an application utilizes this buffer to constantly clear and redraw a full-screen layout, it rapidly pollutes the user's terminal scrollback, completely obliterating their command history and previous workflows.35

To circumvent this destructive behavior, sophisticated full-screen CLI applications (such as vim, htop, or nano) execute their interfaces entirely within the terminal's **Alternate Screen Buffer**.36 The alternate buffer is a secondary, independent character cell matrix provided by the terminal emulator specifically designed for transient, full-screen graphical applications.

### **Mechanics of Alternate Buffer Management**

Transitioning an application to the alternate buffer is achieved by emitting the precise ANSI CSI (Control Sequence Introducer) command \\x1b When the application terminates, it emits the inverse sequence \\x1b\[?1049l\` to clear the alternate buffer and restore the primary screen exactly as the user left it before executing the application.40

While discussions and feature requests within the Mosaic repository indicate long-term plans for native alternate screen encapsulation (where Mosaic would constrain both width and height natively to the alternate buffer) 41, an advanced AI agent dashboard must ensure absolute compliance. If the framework does not strictly wrap the execution in these specific ANSI sequences natively for a particular platform, the Kotlin application should intercept the Spring Boot initialization and teardown hooks to emit them manually via \`System.out.print("\\u001B

### **Implications for Scrolling and Overflow**

Operating within the alternate screen buffer fundamentally alters how the application must handle data overflow. Historically and architecturally, the alternate buffer strictly lacks native scrollback capability.36

Therefore, if the AI output logs exceed the vertical height of the TerminalState.size.rows, the developer cannot rely on the mouse wheel or the terminal emulator's native scrollbar. The developer must explicitly implement logical scrolling within the Compose tree itself. This is achieved by maintaining a sliding window index over a large list of string outputs in the application state, mapping keystrokes (via Modifier.onKeyEvent()) or mouse wheel events to manipulate the index, and subsequently shifting the rendered slice of text up or down the screen programmatically.3

## **Rendering Physics: Eradicating Screen Flickering**

Perhaps the most universally encountered and visually jarring defect in TUI engineering is the phenomenon of screen flickering, commonly described in technical issue trackers as a "stroboscopic effect" or "tearing".42 In the context of a highly active AI dashboard—where text strings are generating at 50 to 100 tokens per second across multiple concurrent agent panels—flickering renders an application visually fatiguing and essentially unusable.42

### **The Architecture of the Stroboscopic Effect**

Flickering is a direct byproduct of the inherent physics of standard terminal emulation. To update a UI layout, a basic framework generally moves the cursor to the top-left coordinate (Home), issues an ANSI clear-screen command (\\x1b\[2J), and rapidly writes the entire newly computed text buffer to the standard output stream.46

However, the terminal emulator processes and paints incoming bytes asynchronously to the GPU or display server. If the emulator happens to trigger a display frame render exactly after the screen has been cleared, but just before the new text payload has fully arrived over the output stream, the user perceives a completely black screen for a fraction of a millisecond.42 When this desynchronization occurs across dozens of frames per second during heavy LLM token streaming, the UI flashes violently.46

### **Synchronized Output (DECSET 2026\)**

To completely eliminate this visual artifact, the industry and modern terminal emulators have increasingly adopted the **Synchronized Output** specification, formally initiated via DECSET 2026\.43

When a compliant application emits the start marker \\e\[?2026h, it explicitly signals to the terminal emulator to halt all rendering and suspend all UI flushes to the display.43 The application then rapidly transmits all necessary cursor movements, line clears, color shifts, and string updates representing the new visual frame.43 Only after the strict end marker \\e\[?2026l is received does the emulator process the entire batch of operations atomically, repainting the terminal window in a single, perfectly unified frame.43

Mosaic v0.18.0 incorporates advanced terminal capabilities tracking to address this. The framework's custom terminal integration library automatically detects if the host terminal supports synchronized output. If supported (such as in Ghostty, modern iTerm2, or properly configured tmux environments), Mosaic will automatically emit these synchronized rendering markers around its internal frame updates, establishing a true zero-flicker, double-buffered rendering logic without requiring manual developer intervention.15 Additionally, Mosaic automatically disables the cursor visibility (\\e\[?25l) during the active write cycle, further mitigating visual artifacts that occur when a cursor dances erratically across the screen during a complex update.15

### **Fallback Mechanics: Differential Rendering**

If the target terminal environment (e.g., an outdated version of tmux lacking the xterm\*:sync configuration, or a legacy PowerShell host) does not explicitly support DECSET 2026, Mosaic relies on its built-in differential renderer.43

Instead of clearing the screen, the framework mathematically computes the exact character diffs between the previously drawn frame and the newly requested state. It then generates an optimized payload of ANSI sequences, repositioning the cursor to overwrite only the specific mutated cells.46 While significantly reducing total byte bandwidth and tearing compared to full-screen redraws, differential rendering still carries a slight risk of micro-tearing on extremely slow network connections or heavily taxed local CPUs, cementing true synchronized output as the absolute gold standard for professional TUIs.46

### **Integrating Out-of-Band Logging**

A final consideration for preventing layout corruption and flicker in an AI dashboard is handling unexpected, out-of-band debug logging. If a background Spring Boot process attempts to use System.out.println while the Mosaic TUI is active, it will instantly corrupt the terminal canvas.

To address this, Mosaic provides the LocalStaticLogger composition local. This utility grants access to a StaticLogger object, which allows the developer to queue plain strings at arbitrary points in the codebase.3 Mosaic safely intercepts these strings and injects them statically directly above the rendered UI during the next synchronized frame calculation, ensuring that debug logs do not interfere with the active Compose grid.3

## **Conclusion**

The evolution of terminal-based AI tooling necessitates system architectures that far transcend simple procedural string outputs. By synthesizing the reactive capabilities of the Kotlin Jetpack Compose compiler through the highly optimized jakewharton/mosaic runtime, and coupling it with the robust dependency injection and lifecycle orchestration of Spring Boot, developers can construct unparalleled full-screen user interfaces.

Achieving a flawless, zero-flicker experience mandates stringent control over the entire terminal ecosystem. Relying on integrated IDE consoles critically undermines the complex ANSI protocols required for differential updates and TTY focus tracking. Instead, executing within a fully configured, dedicated shell environment—armed with explicit UTF-8 encoding boundaries, Virtual Terminal Processing logic, alternate screen buffer controls, and DECSET 2026 synchronized rendering markers—guarantees that advanced AI experimentation dashboards behave with the fluidity, responsiveness, and structural integrity of native graphical applications.

#### **Sources des citations**

1. Diving into Mosaic for Jetpack Compose, consulté le mai 14, 2026, [https://jorgecastillo.dev/diving-into-mosaic](https://jorgecastillo.dev/diving-into-mosaic)  
2. Mosaic – Jetpack Compose for terminal UI by Jake Wharton : r/Kotlin \- Reddit, consulté le mai 14, 2026, [https://www.reddit.com/r/Kotlin/comments/n54ha8/mosaic\_jetpack\_compose\_for\_terminal\_ui\_by\_jake/](https://www.reddit.com/r/Kotlin/comments/n54ha8/mosaic_jetpack_compose_for_terminal_ui_by_jake/)  
3. Releases · JakeWharton/mosaic \- GitHub, consulté le mai 14, 2026, [https://github.com/JakeWharton/mosaic/releases](https://github.com/JakeWharton/mosaic/releases)  
4. JakeWharton/mosaic: Build terminal UI in Kotlin using Jetpack Compose \- GitHub, consulté le mai 14, 2026, [https://github.com/jakewharton/mosaic](https://github.com/jakewharton/mosaic)  
5. \[ANN\] Mosaic \- A Modern Terminal User Interface Framework for OCaml (Early Preview), consulté le mai 14, 2026, [https://discuss.ocaml.org/t/ann-mosaic-a-modern-terminal-user-interface-framework-for-ocaml-early-preview/17572](https://discuss.ocaml.org/t/ann-mosaic-a-modern-terminal-user-interface-framework-for-ocaml-early-preview/17572)  
6. 0.13.0 · JakeWharton mosaic · Discussion \#381 \- GitHub, consulté le mai 14, 2026, [https://github.com/JakeWharton/mosaic/discussions/381](https://github.com/JakeWharton/mosaic/discussions/381)  
7. "Mosaic 0.12.0 and 0.13.0 have …" \- Mastodon \- Jake Wharton (@jw@jakewharton.com), consulté le mai 14, 2026, [https://mastodon.jakewharton.com/@jw/112521975860557005](https://mastodon.jakewharton.com/@jw/112521975860557005)  
8. Compatibility and versions | Kotlin Multiplatform Documentation, consulté le mai 14, 2026, [https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html)  
9. The Mechanics of Spring Boot's CommandLineRunner \- Medium, consulté le mai 14, 2026, [https://medium.com/@AlexanderObregon/the-mechanics-of-spring-boots-commandlinerunner-d000be905133](https://medium.com/@AlexanderObregon/the-mechanics-of-spring-boots-commandlinerunner-d000be905133)  
10. Creating a Spring Boot Console Application With Kotlin \- Baeldung, consulté le mai 14, 2026, [https://www.baeldung.com/kotlin/spring-boot-console-application](https://www.baeldung.com/kotlin/spring-boot-console-application)  
11. Spring Boot CommandLineRunner Example \- Mkyong.com, consulté le mai 14, 2026, [https://mkyong.com/spring-boot/spring-boot-commandlinerunner-example/](https://mkyong.com/spring-boot/spring-boot-commandlinerunner-example/)  
12. Is it thread-safe to run multiple CommandLineRunner at same time via Spring Boot?, consulté le mai 14, 2026, [https://stackoverflow.com/questions/66740067/is-it-thread-safe-to-run-multiple-commandlinerunner-at-same-time-via-spring-boot](https://stackoverflow.com/questions/66740067/is-it-thread-safe-to-run-multiple-commandlinerunner-at-same-time-via-spring-boot)  
13. Spring Boot Lifecycle — Deep Dive | by Anil Goyal \- Medium, consulté le mai 14, 2026, [https://medium.com/@anil.goyal0057/spring-boot-lifecycle-deep-dive-c87e203c8717](https://medium.com/@anil.goyal0057/spring-boot-lifecycle-deep-dive-c87e203c8717)  
14. How to Use CommandLineRunner in Spring Boot (Practical Examples) | by Nisha Kumari, consulté le mai 14, 2026, [https://medium.com/@nishamishra1017/how-to-use-commandlinerunner-in-spring-boot-practical-examples-15128bdc564c](https://medium.com/@nishamishra1017/how-to-use-commandlinerunner-in-spring-boot-practical-examples-15128bdc564c)  
15. 0.17.0 · JakeWharton mosaic · Discussion \#857 \- GitHub, consulté le mai 14, 2026, [https://github.com/JakeWharton/mosaic/discussions/857](https://github.com/JakeWharton/mosaic/discussions/857)  
16. Understanding the Spring Boot Lifecycle \- DEV Community, consulté le mai 14, 2026, [https://dev.to/devcorner/understanding-the-spring-boot-lifecycle-4kbn](https://dev.to/devcorner/understanding-the-spring-boot-lifecycle-4kbn)  
17. Spring Boot CommandLineRunner Example: 3 Ways to Use \- HowToDoInJava, consulté le mai 14, 2026, [https://howtodoinjava.com/spring-boot/command-line-runner-interface-example/](https://howtodoinjava.com/spring-boot/command-line-runner-interface-example/)  
18. How to Prevent Flickering Effect when Switching Screens based on DataStore Value in Jetpack Compose? \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/78287440/how-to-prevent-flickering-effect-when-switching-screens-based-on-datastore-value](https://stackoverflow.com/questions/78287440/how-to-prevent-flickering-effect-when-switching-screens-based-on-datastore-value)  
19. How to color System.out.println output? \- java \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/1448858/how-to-color-system-out-println-output](https://stackoverflow.com/questions/1448858/how-to-color-system-out-println-output)  
20. is it possible to color java output in terminal using rgb or hex colors? \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/59373280/is-it-possible-to-color-java-output-in-terminal-using-rgb-or-hex-colors](https://stackoverflow.com/questions/59373280/is-it-possible-to-color-java-output-in-terminal-using-rgb-or-hex-colors)  
21. I Just Wanted Emacs to Look Nice — Using 24-Bit Color in Terminals | Chad Austin, consulté le mai 14, 2026, [https://chadaustin.me/2024/01/truecolor-terminal-emacs/](https://chadaustin.me/2024/01/truecolor-terminal-emacs/)  
22. File Encodings | IntelliJ IDEA Documentation \- JetBrains, consulté le mai 14, 2026, [https://www.jetbrains.com/help/idea/settings-file-encodings.html](https://www.jetbrains.com/help/idea/settings-file-encodings.html)  
23. Encoding | IntelliJ IDEA Documentation \- JetBrains, consulté le mai 14, 2026, [https://www.jetbrains.com/help/idea/encoding.html](https://www.jetbrains.com/help/idea/encoding.html)  
24. IntelliJ IDEA incorrect encoding in console output \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/35231291/intellij-idea-incorrect-encoding-in-console-output](https://stackoverflow.com/questions/35231291/intellij-idea-incorrect-encoding-in-console-output)  
25. Unicode characters appear as question marks in IntelliJ IDEA console \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/1082343/unicode-characters-appear-as-question-marks-in-intellij-idea-console](https://stackoverflow.com/questions/1082343/unicode-characters-appear-as-question-marks-in-intellij-idea-console)  
26. Terminal settings | IntelliJ IDEA Documentation \- JetBrains, consulté le mai 14, 2026, [https://www.jetbrains.com/help/idea/settings-tools-terminal.html](https://www.jetbrains.com/help/idea/settings-tools-terminal.html)  
27. Windows console with ANSI colors handling \- Super User, consulté le mai 14, 2026, [https://superuser.com/questions/413073/windows-console-with-ansi-colors-handling](https://superuser.com/questions/413073/windows-console-with-ansi-colors-handling)  
28. PowerShell is considering enabling VT support \*unconditionally\* in its \`conhost.exe\` sessions. Is it safe? · microsoft terminal · Discussion \#14802 \- GitHub, consulté le mai 14, 2026, [https://github.com/microsoft/terminal/discussions/14802](https://github.com/microsoft/terminal/discussions/14802)  
29. Console Virtual Terminal Sequences \- Microsoft Learn, consulté le mai 14, 2026, [https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences](https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences)  
30. Unicode / Emoji Not Displaying Properly in Windows Terminal \- HP Support Community, consulté le mai 14, 2026, [https://h30434.www3.hp.com/t5/Notebook-Software-and-How-To-Questions/Unicode-Emoji-Not-Displaying-Properly-in-Windows-Terminal/td-p/9647404](https://h30434.www3.hp.com/t5/Notebook-Software-and-How-To-Questions/Unicode-Emoji-Not-Displaying-Properly-in-Windows-Terminal/td-p/9647404)  
31. "Mosaic is switching to its own…" \- Mastodon \- Jake Wharton (@jw@jakewharton.com), consulté le mai 14, 2026, [https://mastodon.jakewharton.com/@jw/114006248420251644](https://mastodon.jakewharton.com/@jw/114006248420251644)  
32. Lazy lists and lazy grids | Jetpack Compose | Android Developers, consulté le mai 14, 2026, [https://developer.android.com/develop/ui/compose/lists](https://developer.android.com/develop/ui/compose/lists)  
33. Mastering Responsive UI in Jetpack Compose | by Farman Ullah Marwat \- Medium, consulté le mai 14, 2026, [https://medium.com/@farimarwat/mastering-responsive-ui-in-jetpack-compose-5a2363b1e001](https://medium.com/@farimarwat/mastering-responsive-ui-in-jetpack-compose-5a2363b1e001)  
34. Android Adaptive Design (Part 1): Make any Compose Screen Responsive in 4 Steps, consulté le mai 14, 2026, [https://tanishranjan.medium.com/responsive-design-part-1-make-any-compose-screen-responsive-in-4-steps-3fe6f3191d3d](https://tanishranjan.medium.com/responsive-design-part-1-make-any-compose-screen-responsive-in-4-steps-3fe6f3191d3d)  
35. Configurable scrollback buffer size for TUI alternate screen \#38283 \- GitHub, consulté le mai 14, 2026, [https://github.com/anthropics/claude-code/issues/38283](https://github.com/anthropics/claude-code/issues/38283)  
36. How do some tools (e.g. nano , less) manage to leave no content in terminals after exit?, consulté le mai 14, 2026, [https://unix.stackexchange.com/questions/336609/how-do-some-tools-e-g-nano-less-manage-to-leave-no-content-in-terminals-aft](https://unix.stackexchange.com/questions/336609/how-do-some-tools-e-g-nano-less-manage-to-leave-no-content-in-terminals-aft)  
37. How do "fullscreen" terminal apps work ? : r/linux \- Reddit, consulté le mai 14, 2026, [https://www.reddit.com/r/linux/comments/1gbzsk7/how\_do\_fullscreen\_terminal\_apps\_work/](https://www.reddit.com/r/linux/comments/1gbzsk7/how_do_fullscreen_terminal_apps_work/)  
38. Using the "alternate screen" in a bash script \- Stack Overflow, consulté le mai 14, 2026, [https://stackoverflow.com/questions/11023929/using-the-alternate-screen-in-a-bash-script](https://stackoverflow.com/questions/11023929/using-the-alternate-screen-in-a-bash-script)  
39. Alternate Screen Buffer (ALTBUF) \- — Terminal Guide, consulté le mai 14, 2026, [https://terminalguide.namepad.de/mode/p47/](https://terminalguide.namepad.de/mode/p47/)  
40. \[BUG\] Thinking spinner causes terminal content to jump/flicker in tmux (main buffer instead of alternate screen) · Issue \#51868 · anthropics/claude-code \- GitHub, consulté le mai 14, 2026, [https://github.com/anthropics/claude-code/issues/51868](https://github.com/anthropics/claude-code/issues/51868)  
41. Use terminal width for top-level constraints · Issue \#719 · JakeWharton/mosaic \- GitHub, consulté le mai 14, 2026, [https://github.com/JakeWharton/mosaic/issues/719](https://github.com/JakeWharton/mosaic/issues/719)  
42. Fix for Claude Code terminal flickering: claude-chill wrapper for CC : r/ClaudeCode \- Reddit, consulté le mai 14, 2026, [https://www.reddit.com/r/ClaudeCode/comments/1qfpugq/fix\_for\_claude\_code\_terminal\_flickering/](https://www.reddit.com/r/ClaudeCode/comments/1qfpugq/fix_for_claude_code_terminal_flickering/)  
43. \[BUG\] TUI flickers/cursor jumps in tmux during streaming output (missing DECSET 2026 synchronized output) · Issue \#37283 · anthropics/claude-code \- GitHub, consulté le mai 14, 2026, [https://github.com/anthropics/claude-code/issues/37283](https://github.com/anthropics/claude-code/issues/37283)  
44. \[BUG\] TUI flickers when there is an existing history · Issue \#9266 · anthropics/claude-code, consulté le mai 14, 2026, [https://github.com/anthropics/claude-code/issues/9266](https://github.com/anthropics/claude-code/issues/9266)  
45. TUI performance and UX improvements · Issue \#2748 · QwenLM/qwen-code \- GitHub, consulté le mai 14, 2026, [https://github.com/QwenLM/qwen-code/issues/2748](https://github.com/QwenLM/qwen-code/issues/2748)  
46. \[builtin-terminal-ui\] Screen flickering · Issue \#3429 · mawww/kakoune \- GitHub, consulté le mai 14, 2026, [https://github.com/mawww/kakoune/issues/3429](https://github.com/mawww/kakoune/issues/3429)  
47. Flickering fix? : r/ClaudeCode \- Reddit, consulté le mai 14, 2026, [https://www.reddit.com/r/ClaudeCode/comments/1py4f62/flickering\_fix/](https://www.reddit.com/r/ClaudeCode/comments/1py4f62/flickering_fix/)  
48. Claude Chill: Fix Claude Code's flickering in terminal | Hacker News, consulté le mai 14, 2026, [https://news.ycombinator.com/item?id=46699072](https://news.ycombinator.com/item?id=46699072)  
49. High bandwidth usage (\~200KB/s) and TUI flickering compared to mosh (\~7KB/s) \#207, consulté le mai 14, 2026, [https://github.com/trzsz/trzsz-ssh/issues/207](https://github.com/trzsz/trzsz-ssh/issues/207)  
50. Screen flickering when running TUI inside VSCode terminal · Issue \#1366 \- GitHub, consulté le mai 14, 2026, [https://github.com/Hmbown/DeepSeek-TUI/issues/1366](https://github.com/Hmbown/DeepSeek-TUI/issues/1366)