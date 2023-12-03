import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import React, { Fragment, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useTranslation } from "react-i18next";
import { useQueryErrorResetBoundary } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import Loader from "./Loader";
import Result from "./Result";
import { ErrorHandler } from "../utils/errorUtils";
import { useSnackbar } from "../contexts/SnackbarProvider";

type MyErrorBoundaryProps = {
  children: React.ReactNode;
};

const MyErrorBoundary = ({ children }: MyErrorBoundaryProps) => {
  const { reset } = useQueryErrorResetBoundary();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const snackbar = useSnackbar();

  return (
    <ErrorBoundary
      onReset={reset}
      fallbackRender={({ error, resetErrorBoundary }) => (
        <Result
          extra={
            <Fragment>
              <Button onClick={() => {
                resetErrorBoundary();
                navigate("/login");
              }} variant="contained">
                {t("auth.register.back")}
              </Button>
              {" "}
              <Button onClick={() => resetErrorBoundary()} variant="contained">
                {t("common.retry")}
              </Button>
            </Fragment>
          }
          status="error"
          title={ErrorHandler.handle(undefined, error, "g283")?.titleStr ?? "Oops!"}
          subTitle={"Details: " + ErrorHandler.handle(undefined, error, "g283")?.detailStr}
        />
      )}
    >
      <React.Suspense fallback={<Loader />}>{children}</React.Suspense>
    </ErrorBoundary >
  );
};

export default MyErrorBoundary;
