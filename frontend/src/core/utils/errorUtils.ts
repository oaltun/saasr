import { AxiosError } from "axios";
import { ErrorMessage } from "formik";
import { SnackbarContextInterface } from "../contexts/SnackbarProvider";
import {
  ErrorDetail,
  HTTPValidationError,
  ValidationErrorLocItem,
} from "../../saasrapi";

export const extractHTTPValidationErrorData = (
  error: AxiosError<HTTPValidationError>
) => {
  try {
    if (!error.isAxiosError) throw new Error("Not an Axios error");
    if (!error.response) throw new Error("No error response");
    if (!error.response.data.detail)
      throw new Error("No error response data detail");
    if (!error.response.data.detail[0])
      throw new Error("Error response data detail is empty");
    if (!error.response.data.detail[0]?.msg)
      throw new Error("Error response data detail first item has no message");
    const msg = error.response.data.detail[0]?.msg ?? "";
    const msgU = msg.charAt(0).toUpperCase() + msg.slice(1);

    return {
      titleStr: "Data is not valid.",
      detailStr: msgU,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export type FrontendErrorMessage = {
  type: string;
  titleStr: string;
  detailStr: string;
};

export const extractTheHTTPExceptionData = (error: AxiosError<any>) => {
  try {
    if (!error.isAxiosError) throw new Error("Not an Axios error");
    if (!error.response) throw new Error("No error response");
    if (!error.response.data.detail)
      throw new Error("No error response data detail");

    if (typeof error.response.data.detail === "string")
      return error.response.data.detail;

    if (!error.response.data.detail.error_english)
      throw new Error("No error code in detail");
    if (!error.response.data.detail.error_code)
      throw new Error("No error code in detail");

    if (error.response.data.detail.error_code)
      console.log(
        "(234edd) Error code: " + error.response.data.detail.error_code
      );

    return {
      titleStr: error.response.data.detail.error_english,
      detailStr: error.message,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export const extractJSONResponseWithErrorDetailData = (
  error: AxiosError<ErrorDetail>
) => {
  try {
    if (!error.isAxiosError) throw new Error("Not an Axios error");
    if (!error.response) throw new Error("No error response");
    if (!error.response.data.is_error_detail)
      throw new Error("Not an error detail");

    return {
      titleStr: error.response.data.error_english,
      detailStr: error.message,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export const extractErrorDetailData = (error: ErrorDetail) => {
  try {
    if (!error.is_error_detail) throw new Error("Not an ErrorDetail object.");

    return {
      titleStr: "",
      detailStr: error.error_english,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export const extractErrorData = (error: Error) => {
  try {
    if (!(error instanceof Error))
      throw new Error("This error is not of type Error.");

    if (error.message === "Failed to fetch" && error.name === "TypeError") {
      return {
        titleStr: "Error: Failed to fetch data.",
        detailStr:
          "Failed to fetch data from server. Please check your internet connection.",
      } as FrontendErrorMessage;
    }

    if (error.name === "ChunkLoadError") {
      return {
        titleStr: "Error: " + error.message,
        detailStr:
          "Failed to load data from server. Please check your internet connection.",
      } as FrontendErrorMessage;
    }

    return {
      titleStr: "Error: " + error.message,
      detailStr: "Error name: " + error.name,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export const extractStringData = (error: string) => {
  try {
    if (typeof error !== "string") throw new Error("Not a string");

    return {
      titleStr: "Error",
      detailStr: error,
    } as FrontendErrorMessage;
  } catch (e: any) {}
};

export class ErrorHandler {
  static handle = (
    snackbar: SnackbarContextInterface | undefined,
    error: AxiosError<ErrorDetail> | string | ErrorDetail | Error | any,
    pcode: string = ""
  ) => {
    console.log("JSON.stringify:" + JSON.stringify(error));
    console.log("Above is JSON.stringify() of an error. We can also extract:");
    console.log([
      "pcode",
      pcode,
      "constructor",
      error.constructor.toString(),
      "cause",
      error.cause,
      "status_code",
      error.status_code,
      "message",
      error.message,
      "is error detail",
      error.response?.data.is_error_detail,
      "response.data",
      error.response?.data,
    ]);

    if (typeof error === "string") {
      const frontendEM: FrontendErrorMessage = {
        titleStr: error,
        detailStr: "",
        type: "",
      };
      if (snackbar) snackbar.error(frontendEM);

      return frontendEM;
    }

    //-------------------------------//
    // Set error type from constructor
    //-------------------------------//
    const eTypeStr = error.constructor.toString();
    const funDec = eTypeStr.split("()")[0];
    const eType = funDec.split(" ")[1];

    //-------------------------------//
    // Most errors have a message
    //-------------------------------//

    const eTitle = error.message ?? "";

    //-------------------------------//
    // Add some details
    //-------------------------------//
    let eDetails = "";
    if (error.name) eDetails += "Name:" + error.name;

    // Add error detail info in axios
    const errorA = error as AxiosError<ErrorDetail>;
    const hasED = error.response?.data.is_error_detail ? true : false;
    if (hasED) {
      eDetails += "English: " + errorA.response?.data.error_english ?? "";
      eDetails += "Code: " + errorA.response?.data.error_code ?? "";
    }

    // Add network error detail
    if (
      error.message === "Network Error" ||
      error.message === "Failed to fetch"
    ) {
      eDetails = "Please retry. " + eDetails;
    }

    //-------------------------------//
    // Construct object to return
    //-------------------------------//
    const frontendEM: FrontendErrorMessage = {
      titleStr: eTitle,
      detailStr: eDetails,
      type: eType,
    };

    //-------------------------------//
    // Show error to the user
    //-------------------------------//
    if (snackbar) snackbar.error(frontendEM);

    //-------------------------------//
    // return
    //-------------------------------//
    return frontendEM;
  };
}
