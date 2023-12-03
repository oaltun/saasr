import Button from "@mui/material/Button";
import Moment from "react-moment";
import { useParams } from "react-router-dom";
import {
  ErrorDetail,
  PaymentFormAddLicense,
  TeamInvitationCreate,
  TeamInvitationOut,
  TeamInvitationStatusUpdate,
  TeamUpdate,
  usePaymentPaymentRequestAddLicense,
  usePaymentPaymentRequestCurrentPrice,
  useTeamsInvitationAcceptDelete,
  useTeamsInvitationCreate,
  useTeamsTeamGet,
} from "../saasrapi";
import { Box, CircularProgress, Grid, Typography } from "@mui/material";
import Section from "../core/components/Section";
import SubSection from "../core/components/SubSection";
import Important from "../core/components/Important";
import { useQueryClient } from "@tanstack/react-query";
import InputSubmitter from "../core/components/InputSubmitter";
import { AxiosError } from "axios";
import { useSnackbar } from "../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../core/utils/errorUtils";
import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";
import { useTeamUpdater } from "../teams/hooks_orval/useTeamUpdater";
import { handleTeamNameChange } from "../teams/handlers/handleTeamNameChange";
import { GridSection } from "../core/components/GridSection";
import { GridPage } from "../core/components/GridPage";

