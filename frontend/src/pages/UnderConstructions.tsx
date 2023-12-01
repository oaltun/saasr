import Button from "@mui/material/Button";
import { useTranslation } from "react-i18next";
import { Link as RouterLink } from "react-router-dom";
import Result from "../core/components/Result";
import { ReactComponent as ConstructionsSvg } from "../core/assets/constructions.svg";
// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
const UnderConstructions = () => {
  const { t } = useTranslation();

  return (
    <Result
      extra={
        <Button
          color="secondary"
          component={RouterLink}
          to={`/${process.env.PUBLIC_URL}/login`}
          variant="contained"
        >
          {t("common.backHome")}
        </Button>
      }
      image={<ConstructionsSvg />}
      maxWidth="sm"
      subTitle={t("common.errors.underConstructions.subTitle")}
      title={t("common.errors.underConstructions.title")}
    />
  );
};

export default UnderConstructions;
