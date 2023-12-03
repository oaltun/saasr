module.exports = {
  saasrapi: {
    output: {
      mode: "tags-split",
      workspace: "src/saasrapi",
      target: "./api.ts",
      schemas: "./model",
      client: "react-query",
      mock: true,
      prettier: true,
    },
    input: {
      target: "https://saasr-api.example.com/api",
    },
  },
};
