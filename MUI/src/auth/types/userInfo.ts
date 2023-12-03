export type UserInfo = {
  email: string;
  id: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  roles: string[];
  initialTeamParticipationCount: number;
  initialTeamInvitationCount: number;
};