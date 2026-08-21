import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {ignores:['.next/**','node_modules/**','playwright-report/**','test-results/**']},
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files:['**/*.{js,mjs,ts,tsx}'],
    languageOptions:{globals:{...globals.browser,...globals.node}},
    plugins:{'react-hooks':reactHooks},
    rules:{
      ...reactHooks.configs.flat.recommended.rules,
      'no-empty':'off',
      'react-hooks/set-state-in-effect':'off',
      '@typescript-eslint/no-explicit-any':'off',
      '@typescript-eslint/no-unused-vars':['error',{argsIgnorePattern:'^_',varsIgnorePattern:'^_'}],
    },
  },
);
