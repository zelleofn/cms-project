module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/src/setup-jest.ts'],
  testPathIgnorePatterns: [
  '<rootDir>/node_modules/',
  '<rootDir>/dist/',
  '<rootDir>/e2e/'
],
  transform: {
    '^.+\\.(ts|mjs|js|html)$': [
      'jest-preset-angular',
      {
        tsconfig: '<rootDir>/tsconfig.spec.json',
        stringifyContentPathRegex: '\\.(html|svg)$',
      },
    ],
  },
 moduleNameMapper: {
  '^src/(.*)$': '<rootDir>/src/$1',
},

  transformIgnorePatterns: ['node_modules/(?!.*\\.mjs$)'],
};