const TeamManagement = () => {
  const { id: teamId } = useParams();
  const queryClient = useQueryClient();
  const snackbar = useSnackbar();

  // ======= //
  //   QUERIES
  // ======= //

  const teamQry = useTeamsTeamGet(teamId);
  const currentPriceQry = usePaymentPaymentRequestCurrentPrice({
    team_id: teamId,
  });

  // ======= //
  //   MUTATORS
  // ======= //

  const teamUpdater = useTeamUpdater(teamQry.queryKey);

  const invitationCrt = useTeamsInvitationCreate({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries(teamQry.queryKey);
      },
    },
  });

  const invitationAD = useTeamsInvitationAcceptDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries(teamQry.queryKey);
      },
    },
  });

  const addLicenseMt = usePaymentPaymentRequestAddLicense({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries(teamQry.queryKey);
      },
    },
  });

  // ======= //
  //   HANDLERS
  // ======= //

  const handleNumLicencesNextTermChange = (num: string) => {
    const data: TeamUpdate = { number_of_licenses_next_term: Number(num) };
    const onError = (error: AxiosError<any>) =>
      ErrorHandler.handle(snackbar, error, "(updatingNumLicensesNextTerm)");
    teamUpdater.mutate({ id: teamId, data: data }, { onError });
  };

  const handleAddLicense = (num: string) => {
    const data: PaymentFormAddLicense = {
      number_of_licenses: Number(num),
      team_id: teamId,
    };
    const onError = (error: AxiosError<any>) =>
      ErrorHandler.handle(snackbar, error, "(whenaddinglicense)");
    addLicenseMt.mutate({ data }, { onError });
  };

  const handleInvite = (email: string, is_admin: boolean) => {
    const data: TeamInvitationCreate = {
      email: email,
      is_admin: is_admin,
      team_id: teamId,
    };
    const onError = (error: string | AxiosError<any> | ErrorDetail | Error) =>
      ErrorHandler.handle(snackbar, error, "(g8768)");
    invitationCrt.mutate({ data: data }, { onError });
  };

  const handleInvitationRemove = (invitation: TeamInvitationOut) => {
    const data: TeamInvitationStatusUpdate = {
      team_id: teamId,
      is_accept: false,
    };
    const onError = (error: string | Error | ErrorDetail | AxiosError<any>) =>
      ErrorHandler.handle(snackbar, error, "(b98769sd)");
    invitationAD.mutate(
      { invitationId: invitation.id, data: data },
      { onError }
    );
  };

  const fixNewLicenceNum = (value: string) => {
    const num = Number(value);
    if (value === "" || (0 < num && num < Number.MAX_SAFE_INTEGER))
      return value;

    return "1";
  };

  // ======= //
  // RENDER
  // ======= //
  // MUI page sizes: xs, sm, md, lg, and xl
  // when you set a value for one, it is valid for larger page sizes too.
  // unless that value for larger is specified too.
  if (
    teamQry.data &&
    teamQry.data.data &&
    teamQry.data.data.billing_cycle &&
    teamQry.data.data.plan &&
    currentPriceQry.data &&
    currentPriceQry.data.data
  ) {
    return (
      <GridPage>
        <GridSection>
          <Section title="Team Name">
            <Typography gutterBottom>
              Team name:
              <Important>{teamQry.data.data.name}</Important>
            </Typography>

            <InputSubmitter
              loading={teamUpdater.isLoading}
              label="New team name"
              defaultValue={teamQry.data.data.name}
              onButtonClick={(inputValue: string) =>
                handleTeamNameChange(
                  inputValue,
                  teamId,
                  teamUpdater,
                  snackbar,
                  "(2314)"
                )
              }
              buttonContents="Update"
            />
          </Section>
        </GridSection>

        <GridSection>
          <Section title="Team Members">
            <SubSection title="Invitations">
              <Typography>
                Invite team members here. Only team members can use the Saasr
                features, team administrators can not.
              </Typography>

              <InputSubmitter
                loading={invitationCrt.isLoading}
                label="Add an email to invite to the team."
                defaultValue=""
                onButtonClick={(email: string) => handleInvite(email, false)}
                buttonContents="Invite"
              />

              {teamQry.data.data.invitations?.filter((prt) => !prt.is_admin)
                .length === 0 && (
                <Typography>
                  This team has no member invitations, yet.
                </Typography>
              )}
              {
                /* if there are members */
                teamQry.data.data.invitations
                  ?.filter((inv) => !inv.is_admin)
                  .map((invitation) => {
                    return (
                      <li key={invitation.email}>
                        {invitation.email}{" "}
                        <LoadingButton
                          style={{ color: "red" }}
                          onClick={() => {
                            handleInvitationRemove(invitation);
                          }}
                          loading={invitationAD.isLoading}
                        >
                          Remove Invitation
                        </LoadingButton>
                      </li>
                    );
                  })
              }
            </SubSection>

            <SubSection title="Members">
              {teamQry.data.data.participations?.filter((prt) => !prt.is_admin)
                .length === 0 && (
                <Typography>This team has no members, yet.</Typography>
              )}
              {
                /* if there are members */
                teamQry.data.data.participations
                  ?.filter((prt) => !prt.is_admin)
                  .map((member) => {
                    return (
                      <li key={member.user.email}>
                        {member.user.email}{" "}
                        <Button style={{ color: "red" }}>Remove Member</Button>
                      </li>
                    );
                  })
              }
            </SubSection>
          </Section>
        </GridSection>

        <GridSection>
          <Section title="Team Admins">
            <SubSection title="Invitations">
              <Typography>
                Invite team admins here. Only team members can use the Saasr
                features, team admins can not.
              </Typography>

              <InputSubmitter
                loading={invitationCrt.isLoading}
                label="Add an email to invite to the team."
                defaultValue=""
                onButtonClick={(email: string) => handleInvite(email, true)}
                buttonContents="Invite"
              />

              {teamQry.data.data.invitations?.filter((prt) => prt.is_admin)
                .length === 0 && (
                <Typography>
                  This team has no admin invitations, yet.
                </Typography>
              )}
              {
                /* if there are admins */
                teamQry.data.data.invitations
                  ?.filter((inv) => inv.is_admin)
                  .map((invitation) => {
                    return (
                      <li key={invitation.email}>
                        {invitation.email}{" "}
                        <LoadingButton
                          style={{ color: "red" }}
                          onClick={() => {
                            handleInvitationRemove(invitation);
                          }}
                          loading={invitationAD.isLoading}
                        >
                          Remove Invitation
                        </LoadingButton>
                      </li>
                    );
                  })
              }
            </SubSection>

            <SubSection title="Admins">
              {teamQry.data.data.participations?.filter((prt) => prt.is_admin)
                .length === 0 && (
                <Typography>This team has no admins, yet.</Typography>
              )}
              {
                /* if there are members */
                teamQry.data.data.participations
                  ?.filter((prt) => prt.is_admin)
                  .map((member) => {
                    return (
                      <li key={member.user.email}>
                        {member.user.email}{" "}
                        <Button style={{ color: "red" }}>Remove Admin</Button>
                      </li>
                    );
                  })
              }
            </SubSection>
          </Section>
        </GridSection>

        <GridSection>
          <Section title="Team Licenses">
            <Typography>
              The team has currently{" "}
              <Important>{teamQry.data.data.number_of_licenses}</Important>{" "}
              licences.
            </Typography>

            <Typography>
              Current plan:{" "}
              <Important>
                {teamQry.data.data.plan.name} (
                {teamQry.data.data.plan.description})
              </Important>
              .
            </Typography>
            <Typography>
              Current billing period:{" "}
              <Important>
                {teamQry.data.data.billing_cycle.name} (
                {teamQry.data.data.billing_cycle.description})
              </Important>
              .
            </Typography>
            <Typography>
              {" "}
              This term expires on{" "}
              <Important>
                <Moment format="DD/MM/YYYY">
                  {teamQry.data.data.term_end_date}
                </Moment>
              </Important>{" "}
            </Typography>
            <Typography>
              If you add new licenses today each license would be{" "}
              <Important>${currentPriceQry.data.data.price}</Important> (We
              charge only for the remaining time).
            </Typography>

            <InputSubmitter
              label="Number of new licenses"
              defaultValue=""
              fixValue={(value) => fixNewLicenceNum(value)}
              valueError={(val) =>
                val ? "" : "Number of new licenses can not be empty."
              }
              loading={addLicenseMt.isLoading}
              onButtonClick={(val) => handleAddLicense(val)}
              buttonContents="Add new licenses"
              end={(val) =>
                val && (
                  <Typography component={"span"}>
                    {" "}
                    Total:{" "}
                    <Important>
                      $
                      {String(
                        Number(val) * Number(currentPriceQry.data.data.price)
                      )}
                    </Important>
                  </Typography>
                )
              }
            />
          </Section>
        </GridSection>

        <GridSection>
          <Section title="Licenses Next Term">
            <Typography>
              {" "}
              Next term the team will have{" "}
              <Important>
                {teamQry.data.data.number_of_licenses_next_term}
              </Important>{" "}
              licenses. At the start of the term, we will automatically charge
              the money.{" "}
            </Typography>

            <InputSubmitter
              loading={teamUpdater.isLoading}
              label="Next term number of licenses"
              defaultValue={teamQry.data.data.number_of_licenses_next_term.toString()}
              onButtonClick={(val) => handleNumLicencesNextTermChange(val)}
              buttonContents="Set next term number of licenses"
            />
          </Section>
        </GridSection>
      </GridPage>
    );
  }
  return <CircularProgress />;
};

export default TeamManagement;
