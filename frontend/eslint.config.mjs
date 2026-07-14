import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypeScript from "eslint-config-next/typescript";
import prettier from "eslint-config-prettier";

const config = [
  {
    ignores: [
      ".next/**",
      "node_modules/**",
      "src/app/(with-layout)/**",
      "src/app/(with-nonlayout)/**",
      "src/assets/**",
      "src/common/**",
      "src/components/**",
      "src/helpers/**",
      "src/layouts/**",
      "src/slices/**",
      "src/types/**",
      "src/hooks/useRedux.ts",
      "src/lib/react-apexcharts-safe.tsx",
      "src/providers/index.tsx",
      "src/utils/fakeBackendInit.ts",
    ],
  },
  ...nextCoreWebVitals,
  ...nextTypeScript,
  prettier,
  {
    files: ["eslint.config.mjs", "postcss.config.mjs"],
    rules: {
      "import/no-anonymous-default-export": "off",
    },
  },
  {
    files: ["next.config.js"],
    rules: {
      "@typescript-eslint/no-require-imports": "off",
    },
  },
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-unused-expressions": "off",
      "react/no-unescaped-entities": "off",
      "react-hooks/exhaustive-deps": "off",
      "@next/next/no-html-link-for-pages": "off",
    },
  },
];

export default config;
