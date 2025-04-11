// 为Node.js内置模块提供类型定义
declare module 'fs' {
  export * from 'node:fs';
}

declare module 'path' {
  export * from 'node:path';
}

// 为Jest全局函数提供类型定义
declare global {
  const describe: jest.Describe;
  const it: jest.It;
  const expect: jest.Expect;
  const jest: jest.Jest;
}