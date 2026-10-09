import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./auth";
import { ChatResultsProvider } from "./chatResults";
import { PointsProvider } from "./fun/points";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PointsProvider>
          <ChatResultsProvider>
            <App />
          </ChatResultsProvider>
        </PointsProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
