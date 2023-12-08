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
      target: "http://0.0.0.0:8888/api",
    },
  },
};
