import { Button, Typography } from "@mui/material";
import { GridCol } from "../../core/components/GridCol";
import { GridRow } from "../../core/components/GridRow";
import Section from "../../core/components/Section";
import Moment from "react-moment";
import axios from "axios";
import { IssuesUrl } from "../../core/config/urls";
import { getToken } from "../../auth/utils/auth";
import { ErrorHandler } from "../../core/utils/errorUtils";
import { useSnackbar } from "../../core/contexts/SnackbarProvider";
import { GridBr } from "../../core/components/GridBr";
import { useNavigate } from "react-router";
import { Link } from "react-router-dom";



export type IssueSummaryItem = {
  title: string;
  id: string;
  owner: {
    id: string;
    email: string;
    name: string;
    surname: string;
  };
  created_at: string;
  is_closed: boolean;
  closed_at: string;
  closer: {
    id: string;
    email: string;
    name: string;
    surname: string;
  };
}




export type IssueSummaryProps = {
  owner_name: string,
  owner_surname: string,
  closer_name?: string,
  closer_surname?: string,
  issue_id: string,
  issue_title: string,
  issue_is_closed: boolean,
  issue_created_at: string,
  issue_closed_at?: string,
  show_controls?: boolean
};
export const IssueSummary = ({
  owner_name,
  owner_surname,
  closer_name,
  closer_surname,
  issue_id,
  issue_title,
  issue_is_closed,
  issue_created_at,
  issue_closed_at,
  show_controls,
}: IssueSummaryProps) => {
  const controls = show_controls ?? false;
  const snackbar = useSnackbar();
  const navigate = useNavigate();



  return <GridRow xs={12}>
    <Section title={
      <Link
        to={`${process.env.PUBLIC_URL}/issue/` + issue_id}
      >
        {issue_title}
      </Link>}>
      <GridRow>
        Status: {issue_is_closed ? "Closed" : "Open"}
      </GridRow>
      <GridRow>
        Opened by {owner_name + " " + owner_surname} at &nbsp; <Moment
          format="DD/MM/YYYY hh:mm">
          {issue_created_at}
        </Moment>
      </GridRow>


      {issue_is_closed
        && <GridRow>
          <Typography>Closed
            &nbsp;
            {!!closer_name && !!closer_surname
              && <span>by {closer_name + " " + owner_surname}</span>
            }

            at <Moment
              format="DD/MM/YYYY hh:mm">
              {issue_closed_at}
            </Moment>
          </Typography>
        </GridRow>
      }

      <GridRow>Issue id: &nbsp; {issue_id}</GridRow>

    </Section>
  </GridRow>




};

