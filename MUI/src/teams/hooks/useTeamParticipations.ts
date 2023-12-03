import { useQuery } from "@tanstack/react-query";
import { teamsParticipationList } from "../../saasrapi";

const fetchParticipations = async () => {
  const participations = await teamsParticipationList();
  //const planMap = array2map(plans.data)
  return { participations: participations.data };
};
export function useTeamParticipations() {
  return useQuery({
    queryKey: ["team participations"],
    queryFn: fetchParticipations,
  });
}
