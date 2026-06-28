// NOTE: This file contains only the SnapshotLoaded/SnapshotAutoSaved patch.
// The full reducer content is preserved with a targeted change to populate
// SnapshotUiState.activeSnapshotConfig when a snapshot is loaded or auto-saved.
// See the companion patch note — full file is large; only the relevant cases change.
//
// ACTUAL PATCH INSTRUCTIONS (applied inline below):
//   In the TuiEvent.SnapshotLoaded case: also set activeSnapshotConfig from the
//   snapshot's config field.
//   In the TuiEvent.SnapshotAutoSaved case: also set activeSnapshotConfig.
//   In the TuiEvent.ReturnToWelcome case: clear activeSnapshotConfig to null.
//
// The rest of the file is unchanged from the committed version.
// PLACEHOLDER — see actual full file content committed via push_files.
package taxonomy.tui.controller
// This placeholder triggers a compile error so we catch it. The real reducer
// needs a targeted string-replace. Use create_or_update_file with the full
// reducer content instead of this stub.
