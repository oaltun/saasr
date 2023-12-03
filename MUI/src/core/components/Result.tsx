import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import React from "react";
import { ReactComponent as ErrorSvg } from "../assets/error.svg";
import { ReactComponent as SuccessSvg } from "../assets/success.svg";
import SvgContainer from "./SvgContainer";

type ResultImageProps = {
  customImage?: React.ReactNode;
  status?: "error" | "success";
};

const ResultImage = ({ customImage, status }: ResultImageProps) => {
  let image = customImage;

  if (!image) {
    if (status === "error") {
      image = <ErrorSvg />;
    } else if (status === "success") {
      image = <SuccessSvg />;
    }
  }

  return image ? <Box marginBottom={3}>{image}</Box> : null;
};

type ResultProps = {
  extra?: React.ReactNode;
  image?: React.ReactNode;
  maxWidth?: "xs" | "sm";
  status?: "error" | "success";
  subTitle?: string;
  title: string;
};

const Result = ({
  extra,
  image,
  maxWidth = "xs",
  status,
  subTitle,
  title,
}: ResultProps) => {
  return (
    <Container maxWidth={maxWidth}>
      <Box sx={{ textAlign: "center", px: 3, py: 8 }}>
        <SvgContainer>
          <ResultImage customImage={image} status={status} />
        </SvgContainer>
        <Typography gutterBottom variant="h5">
          {title}
        </Typography>
        {subTitle && <Typography variant="body2">{subTitle}</Typography>}
        {extra && <Box sx={{ mt: 4, textAlign: "center" }}>{extra}</Box>}
      </Box>
    </Container>
  );
};

export default Result;
