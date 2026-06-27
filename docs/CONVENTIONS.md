# CONVENTIONS

- **Build command**: `JAVA_HOME=~/.gradle/jdks/jdk-21.0.11+10 ./gradlew compileKotlin compileTestKotlin --no-daemon`.
- **Test command**: `JAVA_HOME=~/.gradle/jdks/jdk-21.0.11+10 ./gradlew test --no-daemon --tests "<pattern>"`.
- **Branch naming**: `pr-NN-short-slug`.
- **PR title**: `PR #NN: <imperative summary>`.
- Squash-merge; delete branch on merge.
- Never edit code from the parent agent — always delegate to coding subagent.
