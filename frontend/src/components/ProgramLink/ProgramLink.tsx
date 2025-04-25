import { Link } from "react-router-dom";
import { Link as MuiLink } from "@mui/material";
import { GridRenderCellParams } from "@mui/x-data-grid";

type ProgramLinkProps = {params: GridRenderCellParams, endpoint: string}

export function ProgramLink({params, endpoint}:ProgramLinkProps) {
    return (
        <MuiLink component={Link} to={`${endpoint}/${params.row.ProgramName}?programId=${[params.row.id]}`}>
            {params.row.ProgramName}
        </MuiLink>
    );
}

