/**
 * 日志记录工具
 */

// Simple logger implementation that can be replaced with a more robust one if needed
export interface Logger {
  debug(message: string): void;
  info(message: string): void;
  warn(message: string): void;
  warning(message: string): void; // Alias for warn
  error(message: string): void;
}

class SimpleLogger implements Logger {
  private moduleName: string;
  
  constructor(moduleName: string) {
    this.moduleName = moduleName;
  }
  
  debug(message: string): void {
    console.debug(`[${this.moduleName}] ${message}`);
  }
  
  info(message: string): void {
    console.info(`[${this.moduleName}] ${message}`);
  }
  
  warn(message: string): void {
    console.warn(`[${this.moduleName}] ${message}`);
  }
  
  warning(message: string): void {
    this.warn(message);
  }
  
  error(message: string): void {
    console.error(`[${this.moduleName}] ${message}`);
  }
}

// Cache loggers to avoid creating multiple instances for the same module
const loggers: { [key: string]: Logger } = {};

/**
 * Get a logger for a specific module
 * @param moduleName The name of the module
 * @returns A logger instance
 */
export function getLogger(moduleName: string): Logger {
  if (!loggers[moduleName]) {
    loggers[moduleName] = new SimpleLogger(moduleName);
  }
  return loggers[moduleName];
}

/**
 * Set the global log level
 * @param level The log level to set
 */
export function setLogLevel(level: 'debug' | 'info' | 'warn' | 'error'): void {
  // 这里可以添加更复杂的日志级别控制逻辑
  console.info(`Setting log level to ${level}`);
} 