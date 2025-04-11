import { helloWorld } from '../index';

describe('Index', () => {
  it('should return hello world message', () => {
    expect(helloWorld()).toBe('Hello, World! TypeScript Dependency System is initialized.');
  });
});