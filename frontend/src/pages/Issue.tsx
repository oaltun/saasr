import Box from "@mui/material/Box";
import { useState, useEffect } from "react";
import { useSettings } from "../core/contexts/SettingsProvider";
import Button from "@mui/material/Button";
import { useNavigate } from "react-router-dom";
import { IssuesUrl } from "../core/config/urls.js";
import axios from "axios";
import { getToken } from "../auth/utils/auth";
import { useLocation } from "react-router-dom";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../core/utils/errorUtils";
import { GridSection } from "../core/components/GridSection";
import { GridCol } from "../core/components/GridCol";
import { GridRow } from "../core/components/GridRow";
import { GridPage } from "../core/components/GridPage";
import Section from "../core/components/Section";
import AddCommentIcon from "@mui/icons-material/AddComment";
import { Link } from "@mui/material";
import { IssueOut } from "../saasrapi";
import {
  IssueSummary,
  IssueSummaryItem,
} from "../issues/components/IssueSummary";

function compareIssues(a, b) {
  if (a.created_at < b.created_at) {
    return 1;
  }
  if (a.created_at > b.created_at) {
    return -1;
  }
  return 0;
}

const Issue = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const snackbar = useSnackbar();
  const { state } = useLocation();

  const [settingsOpen, setSettingsOpen] = useState(false);
  const { collapsed, open, toggleDrawer } = useSettings();

  const [issues, setIssues] = useState([
    {
      title: "string",
      id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      owner: {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        email: "string",
        name: "string",
        surname: "string",
      },
      created_at: "2022-10-13T08:45:52.974Z",
      is_closed: true,
      closed_at: "2022-10-13T08:45:52.974Z",
      closer: {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        email: "string",
        name: "string",
        surname: "string",
      },
    },
  ]);

  useEffect(() => {
    getIssues();
  }, []);

  const token = getToken();
  const getIssues = async () => {
    const token = getToken();
    axios
      .get(IssuesUrl, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        console.log("prc", res);

        const objs: [] = res.data;

        objs.sort(compareIssues);
        setIssues(res.data);
      })
      .catch((error) => {
        ErrorHandler.handle(snackbar, error, "(qqxcd)");
      });
  };

  const handleSettingsToggle = () => {
    setSettingsOpen(!settingsOpen);
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
      <GridSection>
        <GridRow>
          <GridCol>
            <Button
              onClick={() => {
                navigate(`/${process.env.PUBLIC_URL}/issue-new`);
              }}
              startIcon={<AddCommentIcon />}
            >
              Add Issue
            </Button>
          </GridCol>
        </GridRow>

        {issues.map((item: IssueSummaryItem) => (
          <GridRow>
            <IssueSummary
              issue_closed_at={item.closed_at}
              issue_created_at={item.created_at}
              issue_id={item.id}
              issue_is_closed={item.is_closed}
              issue_title={item.title}
              owner_name={item.owner.name}
              owner_surname={item.owner.surname}
            />
          </GridRow>
        ))}
      </GridSection>
    </GridPage>
  );
};

export default Issue;
