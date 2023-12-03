import { UserInfo } from "./userInfo";

export type TokenInfo = {
  downloadedAt: number;
  timeDelta: number;
  user: UserInfo;
};
