import { AxiosError } from "axios";
import { SnackbarContextInterface } from "../../core/contexts/SnackbarProvider";
import { ErrorHandler } from "../../core/utils/errorUtils";
import { TeamUpdate } from "../../saasrapi/model/teamUpdate";
import { TeamUpdater } from "../hooks_orval/useTeamUpdater";

export const handleTeamNameChange = (
  newTeamName: string,
  teamId: string,
  teamUpdater: TeamUpdater,
  snackbar: SnackbarContextInterface,
  pcode = ""
) => {
  const data: TeamUpdate = { name: newTeamName };
  const onError = (error: AxiosError<any>) =>
    ErrorHandler.handle(snackbar, error, pcode);
  teamUpdater.mutate({ id: teamId, data: data }, { onError });
};
