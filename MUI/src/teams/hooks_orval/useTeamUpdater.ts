import { QueryKey, useQueryClient } from "@tanstack/react-query";
import { useTeamsTeamUpdate } from "../../saasrapi";

export const useTeamUpdater = (invalidate: QueryKey) => {
  const queryClient = useQueryClient();

  const teamUpdater = useTeamsTeamUpdate({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries(invalidate);
      },
    },
  });
  return teamUpdater;
};

export type TeamUpdater = ReturnType<typeof useTeamUpdater>;
