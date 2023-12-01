import { useState, useEffect } from "react";
import Button from "@mui/material/Button";
import { teamInvitationsUrl } from "../../core/config/urls.js";
import axios, { AxiosError } from "axios";
import { getToken } from "../../auth/utils/auth";
import {
  HTTPValidationError,
  TeamInvitationOut,
  useTeamsInvitationList,
} from "../../saasrapi";
import { ErrorHandler } from "../../core/utils/errorUtils";
import { useSnackbar } from "../../core/contexts/SnackbarProvider";
import Important from "../../core/components/Important";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from "@mui/material";

const InvitationAcceptRejectModal = () => {
  /// modal related
  const [modalShow, setModalShow] = useState(false);
  const modalHandleClose = () => setModalShow(false);
  const snackbar = useSnackbar();

  // Invitations type and state
  const initialInvitation = {
    id: "2df4e9e1-df8e-447b-b53d-417a8c5f71c6",
    email: "abc@gmail.com",
    is_admin: false,
    team: {
      id: "eb81bea9-3088-4aab-8d03-b4c524157ab3",
      name: "Team 295b0a01-d888-4ba5-929b-ef6a54441bc1",
    },
    inviter: {
      id: "33d17c36-afc9-4e88-97da-5a1cecc76d9a",
      email: "mail@example.com",
      name: "test",
      surname: "test",
    },
  };
  const [invitations, setInvitations] = useState<TeamInvitationOut[]>([
    initialInvitation,
  ]);

  const invQry = useTeamsInvitationList(
    {},
    {
      query: {
        onError: (error: AxiosError<HTTPValidationError>) => {
          ErrorHandler.handle(snackbar, error, "(c349)");
        },
      },
    }
  );

  useEffect(() => {
    if (invQry.isSuccess) {
      setInvitations(invQry.data.data);
      if (invQry.data.data.length > 0) setModalShow(true);
    }
  }, [invQry]);

  const approveInvite = async (
    id: string,
    teamId: string,
    isApproved: boolean
  ) => {
    const URL = teamInvitationsUrl + "/" + id;

    const token = getToken();

    try {
      const res = await axios({
        method: "put",
        url: URL,
        headers: { Authorization: `Bearer ${token}` },
        data: {
          team_id: teamId,
          is_accept: isApproved,
        },
      });
      console.log(res);
      window.location.reload();
    } catch (error: any) {
      ErrorHandler.handle(snackbar, error, "(111hjkh111)");
    }
  };

  // TODO: try ResponsiveDialog
  return (
    <Dialog open={modalShow} onClose={modalHandleClose}>
      <DialogTitle>Welcome! You have following invitations:</DialogTitle>
      <DialogContent>
        <ul>
          {invitations.map((item) => (
            <li key={item.id}>
              <DialogContentText>
                <Important>{item.inviter.name}</Important>{" "}
                <Important>{item.inviter.surname}</Important> invited you to{" "}
                <Important>{item.team.name}</Important>
                <br />
              </DialogContentText>
              <DialogActions>
                <Button
                  onClick={() => approveInvite(item.id, item.team.id, true)}
                  color="primary"
                >
                  Accept
                </Button>{" "}
                <Button
                  onClick={() => approveInvite(item.id, item.team.id, false)}
                  color="error"
                >
                  Reject
                </Button>
              </DialogActions>
            </li>
          ))}
        </ul>
      </DialogContent>
    </Dialog>
  );
};

export default InvitationAcceptRejectModal;
