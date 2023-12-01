import {
  HTTPValidationError,
  TeamParticipationOut,
  useTeamsParticipationList,
} from "../saasrapi";
import Loader from "../core/components/Loader";
import { Box, Button, Divider, Typography } from "@mui/material";
import InvitationAcceptRejectModal from "../teams/components/InvitationAcceptRejectModal";
import { AxiosError } from "axios";
import { useNavigate } from "react-router";
import { ErrorHandler } from "../core/utils/errorUtils";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { GridSection } from "../core/components/GridSection";
import Section from "../core/components/Section";
import { GridCol } from "../core/components/GridCol";
import { GridRow } from "../core/components/GridRow";
import Important from "../core/components/Important";
import { GridPage } from "../core/components/GridPage";

// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
const Teams = () => {
  const snackbar = useSnackbar();
  const navigate = useNavigate();

  const participationQry = useTeamsParticipationList(
    {},
    {
      query: {
        onError: (error: AxiosError<HTTPValidationError>) => {
          ErrorHandler.handle(snackbar, error, "(s9879)");
        },
      },
    }
  );

  if (participationQry.data) {
    return (
      <GridPage>
        <GridSection md={6}>
          <Section title="Your Team Participations">
            {participationQry.data?.data.map(
              (participation: TeamParticipationOut, index: number) => {
                return (
                  <GridSection>
                    <GridRow justifyContent="space-between">
                      <GridCol xs={10}>
                        <Typography>
                          <Important>
                            {participation.is_admin ? "Admin" : "Member"}
                          </Important>
                          {" in " + participation.team.name}
                        </Typography>
                      </GridCol>
                      <GridCol xs={2} justifyContent="right">
                        {participation.is_admin && (
                          <Button
                            value="Manage"
                            size="small"
                            sx={{ ml: 3 }}
                            onClick={() => {
                              navigate(
                                `/${process.env.PUBLIC_URL}/team/${participation.team_id}`
                              );
                            }}
                          >
                            Manage
                          </Button>
                        )}
                      </GridCol>
                    </GridRow>
                  </GridSection>
                );
              }
            )}
            <InvitationAcceptRejectModal />
          </Section>
        </GridSection>
      </GridPage>
    );
  }

  if (participationQry.isLoading) {
    return <Loader />;
  }
  if (participationQry.isError) {
    console.log("Error, (b88b613d)");
    return <Box>Error. Error code: {participationQry.error.code}</Box>;
  }

  return <Box>Undefined error on team participation page.</Box>;
};

export default Teams;
