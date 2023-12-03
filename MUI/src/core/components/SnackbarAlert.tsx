import Alert, { AlertColor } from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { PropsWithChildren } from "react";



export interface SnackbarAlertProps {
  open: boolean;
  handleClose?: (() => void) | undefined;
  severity?: AlertColor | undefined;
  autoHideDuration?: number | null | undefined;
  key?: string | undefined;
}

export const SnackbarAlert = (props: PropsWithChildren<SnackbarAlertProps>) => {


  return (
    <>

      <Snackbar
        open={props.open}
        autoHideDuration={props.autoHideDuration}
        onClose={props.handleClose}
        key={props.key}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={props.handleClose}
          severity={props.severity}
          sx={{ width: '100%' }}

        >
          {props.children}
        </Alert>
      </Snackbar>
    </>
  )
};

export default SnackbarAlert;
