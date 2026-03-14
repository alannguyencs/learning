const { createProxyMiddleware } = require("http-proxy-middleware");
const fs = require("fs");
const path = require("path");

// Read BACKEND_PORT from root .env
let backendPort = 8999;
const envPath = path.resolve(__dirname, "../../.env");
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf-8");
  const match = envContent.match(/^BACKEND_PORT=(\d+)/m);
  if (match) {
    backendPort = match[1];
  }
}

module.exports = function (app) {
  app.use(
    ["/api", "/auth", "/health"],
    createProxyMiddleware({
      target: `http://localhost:${backendPort}`,
      changeOrigin: true,
    }),
  );
};
