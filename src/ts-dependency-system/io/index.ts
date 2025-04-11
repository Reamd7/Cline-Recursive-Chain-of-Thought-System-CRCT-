/**
 * IO Module
 * 
 * This module provides input/output functionality for the dependency processing system,
 * including tracker IO, updating document tracker, updating main tracker, and updating mini tracker.
 */

// Export tracker-io functions
export {
  getTrackerPath,
  readTrackerFile,
  writeTrackerFile,
  backupTrackerFile,
  mergeTrackers,
  exportTracker,
  removeFileFromTracker,
  removeKeyFromTracker,
  TrackerData
} from './tracker-io';

// Export update-doc-tracker functions and data
export {
  docFileInclusionLogic,
  getDocTrackerPath,
  docTrackerData
} from './update-doc-tracker';

// Export update-main-tracker functions and data
export {
  getMainTrackerPath,
  mainKeyFilter,
  aggregateDependenciesContextual,
  mainTrackerData,
  DependencySuggestion
} from './update-main-tracker';

// Export update-mini-tracker functions
export {
  getMiniTrackerData
} from './update-mini-tracker';

// Flag to indicate that the IO module is initialized
export const ioModuleInitialized = true;