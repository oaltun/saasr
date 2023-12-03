import React from "react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./core/config/i18n";
import reportWebVitals from "./reportWebVitals";
import { createRoot } from "react-dom/client";

import AuthProvider from "./auth/contexts/AuthProvider";
import Loader from "./core/components/Loader";
import MyErrorBoundary from "./core/components/MyErrorBoundary";
import SettingsProvider from "./core/contexts/SettingsProvider";
import SnackbarProvider from "./core/contexts/SnackbarProvider";
import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";




// react query settings
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error: any, _query) => {
      try {
        console.log(`QueryClient: Something went wrong: ${error.message}`)

      } catch (error: any) {
        console.log("QueryClient: Look at that! Caught an error.");
      }
    }
  }),
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 4,
      suspense: true,
    },
  },
});

const container = document.getElementById("root");
const root = createRoot(container!);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <React.Suspense fallback={<Loader />}>
        <QueryClientProvider client={queryClient}>
          <SettingsProvider>
            <MyErrorBoundary>
              <SnackbarProvider>
                <AuthProvider>
                  <App />
                </AuthProvider>
              </SnackbarProvider>
            </MyErrorBoundary>
          </SettingsProvider>
          <ReactQueryDevtools initialIsOpen />
        </QueryClientProvider>
      </React.Suspense>
    </BrowserRouter>
  </React.StrictMode>
)

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
