import Alert, { AlertColor } from "@mui/material/Alert/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Snackbar from "@mui/material/Snackbar";
import Typography from "@mui/material/Typography";
import React, { createContext, useContext, useState } from "react";
import { useTranslation } from "react-i18next";
import { FrontendErrorMessage } from "../utils/errorUtils";


export interface SnackbarContextInterface {
  error: (newMessage: string | FrontendErrorMessage) => void;
  success: (newMessage: string | FrontendErrorMessage) => void;
  info: (newMessage: string | FrontendErrorMessage) => void;
  warning: (newMessage: string | FrontendErrorMessage) => void;
}

export const SnackbarContext = createContext({} as SnackbarContextInterface);

type SnackbarProviderProps = {
  children: React.ReactNode;
};

const SnackbarProvider = ({ children }: SnackbarProviderProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [body, setBody] = useState("");
  const [message, setMessage] = useState<string | FrontendErrorMessage>("");
  const [severity, setSeverity] = useState<AlertColor | undefined>(undefined);

  const handleClose = (
    _event: any,
    reason?: string
  ) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };

  const snackbarOpen = (message: string | FrontendErrorMessage, severity: AlertColor) => {
    setMessage(message)
    setSeverity(severity);
    setOpen(true);
  }

  const error = (newMessage: string | FrontendErrorMessage) => {
    snackbarOpen(newMessage, "error");
  };

  const success = (newMessage: string | FrontendErrorMessage) => {
    snackbarOpen(newMessage, "success");
  };

  const info = (newMessage: string | FrontendErrorMessage) => {
    snackbarOpen(newMessage, "info");
  };

  const warning = (newMessage: string | FrontendErrorMessage) => {
    snackbarOpen(newMessage, "warning");
  };


  console.log(message);

  return (
    <SnackbarContext.Provider
      value={{ error, success, warning, info }}
    >
      {children}
      <Snackbar
        key={body}
        anchorOrigin={{
          vertical: "top",
          horizontal: "center",
        }}
        open={open}
        autoHideDuration={8000}
        onClose={handleClose}
      >
        <Alert
          onClose={handleClose}
          severity={severity}
          sx={{ width: '100%' }}

        >{typeof message === "string" ? (
          <>
            <AlertTitle>{message}</AlertTitle>
          </>
        ) : (
          <>
            {message.titleStr && <AlertTitle>{message.titleStr}</AlertTitle>}
            {message.detailStr && <Typography> {message.detailStr}</Typography>}
            {message.type && <Typography>Type: {message.type}</Typography>}
          </>
        )}


        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
};

export function useSnackbar() {
  return useContext(SnackbarContext);
}

export default SnackbarProvider;
