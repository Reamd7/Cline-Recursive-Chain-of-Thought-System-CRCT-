/**
 * Logger utility for the dependency system.
 * Provides consistent logging across the application.
 */

export const logger = {
  debug: (message: string, ...args: any[]) => {
    if (process.env.DEBUG) {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  },

  info: (message: string, ...args: any[]) => {
    console.info(`[INFO] ${message}`, ...args);
  },

  warning: (message: string, ...args: any[]) => {
    console.warn(`[WARNING] ${message}`, ...args);
  },

  error: (message: string, ...args: any[]) => {
    console.error(`[ERROR] ${message}`, ...args);
  }
}; 