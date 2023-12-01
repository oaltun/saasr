import Box from "@mui/material/Box";
import { TextField } from "@mui/material/";
import { useState, useEffect } from "react";
import { useSettings } from "../core/contexts/SettingsProvider";
import Button from "@mui/material/Button";
import { IssuesUrl } from "../core/config/urls.js";
import { getToken } from "../auth/utils/auth";
import { useLocation, useNavigate } from "react-router-dom";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import axios from "axios";
import { ErrorHandler } from "../core/utils/errorUtils";
import { GridCol } from "../core/components/GridCol";
import { GridRow } from "../core/components/GridRow";
import { GridSection } from "../core/components/GridSection";
import { GridPage } from "../core/components/GridPage";

const steps = [
  "Plan Details",
  "Review Order",
  "Billing Address & Payment Details",
];

const NewIssue = () => {
  const [loading, setLoading] = useState(false);
  const snackbar = useSnackbar();
  const navigate = useNavigate();

  const token = getToken();

  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");

  const { state } = useLocation();

  const [settingsOpen, setSettingsOpen] = useState(false);
  const { collapsed, open, toggleDrawer } = useSettings();

  useEffect(() => { }, []);

  const handleSettingsToggle = () => {
    setSettingsOpen(!settingsOpen);
  };

  const submit = async () => {
    const token = getToken();
    const config = {
      headers: { Authorization: `Bearer ${token}` },
    };
    const data = {
      title: title,
      message_text: message,
    };
    try {
      const response = await axios.post(IssuesUrl, data, config);

      navigate(`/${process.env.PUBLIC_URL}/issue`);

    } catch (error: any) {
      ErrorHandler.handle(snackbar, error, "(asdnfks)")
    }
  };

  if (loading) {
    return <Box></Box>;
  }
  // ======= //
  // RENDER
  // ======= //
  // MUI page sizes: xs, sm, md, lg, and xl
  // when you set a value for one, it is valid for larger page sizes too.
  // unless that value for larger is specified too.
  return (
    <GridPage>
      <GridSection xs={12}>
        <GridRow xs={12}>
          <GridCol xs={12} >
            New Issue

            <TextField

              label="Title.."
              style={{ width: "100%" }}

              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
              }}
            />

            <TextField

              label="Message.."
              style={{ width: "100%" }}

              multiline={true}
              rows={5}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
              }}
            />

            <Button onClick={submit}>Submit New Issue</Button>

          </GridCol>
        </GridRow>
      </GridSection>
    </GridPage>



  );
};

export default NewIssue;
