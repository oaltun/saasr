import decodeJwt from "jwt-decode";
import {
  registerUrl,
  passwordResetUrl,
  passwordResetRequestUrl,
  loginUrl,
} from "../../core/config/urls.js";
import { UserInfo } from "../types/userInfo";
import axios from "axios";
import { TokenInfo } from "../types/tokenInfo.js";
import { LoginInputData } from "../types/loginInput.js";
import { LoginInfo } from "../types/loginInfo.js";
import { UserInput } from "../types/userInput.js";
import { UserOut } from "../../saasrapi/index.js";

export const getToken = () => {
  return localStorage.getItem("token");
};
export const deleteToken = () => {
  return localStorage.removeItem("token");
};

type TokenDecoded = {
  sub: string; //user email
  exp: number; //expiration time
  prm: string; //user permissions
  uid: string; //user id
  td: number; //time delta in minutes
  ia: number; //user is_active
  isu: number; //user is_superuser
  iv: number; //user is_verified
  pc: number; //user team participation count
  ic: number; //user team invitation count
};

export const tokenExpired = (tokenInfo: TokenInfo | null): boolean => {
  if (!tokenInfo) return true;
  // We assume token expires earlier. This may help to reduce unnecessary page flashs.
  const earlier = 60 * 1000; // 60 seconds
  const expireTime =
    tokenInfo.downloadedAt + tokenInfo.timeDelta * 60 * 1000 - earlier;
  const expired = Date.now() > expireTime;
  // if (expired) logout();
  return expired;
};

class FetchResponseError extends Error {
  pcode: string;
  status: number;
  response_statusText: string;
  response_headers: Headers;
  response_type: ResponseType;

  constructor(message: string, pcode: string, response: Response) {
    super(message);
    this.pcode = pcode;
    this.status = response.status;
    this.response_statusText = response.statusText;
    this.response_headers = response.headers;
    this.response_type = response.type;
  }
}

function check_response(message, pcode, response: Response) {
  if (!response.ok) {
    throw new FetchResponseError(message, pcode, response);
  }
}

export const login = async ({ email, password }: LoginInputData) => {
  if (!(email.length > 0) || !(password.length > 0)) {
    console.log("Email or password was not provided, (3295c26d)");
    throw new Error("Email or password was not provided");
  }

  const formData = new FormData();
  // OAuth2 expects form data, not JSON data
  formData.append("username", email);
  formData.append("password", password);
  const request = new Request(loginUrl, {
    method: "POST",
    body: formData,
  });

  const response = await fetch(request);
  check_response("Cannot fetch login data", "(1hgf)", response);

  const data = await response.json();

  if ("access_token" in data) {
    const tokenStr: string = data["access_token"];

    localStorage.setItem("token", tokenStr);

    const token: TokenDecoded = decodeJwt(data["access_token"]);

    const userInfo: UserInfo = {
      id: token.uid,
      email: token.sub,
      is_active: token.ia === 1 ? true : false,
      is_superuser: token.isu === 1 ? true : false,
      is_verified: token.iv === 1 ? true : false,
      roles: token.prm.split(","),
      initialTeamParticipationCount: token.pc,
      initialTeamInvitationCount: token.ic,
    };
    const tokenInfo: TokenInfo = {
      downloadedAt: Date.now(),
      timeDelta: token.td,
      user: userInfo,
    };

    localStorage.setItem("tokenInfo", JSON.stringify(tokenInfo));

    const loginInfo: LoginInfo = { token: tokenStr, tokenInfo: tokenInfo };
    console.log("Logged in.");

    return loginInfo;
  }
  return null;
};

export const getTokenInfo = () => {
  const decodedTokenStr = localStorage.getItem("tokenInfo");
  const tokenInfo: TokenInfo | null = decodedTokenStr
    ? JSON.parse(decodedTokenStr)
    : null;
  return tokenInfo;
};

export const logout = async () => {
  localStorage.removeItem("token");

  localStorage.removeItem("tokenInfo");
  // axios.defaults.headers.common['Authorization'] = "";
  console.log("Logged out.");
  // window.location.href = '/login';
};

//
/**
 * Sign up via backend and store JSON web token on success
 *
 * @param email
 * @param password
 * @returns JSON data containing access token on success
 * @throws Error on http errors or failed attempts
 */
export const signUp = async (userInfo: UserInput): Promise<UserOut> => {
  // Assert email or password or password confirmation is not empty
  const { email, password, passwordConfirmation } = userInfo;

  if (!(password === passwordConfirmation)) {
    throw new Error("Passwords do not match.");
  }

  const formData = new FormData();
  // OAuth2 expects form data, not JSON data
  formData.append("username", email);
  formData.append("password", password);

  const request = new Request(registerUrl, {
    method: "POST",
    body: formData,
  });

  const response: Response = await fetch(request);
  check_response("Cannot fetch signup data", "(vhgf)", response);

  const data = await response.json();

  return data;
};

export const forgotPassword = async ({ email }: { email: string }) => {
  const apiData = {
    email: email,
  };

  const response = await axios.post(passwordResetRequestUrl, apiData);
  const data = response;
  // const data = await response;

  return data;
};

export const forgotPasswordConfirm = async ({
  code,
  newPassword,
}: {
  code: string;
  newPassword: string;
}) => {
  const apiData = {
    password: newPassword,
    hash: code,
  };

  const response = await axios.post(passwordResetUrl, apiData);

  // const data = await response;
  const data = response;

  return data;
};
