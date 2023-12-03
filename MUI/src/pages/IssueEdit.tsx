import Box from "@mui/material/Box";
import { CircularProgress, Grid, TextField, Typography } from "@mui/material/";
import { useState, useEffect } from "react";
import { useSettings } from "../core/contexts/SettingsProvider";

import Button from "@mui/material/Button";
import Moment from "react-moment";
import { IssuesUrl, PostMessageUrl } from "../core/config/urls.js";
import axios from "axios";
import { getToken } from "../auth/utils/auth";
import { useLocation } from "react-router-dom";
import { useParams } from "react-router-dom";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../core/utils/errorUtils";
import { GridPage } from "../core/components/GridPage";
import { GridRow } from "../core/components/GridRow";
import { GridCol } from "../core/components/GridCol";
import { GridSection } from "../core/components/GridSection";
import Section from "../core/components/Section";
import { IssueSummary } from "../issues/components/IssueSummary";


const IssueEdit = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const snackbar = useSnackbar();

  const token = getToken();

  const [message, setMessage] = useState("");

  const [issueDetail, setIssueDetail] = useState({
    title: "string",
    id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    owner: {
      id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      email: "string",
      name: "string",
      surname: "string",
    },
    created_at: "2022-10-14T11:05:13.562Z",
    is_closed: true,
    closed_at: "2022-10-14T11:05:13.562Z",
    closer: {
      id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      email: "string",
      name: "string",
      surname: "string",
    },
    messages: [
      {
        issue_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        text: "string",
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        created_at: "2022-10-14T11:18:19.564Z",
        owner: {
          id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          email: "string",
          name: "string",
          surname: "string",
        },
      },
      {
        issue_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        text: "string",
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        created_at: "2022-10-14T11:18:19.564Z",
        owner: {
          id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          email: "string",
          name: "string",
          surname: "string",
        },
      },
    ],
  });

  const { state } = useLocation();

  const [settingsOpen, setSettingsOpen] = useState(false);
  const { collapsed, open, toggleDrawer } = useSettings();

  useEffect(() => {
    getIssueDetail();
  }, []);

  const getIssueDetail = async () => {
    axios
      .get(IssuesUrl + "/" + id, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        console.log(res);
        setIssueDetail(res.data);
      })
      .catch((error) => {
        ErrorHandler.handle(snackbar, error, "(1qweq11111)");
      });
  };



  const handleSettingsToggle = () => {
    setSettingsOpen(!settingsOpen);
  };

  const addIssue = async () => {
    const config = {
      headers: { Authorization: `Bearer ${token}` },
    };
    const data = {
      issue_id: id,
      text: message,
    };
    try {
      const response = await axios.post(PostMessageUrl, data, config);
      window.location.reload();
    } catch (error: any) {
      ErrorHandler.handle(snackbar, error, "(sdl33)");
    }
  };

  const closeIssue = async (id) => {
    try {
      const res = await axios({
        method: "put",
        url: IssuesUrl + "/" + id,
        headers: { Authorization: `Bearer ${getToken()}` },
        data: {
          is_closed: true,
        },
      });
      console.log(res);
      window.location.reload();
    } catch (error: any) {
      ErrorHandler.handle(snackbar, error, "(isasa)");
    }
  };

  if (loading) {
    return <CircularProgress />;
  }
  // ======= //
  // RENDER
  // ======= //
  // MUI page sizes: xs, sm, md, lg, and xl
  // when you set a value for one, it is valid for larger page sizes too.
  // unless that value for larger is specified too.
  return (
    <GridPage>
      <GridSection spacing={1}>

        <GridRow spacing={0}>
          {!issueDetail.is_closed && <Button
            color="warning"
            variant="contained"
            size="small"
            onClick={() => closeIssue(issueDetail.id)}
          >
            Close Issue
          </Button>

          }
        </GridRow>

        <GridRow spacing={1}>
          <IssueSummary
            issue_closed_at={issueDetail.closed_at}
            issue_created_at={issueDetail.created_at}
            issue_id={issueDetail.id}
            issue_is_closed={issueDetail.is_closed}
            issue_title={issueDetail.title}
            owner_name={issueDetail.owner.name}
            owner_surname={issueDetail.owner.surname}
            show_controls={true}
          />
        </GridRow>
        {issueDetail.messages.map((item) => (
          <GridCol xs={12} >
            <Section
              title={
                item.owner.name
                + " "
                + item.owner.surname
              }
            >
              <GridRow>
                <GridCol xs={12} justifyContent="right">
                  Message added at&nbsp; <Moment format="DD/MM/YYYY hh:mm">{item.created_at}</Moment>
                </GridCol>
              </GridRow>
              <GridRow>
                <GridCol xs={12}>
                  <Typography>
                    {item.text}
                  </Typography>
                </GridCol>
              </GridRow>
            </Section>
          </GridCol>

        ))}
      </GridSection>

      {
        !issueDetail.is_closed && (
          <GridRow xs={12} md={8}>

            <TextField
              label="New message text"
              style={{ width: "100%" }}
              multiline={true}
              rows={5}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
              }}
            />
            <Button disabled={issueDetail.is_closed} onClick={addIssue}>Add Message</Button>
          </GridRow>

        )
      }

    </GridPage >
  );
}
export default IssueEdit;
