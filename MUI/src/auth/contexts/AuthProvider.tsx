import React, { createContext, useContext } from "react";
import { useSnackbar } from "../../core/contexts/SnackbarProvider";

import { useLogin } from "../hooks/useLogin";
import { useLogout } from "../hooks/useLogout";
import { LoginInfo } from "../types/loginInfo";
import { TokenInfo } from "../types/tokenInfo";
import { UserInfo } from "../types/userInfo";
import { getToken, getTokenInfo, tokenExpired } from "../utils/auth";




interface AuthContextInterface {
  validUserRoles: (permittedRoles: string[]) => string[];
  isLoggingIn: boolean;
  isLoggingOut: boolean;
  login: (email: string, password: string) => Promise<LoginInfo | null>;
  logout: () => Promise<void>;
  tokenInfo: TokenInfo | null;
  token: string | null;
  expired: () => boolean;
  hasRole: (roles?: string[]) => boolean;
  userInfo: UserInfo | null;
}

export const AuthContext = createContext({} as AuthContextInterface);

type AuthProviderProps = {
  children?: React.ReactNode;
};

const AuthProvider = ({ children }: AuthProviderProps) => {
  const snackbar = useSnackbar();
  const { isLoggingIn, login } = useLogin();
  const { isLoggingOut, logout } = useLogout();
  const tokenInfo = getTokenInfo();
  const token = getToken();
  const userInfo: UserInfo | null = tokenInfo ? tokenInfo.user : null;

  const validUserRoles = (permittedRoles: string[]): string[] => {
    const userRoles: string[] = userInfo?.roles ?? [];
    const validRoles: string[] = [];
    for (const userRole of userRoles) {
      if (permittedRoles.includes(userRole)) {
        validRoles.push(userRole);
      }
    }
    return validRoles;
  };

  const hasRole = (roles?: string[]) => {
    return validUserRoles(roles ?? []).length > 0;
  };

  const expired = (): boolean => {
    return tokenInfo ? tokenExpired(tokenInfo) : true;
  }

  const handleLogin = async (email: string, password: string) => {
    return login({ email, password })
      .then((loginInfo) => {
        // setLoginInfo(loginInfo)
        return loginInfo;
      })
      .catch((err) => {
        throw err;
      });
  };

  const handleLogout = async () => {
    return logout()
      .then(() => {
        // setLoginInfo(null);
      })
      .catch((err) => {
        throw err;
      });
  };

  return (
    <AuthContext.Provider
      value={{
        validUserRoles,
        isLoggingIn,
        isLoggingOut,
        login: handleLogin,
        logout: handleLogout,
        tokenInfo: tokenInfo,
        token: token,
        expired: expired,
        hasRole: hasRole,
        userInfo: userInfo,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthProvider;
